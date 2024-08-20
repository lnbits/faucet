Vue.component(VueQrcode.name, VueQrcode)
new Vue({
  el: '#vue',
  mixins: [windowMixin],
  data: () => ({
    headline: 'Scan the QR code to get free satoshis',
    faucet: faucet_data,
    countdown: '00:00:00',
    countdownTimer: null
  }),
  computed: {
    title: function () {
      return `${this.faucet.title} (${this.faucet.current_use} / ${this.faucet.uses})`
    },
    qrLink: function () {
      return `${window.location.origin}?lightning:${this.faucet.lnurl}`
    },
    qrValue: function () {
      return `lightning:${this.faucet.lnurl}`
    }
  },
  methods: {
    initWs: async function () {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const url = `${protocol}://${window.location.host}/faucet/${this.faucet.id}/ws`
      this.ws = new WebSocket(url)
      this.ws.addEventListener('message', async ({data}) => {
        const res = JSON.parse(data.toString())
        console.log(res)
        this.faucet.current_use = res.current_use
        this.faucet.lnurl = res.lnurl
        this.faucet.next_tick = res.next_tick
      })
      this.ws.addEventListener('close', async () => {
        this.$q.notify({
          type: 'negative',
          message: 'WebSocket connection closed. Retrying...',
          timeout: 1000
        })
        setTimeout(() => {
          this.initWs()
        }, 3000)
      })
    },
    formatDateTime: function (val) {
      return new Date(val).toLocaleString()
    },
    hasEnded: function () {
      return new Date(this.faucet.end_time).getTime() <= new Date().getTime()
    },
    hasStarted: function () {
      return new Date(this.faucet.start_time).getTime() <= new Date().getTime()
    },
    isRunning: function () {
      return this.hasStarted() && !this.hasEnded()
    },
    startCountdown: function () {
      if (this.countdownTimer) clearInterval(this.countdownTimer)
      this.countdownTimer = setInterval(() => {
        const now = new Date().getTime()
        const nextTick = new Date(this.faucet.next_tick).getTime()
        const distance = nextTick - now
        if (distance < 0) {
          clearInterval(this.countdownTimer)
          this.countdown = '00:00:00'
        } else {
          const hours = Math.floor(
            (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
          )
          const minutes = Math.floor(
            (distance % (1000 * 60 * 60)) / (1000 * 60)
          )
          const seconds = Math.floor((distance % (1000 * 60)) / 1000)
          this.countdown = `${hours}:${minutes}:${seconds}`
        }
      }, 1000)
    }
  },
  created: function () {
    this.initWs()
    if (isRunning()) {
      this.startCountdown()
    }
  }
})
