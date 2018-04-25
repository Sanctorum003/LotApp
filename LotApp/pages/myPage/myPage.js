/**
 * 个人信息页面
 * 
 */

const app = getApp()
Page({
  data: {
    isAdmin:false //是否为管理员
  },
  onLoad() {
    this.setData({ isAdmin: app.globalData.isAdmin })
  },
  onShow() {
    this.getUserInfo();
  },
  getUserInfo: function (cb) {
    var that = this
    wx.login({
      success: function () {
        wx.getUserInfo({
          success: function (res) {
            that.setData({
              userInfo: res.userInfo
            });
          }
        })
      }
    })
  },
  askOrder:function(){
    wx.sendSocketMessage({
      data: "askOrder:",
      success: function (res) {
        wx.navigateTo({
          url: '../order-list/index',
        })
      },
      fail: function (res) {
        console.log("请求历史订单失败")
        wx.showToast({
          title: '请求订单失败',
          image: '../../images/error.png',
          duration: 2000
        })
        app.globalData.carID = null
      }
    })
  },
  switchToLotInfo:function()
  {
    if (app.globalData.carID == null) {
      console.error(app.globalData.carID)
      console.error(app.globalData.errMsg)
      wx.showToast({
        title: '无车位信息',
        image: '../../images/error.png',
        duration: 2000
      })
    }
    else
    {
      wx.navigateTo({
        url: '../timer/timer',
      })
    }
  },
  switchToAdmin:function()
  {

  }
})