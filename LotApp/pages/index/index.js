/**
 * 许多主要逻辑
 * 可能bug1：手机真机操作时，返回carID与本地carID不一致事可能无法跳转。【移到OnReady】-【完成成功】
 */

//index.js
//获取应用实例
var app = getApp()

Page({
  data: {
    id: 0,
    latitude: '28.714621',
    longitude: '115.82749',
    scale: 15,   //缩放级别
    marks: [{
      id: 0,
      title: "去这里",
      iconPath: "../images/marker.png",
      latitude: 28.714621,
      longitude: 115.82749,
      width: 45,
      height: 50
    }],
    covers: [{                              //车位标记点
      latitude: 33.3837676883,
      longitude: 120.1983797550,
    }, {
      latitude: 33.3799512330,
      longitude: 120.2032613754,
    }, {
      latitude: 33.3783744326,
      longitude: 120.1988089085,
    }, {
      latitude: 33.3799064379,
      longitude: 120.1975536346,
    }, {
      latitude: 33.3822984624,
      longitude: 120.2026069164,
    }]
  },
  bindregionchange: function (e) {             //经纬度发生变化时会触发此事件
    if (e.type == "begin") {
      console.log("begin");
    } else if (e.type == "end") {
      console.log("end");
    }
  },

  bindcontroltap: function (e) {              //点击控件时会触发此事件
    // 点击事件选项
    switch (e.controlId) {
      // 当点击图标location.png的图标，则触发事件movetoPositioon()
      case 1: this.movetoPosition();
        break;
      // 当点击图标use.png的图标，则触发事件scanCode.png()
      case 2: wx.scanCode({                                 //扫码
        success: (res) => {
          var result = res.result;
          app.globalData.carID = result;             //记录扫码内容
          console.log(app.globalData.carID);
          
          //发送车位信息
          var that = this
          wx.sendSocketMessage({
            data: "carID:" + app.globalData.carID,
            success: function (res) {
              app.globalData.isScanQR = true
              console.log("发送车位信息")
              console.log(app.globalData.carID)
            },
            fail: function (res) {
              app.globalData.carID = null
              console.log("发送车位信息失败")
              wx.showToast({
                title: '请求失败',
                image: '../../images/error.png',
                duration: 2000
              })
              app.globalData.carID= null
            }
          })
        }
      });
        break;
      case 4: this.bindtaps();                             //开启导航功能
        break;
    }
  },
  movetoPosition: function () {                                //移动到地图中心
    this.mapCtx.moveToLocation();
  },

  bindtaps: function () {                                    //打开导航功能
    wx.getLocation({
      type: 'gcj02',
      success: function (res) {
        wx.openLocation({
          latitude: res.latitude,
          longitude: res.longitude,
          name: '我的位置',
          scale: 15,
        })
      }
    })
  },

  onShareAppMessage: function (res) {                 //分享功能
    if (res.from === 'button') {
      console.log(res.target)
    }
    return {
      title: '我的停车位',
      path: '/page/user?id=123',
      success: function (res) {
        console.log("分享成功");
      },
      fail: function (res) {
        console.log("分享失败");
      }
    }
  },
  //事件处理函数
  onLoad: function () {                 //页面加载时触发
    console.log('onLoad')
    //调用应用实例的方法获取全局数据
    wx.getLocation({
      type: 'gcj02',
      successs: (res) => {
        console.log(res);
        this.setData({
          longitude: res.longitude,
          latitude: res.latitude,
          marks: [{
            latitude: res.latitude,
            longitude: res.longitude,
          }]
        })
      }
    }),
      wx.getSystemInfo({                //控件信息
        success: (res) => {
          this.setData({
            controls: [{
              id: 1,
              iconPath: '/images/place.png',
              position: {
                left: 20,
                top: res.windowHeight - 120,
                width: 30,
                height: 30
              },
              clickable: true
            },
            {
              id: 2,
              iconPath: '/images/scan.png',
              position: {
                left: res.windowWidth / 2 - 30,
                top: res.windowHeight - 140,
                width: 60,
                height: 60
              },
              clickable: true
            },
            {
              id: 3,
              iconPath: '/images/ballpink.png',
              position: {
                left: res.windowWidth / 2 - 20,
                top: res.windowHeight / 2 - 70,
                width: 40,
                height: 60
              },
              clickable: false
            },
            {
              id: 4,
              iconPath: '/images/guide.png',
              position: {
                left: 15,
                top: res.windowHeight - 180,
                width: 40,
                height: 40
              },
              clickable: true
            },
            ]
          })
        }
      })
  },
  onShow:function(){
    this.mapCtx = wx.createMapContext("Map");
    this.movetoPosition();
    wx.onSocketMessage(function (res) {
      //监听服务器返回信息
      var tmp = JSON.parse(res.data)
      console.warn(tmp)
      if (tmp.header == "user_Info") {
        app.globalData.serUserInfo = JSON.parse(res.data)//解析JSON
        app.globalData.myYuan = app.globalData.serUserInfo.balance//同步钱包金额
        app.globalData.carID = app.globalData.serUserInfo.carID//同步carID信息
        //app.globalData.isAdmin = app.globalData.serUserInfo.isAdmin // 检查是否为管理员
        if (app.globalData.serUserInfo.openId = "oUkv30GoL4y0lj6jUBNRK3AzJ-Yc")
        {
          app.globalData.isAdmin = false
        }
        if (app.globalData.serUserInfo.last_time >= 0) {
          app.globalData.isParkStart = true;//同步是否开始停车
          app.globalData.displayTime = app.globalData.serUserInfo.last_time;//同步持续时间
          wx.navigateTo({//转跳到计时器
            url: '../timer/timer'
          })
        }
      }
      else if (tmp.header == "balance") {
        app.globalData.myYuan = tmp.balance//充值后同步钱包金额
      }
      else if (tmp.header == "carID") {
        // console.warn(app.globalData.carID)
        //-1 车位被占
        //-2 余额不足
        if (tmp.carID == -1) {//对扫描结果进行比对，如果一致，表示可以停车，否则不能停车于此处   
          app.globalData.errMsg = -1 //错误信息
          app.globalData.carID = null//清空carID信息
          wx.showToast({//显示错误信息
            title: '车位被占',
            image: '../../images/error.png',
            duration: 2000
          })
        }
        else if (tmp.carID == -2) {
          app.globalData.errMsg = -2 //错误信息
          app.globalData.carID = null//清空carID信息
          wx.showToast({//显示错误信息
            title: '余额不足',
            image: '../../images/error.png',
            duration: 2000
          })
        }
        else
        {
          app.globalData.errMsg = 0;
          wx.navigateTo({
            url: '../timer/timer',
          })
        }
      }
      else if (tmp.header == "timer_start") {
        app.globalData.isParkStart = true;
        wx.redirectTo({
          url: '../timer/timer'
        })
        //time
      }
      else if (tmp.header == "timer_stop") {
        app.globalData.myYuan = tmp.balance
        app.globalData.myCost = tmp.cost
        app.globalData.displayTime = tmp.last_time
        app.globalData.isParkStart = false
        app.globalData.carID = null
        wx.redirectTo({
          url: '../cost/cost'
        })
      }
      else if (tmp.header == "last_time") {
        app.globalData.displayTime = tmp.last_time
      }
      else if (tmp.header == "his_order")//头部信息为历史订单
      {
        app.globalData.histOrder = tmp;
      }
    })
    wx.onSocketClose(function (res) {
      console.log('WebSocket 已关闭！')
      app.onLaunch()//断线重连
    })
  }
})
