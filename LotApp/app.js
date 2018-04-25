//app.js
const app = getApp()
App({
  onLaunch: function () { 
    var thisPage = this
    // 展示本地存储能力
    var logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)
    var socketMsgQueue = []

    // 登录
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
        socketMsgQueue.push(JSON.stringify(res))////转换成JSON形式发送)

      }
    })

    // 获取用户信息
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.userInfo']) {
          // 已经授权，可以直接调用 getUserInfo 获取头像昵称，不会弹框
          wx.getUserInfo({
            success: res => {
              // 可以将 res 发送给后台解码出 unionId
              this.globalData.userInfo = res.userInfo
              // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
              // 所以此处加入 callback 以防止这种情况
              if (this.userInfoReadyCallback) {
                this.userInfoReadyCallback(res)
              }

              //发送用户原始加密信息给服务器
              socketMsgQueue.push(JSON.stringify(res))//转换成JSON形式发送
              thisPage.connectToServe(socketMsgQueue) 
            }
          })
        }
      }
    })

  },
  connectToServe: function (socketMsgQueue)
    {
     var thisPage = this
    //连接远端服务器
    wx.connectSocket({
      url: 'ws://47.100.116.81:9999',
       success: function (res) {
         console.log("找到目标服务器")
         thisPage.sendUserInfo(socketMsgQueue)//连接成功，传送数据
       },
       fail: function (res) {
         console.log("未找到目标服务器，尝试重新寻找")
         console.log(res)
       }
    })
  },

  sendUserInfo: function (socketMsgQueue) {//发送用户信息
    var thisPage = this
    wx.onSocketOpen(function (res) {
      console.log("WebSocket 已打开！")
      thisPage.globalData.socketOpen = true
      for (var i = 0; i < socketMsgQueue.length; i++) {
        thisPage.sendSocketMessage(socketMsgQueue[i])
      }
      thisPage.globalData.socketMsgQueue = []
    })
    wx.onSocketError(function (res) {
      console.log('WebSocket连接打开失败，请检查！')
      console.log(res)
    })
  },
  sendSocketMessage: function(msg) {
    var thisPage = this
    //console.log(msg)
    if (thisPage.globalData.socketOpen) {
     wx.sendSocketMessage({
        data: msg,
        success: function (res) {
          console.log("发送信息成功")
        },
        fail: function(res) {
          console.log("发送信息失败")
          console.log(res)
        }
      })
    }
  },

  globalData: {
    userInfo: null,
    socketMsgQueue: [],
    socketOpen:false,
    myCost:0,//停车花费
    myYuan:0,//余额信息
    carID: null,//车位信息 【别忘记重进时，对于头部的解析】
    serUserInfo:null,//服务器发回用户信息
    displayTime:0,//停车时间
    isParkStart:false,//是否开始停车
    errMsg:0,//错误信息
    isScanQR:false,//互斥访问二维码
    histOrder:null,//发回的历史订单信息
    isAdmin:false,//是否为管理员
  }
})