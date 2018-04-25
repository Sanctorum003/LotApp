const app = getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    
  },

  onShow:function()
  {
    this.setData({ wallet: app.globalData.myYuan })
  },

  recharge:function(){
    
    console.log("点击充值")
    wx.navigateTo({
      url: '../deposit/deposit',
    })
  }

})