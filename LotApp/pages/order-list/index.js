const app = getApp()
Page({
  data: {
    locHistOrder:null, //历史订单信息
    locHistOrderStartTime: [],//历史订单开始时间
    locHistOrderStopTime: [], //历史订单结束时间
    locHistOrderLastTime: [],//历史订单持续时间
    locHistOrderCost: [], //历史订单花费
    orderLen : 0
  },
  onLoad() {

  },
  onReady()
  {
    var that = this;
    this.setData({ locHistOrder: app.globalData.histOrder })
    this.setData({ orderLen: app.globalData.histOrder.len })
    var pHistOrderStartTime=[]//历史订单开始时间
    var pHistOrderStopTime= [] //历史订单结束时间
    var pHistOrderLastTime = []//历史订单持续时间
    var pHistOrderCost= []//历史订单花费    
    var len = app.globalData.histOrder.len
    console.warn("OpenHistory")
    for (var i = 1; i <= len; i++) {
      pHistOrderStartTime.push(app.globalData.histOrder[i].start_time)
      pHistOrderStopTime.push(app.globalData.histOrder[i].stop_time)
      pHistOrderLastTime.push(app.globalData.histOrder[i].cost)
      pHistOrderCost.push(app.globalData.histOrder[i].last_time)
    }
    console.warn(pHistOrderStartTime)
    this.setData({ locHistOrderStartTime: pHistOrderStartTime })
    this.setData({ locHistOrderStopTime: pHistOrderStopTime })
    this.setData({ locHistOrderLastTime: pHistOrderLastTime })
    this.setData({ locHistOrderCost: pHistOrderCost })
    
  },
  onShow(){
  }
})