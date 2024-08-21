new Vue({
  el: '#vue',
  mixins: [windowMixin],
  data: () => {
    return {
      faucets: [],
      faucetsTable: {
        columns: [
          {name: 'title', align: 'left', label: 'Title', field: 'title'},
          {
            name: 'wallet',
            label: 'Wallet',
            field: 'wallet',
            format: function (val, _row) {
              return _.findWhere(user.wallets, {id: val}).name
            }
          },
          {
            name: 'start_time',
            label: 'Start Time',
            field: 'start_time',
            sortable: true,
            format: function (val, _row) {
              return new Date(val).toLocaleString()
            }
          },
          {
            name: 'end_time',
            label: 'End Time',
            field: 'end_time',
            format: function (val, _row) {
              return new Date(val).toLocaleString()
            }
          },
          {
            name: 'next_tick',
            label: 'Next Tick',
            field: 'next_tick',
            format: function (val, _row) {
              return new Date(val).toLocaleString()
            }
          },
          {
            name: 'interval',
            label: 'Interval',
            field: 'interval'
          },
          {
            name: 'uses',
            label: 'Uses',
            field: 'uses'
          },
          {
            name: 'current_use',
            label: 'Current Use',
            field: 'current_use'
          },
          {
            name: 'withdrawable',
            label: 'Withdrawable',
            field: 'withdrawable'
          }
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
            name: 'end_time',
            label: 'End Time',
            required: true
          },
          {
            type: 'number',
            name: 'interval',
            label: 'Interval',
            required: true
          },
          {
            type: 'number',
            name: 'uses',
            label: 'Uses',
            required: true
          },
          {
            type: 'number',
            name: 'withdrawable',
            label: 'Withdrawable per tick, 0 means (wallet balance / uses)',
            required: true
          },
          {
            type: 'hidden',
            name: 'faucet_id'
          }
        ],
        data: {}
      }
    }
  },
  methods: {
    getFaucets: function () {
      LNbits.api
        .request('GET', `/faucet/api/v1`, this.g.user.wallets[0].adminkey)
        .then(response => {
          this.faucets = response.data
        })
        .catch(error => {
          LNbits.utils.notifyApiError(error)
        })
    },
    sendFormData: function () {
      const faucet_id = this.createFaucetDialog.data.faucet_id
      let data = this.createFaucetDialog.data
      // TODO: remove hack, issue with dynamic fields component
      if (faucet_id !== undefined) {
        data.id = faucet_id
        this.updateFaucet(data)
      } else {
        data.wallet = data.wallet.value
        this.createFaucet(data)
      }
    },
    openCreateDialog: function () {
      this.createFaucetDialog.data = {}
      this.createFaucetDialog.show = true
    },
    openUpdateDialog: function (faucet_id) {
      this.createFaucetDialog.data = _.findWhere(this.faucets, {id: faucet_id})
      this.createFaucetDialog.data.faucet_id = faucet_id
      this.createFaucetDialog.show = true
    },
    updateFaucet: function () {
      const data = this.createFaucetDialog.data
      LNbits.api
        .request(
          'PUT',
          `/faucet/api/v1/${data.id}`,
          user.wallets[0].adminkey,
          data
        )
        .then(response => {
          this.faucets = _.reject(this.faucets, function (obj) {
            return obj.id === data.id
          })
          this.faucets.push(response.data)
          this.createFaucetDialog.show = false
        })
        .catch(error => {
          LNbits.utils.notifyApiError(error)
        })
    },
    createFaucet: function () {
      const data = this.createFaucetDialog.data
      LNbits.api
        .request('POST', '/faucet/api/v1', user.wallets[0].adminkey, data)
        .then(response => {
          this.faucets.push(response.data)
          this.createFaucetDialog.show = false
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    deleteFaucet: function (faucetId) {
      LNbits.utils
        .confirmDialog('Are you sure you want to delete this faucet?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              `/faucet/api/v1/${faucetId}`,
              user.wallets[0].adminkey
            )
            .then(() => {
              this.faucets = _.reject(this.faucets, function (obj) {
                return obj.id === faucetId
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
