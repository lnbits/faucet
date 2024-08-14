new Vue({
  el: '#vue',
  mixins: [windowMixin],
  data: () => {
    return {
      faucets: [],
      faucetsTable: {
        columns: [
          {name: 'title', align: 'left', label: 'Title', field: 'title'}
        ]
      },
      createFaucetDialog: {
        show: false,
        secondMultiplier: 'seconds',
        secondMultiplierOptions: ['seconds', 'minutes', 'hours'],
        fields: [
          {
            type: 'input',
            name: 'title',
            label: 'Title',
            required: true
          },
          {
            type: 'select',
            name: 'wallet',
            label: 'Wallet',
            required: true,
            values: user.wallets.map(wallet => {
              return {label: wallet.name, value: wallet.id}
            })
          },
          {
            type: 'text',
            name: 'description',
            label: 'Description',
            required: false
          },
          {
            type: 'input',
            name: 'start_time',
            label: 'Start Time',
            required: true
          },
          {
            type: 'input',
            name: 'stop_time',
            label: 'Stop Time',
            required: true
          },
          {
            type: 'number',
            name: 'interval',
            label: 'Interval',
            required: true
          }
        ],
        data: {
          is_unique: false,
          use_custom: false,
          has_webhook: false
        }
      }
    }
  },
  methods: {
    getFaucets: function () {
      LNbits.api
        .request('GET', `/faucet/api/v1`, this.g.user.wallets[0].adminkey)
        .then(response => {
          this.faucets = response.data.data
        })
        .catch(error => {
          LNbits.utils.notifyApiError(error)
        })
    },
    sendFormData: function () {
      var wallet = _.findWhere(this.g.user.wallets, {
        id: this.createFaucetDialog.data.wallet
      })
      var data = _.omit(this.createFaucetDialog.data, 'wallet')

      if (!data.use_custom) {
        data.custom_url = null
      }

      if (data.use_custom && !data?.custom_url) {
        data.custom_url = CUSTOM_URL
      }

      data.wait_time =
        data.wait_time *
        {
          seconds: 1,
          minutes: 60,
          hours: 3600
        }[this.createFaucetDialog.secondMultiplier]

      if (data.id) {
        this.updateFaucet(wallet, data)
      } else {
        this.createFaucet(wallet, data)
      }
    },
    updateFaucet: function (wallet, data) {
      // Remove webhook info if toggle is set to false
      if (!data.has_webhook) {
        data.webhook_url = null
        data.webhook_headers = null
        data.webhook_body = null
      }

      LNbits.api
        .request('PUT', `/faucet/api/v1/${data.id}`, wallet.adminkey, data)
        .then(response => {
          this.faucets = _.reject(this.faucets, function (obj) {
            return obj.id === data.id
          })
          this.faucets.push(mapFaucet(response.data))
          this.createFaucetDialog.show = false
        })
        .catch(error => {
          LNbits.utils.notifyApiError(error)
        })
    },
    createFaucet: function (wallet, data) {
      LNbits.api
        .request('POST', '/faucet/api/v1', wallet.adminkey, data)
        .then(response => {
          this.faucets.push(response.data)
          this.createFaucetDialog.show = false
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    deleteFaucet: function (linkId) {
      var link = _.findWhere(this.faucets, {id: linkId})
      LNbits.utils
        .confirmDialog('Are you sure you want to delete this withdraw link?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              `/faucet/api/v1/${linkId}`,
              _.findWhere(this.g.user.wallets, {id: link.wallet}).adminkey
            )
            .then(() => {
              this.faucets = _.reject(this.faucets, function (obj) {
                return obj.id === linkId
              })
            })
            .catch(function (error) {
              LNbits.utils.notifyApiError(error)
            })
        })
    }
  },
  created: function () {
    this.getFaucets()
  }
})
