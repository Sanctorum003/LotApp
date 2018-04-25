/**
 * 充值
 * 维护全局变量{{myYuan}}
 */

const app = getApp()
Page({
  data:{
    currentMoney: 10,
    moneyArr:[
      {
        content:"10元",
        color: "#FFFFFF",
        background: "#34B5E3",
        id: 10,
        top: "150rpx",
        left: "40rpx",
      },
      {
        content:"20元",
        color: "#34B5E3",
        background: "#FFFFFF",
        id: 20,
        top: "150rpx",
        left: "395rpx",
      },
      {
        content:"50元",
        color: "#34B5E3",
        background: "#FFFFFF",
        id: 50,
        top: "270rpx",
        left: "40rpx",
      },
      {
        content:"100元",
        color: "#34B5E3",
        background: "#FFFFFF",
        id: 100,
        top: "270rpx",
        left: "395rpx",
      }
    ],
    //记录上一次点击的充值选项的id
    lastMoneyId: 0
  },
  onLoad:function(options){
  },
  //充值协议
  chargeAgree: function() {
    console.log("点击充值协议")
    wx.navigateTo({
      url: '../recharged/recharged',
    })
  },
  //点击充值选项
  chioceAct: function(res) {
    var that = this
    console.log("点击充值选项")
    //在 button 中添加data-currentid="去充值"后，在点击返回的res中res.currentTarget.dataset.currentid中就是这个值
    console.log(res.currentTarget.dataset.currentid)
    var id = res.currentTarget.dataset.currentid
    if (id == 10) {
      //10元
      that.setData({
        "moneyArr[0].color":"#FFFFFF",
        "moneyArr[0].background":"#34B5E3",
        "moneyArr[1].color":"#34B5E3",
        "moneyArr[1].background":"#FFFFFF",
        "moneyArr[2].color":"#34B5E3",
        "moneyArr[2].background":"#FFFFFF",
        "moneyArr[3].color":"#34B5E3",
        "moneyArr[3].background":"#FFFFFF",
        "lastMoneyId": 0,
        "currentMoney": 10
      })
    }else if (id == 20){
      //20元
      that.setData({
        "moneyArr[1].color":"#FFFFFF",
        "moneyArr[1].background":"#34B5E3",
        "moneyArr[0].color":"#34B5E3",
        "moneyArr[0].background":"#FFFFFF",
        "moneyArr[2].color":"#34B5E3",
        "moneyArr[2].background":"#FFFFFF",
        "moneyArr[3].color":"#34B5E3",
        "moneyArr[3].background":"#FFFFFF",
        "lastMoneyId": 1,
        "currentMoney": 20
      })
    }else if (id == 50){
      //50元
      that.setData({
        "moneyArr[2].color":"#FFFFFF",
        "moneyArr[2].background":"#34B5E3",
        "moneyArr[1].color":"#34B5E3",
        "moneyArr[1].background":"#FFFFFF",
        "moneyArr[0].color":"#34B5E3",
        "moneyArr[0].background":"#FFFFFF",
        "moneyArr[3].color":"#34B5E3",
        "moneyArr[3].background":"#FFFFFF",
        "lastMoneyId": 2,
        "currentMoney": 50
      })
    }else if (id == 100){
      //100元
      that.setData({
        "moneyArr[3].color":"#FFFFFF",
        "moneyArr[3].background":"#34B5E3",
        "moneyArr[1].color":"#34B5E3",
        "moneyArr[1].background":"#FFFFFF",
        "moneyArr[2].color":"#34B5E3",
        "moneyArr[2].background":"#FFFFFF",
        "moneyArr[0].color":"#34B5E3",
        "moneyArr[0].background":"#FFFFFF",
        "lastMoneyId": 3,
        "currentMoney": 100
      })
    }
  },
  //点击去充值
  gotoRecharged: function(res) {
    var that = this
    console.log("去充值按钮")
    wx.sendSocketMessage({
      data: "addMoney:"+that.data.currentMoney,
      success: function (res) {
        console.log("发送信息成功")
        app.globalData.myYuan += that.data.currentMoney
        wx.showToast({
          title: '充值成功',
          image: '../../images/paySuccess.png',
          duration: 1000
        })
        console.log(app.globalData.myYuan)
        console.log(that.data.currentMoney)
      },
      fail: function (res) {
        console.log("发送信息失败")
        wx.showToast({
          title: '请求失败',
          image: '../../images/error.png',
          duration: 2000
        })
      }
    })
  }
})