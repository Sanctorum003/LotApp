var app = getApp()

Page({
  data: { 
    pay:null,
    time:0,
    wallet:null,
    hour:0,
    min:0,
    sec:0
  },
  onLoad: function (options) {
    this.setData({ pay: app.globalData.myCost, time: app.globalData.displayTime, wallet: app.globalData.myYuan })
    var myHour = parseInt(this.data.time / 3600)
    var myMin = parseInt(this.data.time / 60) % 60
    var mySec = this.data.time % 60
    console.error(myHour)
    console.error(myMin)
    console.error(mySec)
    this.setData({ hour: myHour, min: myMin,sec:mySec})
  },
  onUnload:function(){
        // app.globalData.isParkStart = false
        // app.globalData.carID = null
        // app.globalData.isFinishPark = false
  },
  finishAct:function(){
    wx.switchTab({//转跳到主页
          url: '../index/index'
    })
  }
})