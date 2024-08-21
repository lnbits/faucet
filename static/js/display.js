Vue.component(VueQrcode.name, VueQrcode)
new Vue({
  el: '#vue',
  mixins: [windowMixin],
  data: () => ({
    headline: 'Scan the QR code to get free satoshis',
    faucet: faucet_data,
    countdown: { days: 0, hours: 0, minutes: 0, seconds: 0 },
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
        console.log("ws message:", res)
        this.faucet.current_use = res.current_use
        this.faucet.current_k1 = res.current_k1
        this.faucet.lnurl = res.lnurl
        this.faucet.next_tick = res.next_tick
        this.startCountdown()
        if (res.lnurl === null) {
            this.$q.notify({
                type: 'positive',
                message: 'Faucet was drained!!!',
                timeout: 3000
            })
        }
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
    calculateCountdown: function () {
        const now = new Date().getTime()
        const nextTick = new Date(this.faucet.next_tick).getTime()
        const distance = nextTick - now
        if (distance < 0) {
            return { days: 0, hours: 0, minutes: 0, seconds: 0 }
        } else {
            const days = Math.floor(distance / (1000 * 60 * 60 * 24))
            const hours = Math.floor(
            (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
            )
            const minutes = Math.floor(
            (distance % (1000 * 60 * 60)) / (1000 * 60)
            )
            const seconds = Math.floor((distance % (1000 * 60)) / 1000)
            return { days: days, hours: hours, minutes: minutes, seconds: seconds }
        }
    },
    startCountdown: function () {
      if (this.countdownTimer) clearInterval(this.countdownTimer)
      this.countdown = this.calculateCountdown()
      this.countdownTimer = setInterval(() => {
          this.countdown = this.calculateCountdown()
      }, 1000)
    }
  },
  created: function () {
    this.initWs()
    console.log(this.faucet)
    if (!this.hasEnded()) {
      this.countdown = this.calculateCountdown()
      this.startCountdown()
    }
  }
})
