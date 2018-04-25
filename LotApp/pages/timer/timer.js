/**
 * 用的轮子代码不会改，将就用吧
 * onLoad中判断是否选有carID，没有调回主页
 * 显示时间的是{{time}}对应全局{{displayTime}}
 * 利用文件：format-location.js和utils/util.js
 */

var app = getApp()

var countTooGetLocation = 0;
var total_micro_second = 0;
var starRun = 0;
var totalSecond = 0;
var oriMeters = 0.0;
/* 毫秒级倒计时 */
function count_down(that) {

  if (starRun == 0) {
    return;
  }

  if (countTooGetLocation >= 100) {
    var time = date_format(total_micro_second);
    that.updateTime(time);
  }

  if (countTooGetLocation >= 5000) { //1000为1s
    that.getLocation();
    countTooGetLocation = 0;
  }

  //setTimeout
  setTimeout(function () {
      countTooGetLocation += 10;
      total_micro_second += 10;
      count_down(that);
  }
    , 10
  )
}


// 时间格式化输出，如03:25:19 86。每10ms都会调用一次
function date_format(micro_second) {
  // 秒数
  var second = Math.floor(micro_second / 1000);
  // 小时位
  var hr = Math.floor(second / 3600);
  // 分钟位
  var min = fill_zero_prefix(Math.floor((second - hr * 3600) / 60));
  // 秒位
  var sec = fill_zero_prefix((second - hr * 3600 - min * 60));// equal to => var sec = second % 60;


  return hr + ":" + min + ":" + sec + " ";
}


function getDistance(lat1, lng1, lat2, lng2) {
  var dis = 0;
  var radLat1 = toRadians(lat1);
  var radLat2 = toRadians(lat2);
  var deltaLat = radLat1 - radLat2;
  var deltaLng = toRadians(lng1) - toRadians(lng2);
  var dis = 2 * Math.asin(Math.sqrt(Math.pow(Math.sin(deltaLat / 2), 2) + Math.cos(radLat1) * Math.cos(radLat2) * Math.pow(Math.sin(deltaLng / 2), 2)));
  return dis * 6378137;

  function toRadians(d) { return d * Math.PI / 180; }
}

function fill_zero_prefix(num) {
  return num < 10 ? "0" + num : num
}

//****************************************************************************************

Page({
  data: {
    clock: '',
    isLocation: false,
    latitude: 0,
    longitude: 0,
    markers: [],
    covers: [],
    meters: 0.00,
    time: "0:00:00",
    isParkStart:false
  },

  //****************************
  onLoad: function (options) {
    // 页面初始化 options为页面跳转所带来的参数
    this.getLocation()
    count_down(this)
    var that = this
    /*****请求当前持续时间 */
    wx.sendSocketMessage({
      data: "askTime:",
      success: function (res) {
        console.warn(res)
      },
      fail: function (res) {
        console.warn("打开'停车信息'失败")
        wx.switchTab({
          url: '../myPage/myPage',
          success: function (res) {
            wx.showToast({
              title: '无法连接网络',
              image: '../../images/error.png',
              duration: 2000
            })
          }
        })
      }
    })
    /************************* */
  },
  onReady:function()
  {
    var that =this
    this.setData({ isParkStart: app.globalData.isParkStart })
    /*******用于用户用完后，再开清零 */
    if (app.globalData.isParkStart == false) {
      that.stopRun()
      total_micro_second = 0
    }
    /************用于同步停车时间 */
    if (app.globalData.isParkStart == true) {
      console.warn(app.globalData.displayTime)
      total_micro_second = app.globalData.displayTime * 1000
      that.starRun()
    }
  },
  onShow:function(){
    // /*是否有carID没有carID不让进入该页面*/
    // if (app.globalData.errMsg == -1) {
    //   app.globalData.errMsg == 0
    //   wx.switchTab({//转跳到主页
    //     url: '../index/index'
    //   })
    //   wx.showToast({//显示错误信息
    //     title: '车位被占',
    //     image: '../../images/error.png',
    //     duration: 2000
    //   })
    // }

    // if (app.globalData.errMsg == -2) {
    //   app.globalData.carID = null//清空carID信息
    //   wx.switchTab({//转跳到主页
    //     url: '../index/index'
    //   })
    //   wx.showToast({//显示错误信息
    //     title: '余额不足',
    //     image: '../../images/error.png',
    //     duration: 2000
    //   })
    // }

    // if (app.globalData.carID == null && app.globalData.errMsg == 0) {
    //   console.error(app.globalData.carID)
    //   console.error(app.globalData.errMsg)
    //   wx.navigateBack({
    //     // url: '../index/index',
    //     delta: 1,
    //     success: function (res) {
    //       wx.showToast({
    //         title: '无车位信息',
    //         image: '../../images/error.png',
    //         duration: 2000
    //       })
    //     }
    //   })
    // }
  },
  onUnload: function (){
    this.stopRun()
  },
  //****************************
  openLocation: function () {
    wx.getLocation({
      type: 'gcj02', // 默认为 wgs84 返回 gps 坐标，gcj02 返回可用于 wx.openLocation 的坐标
      success: function (res) {
        wx.openLocation({
          latitude: res.latitude, // 纬度，范围为-90~90，负数表示南纬
          longitude: res.longitude, // 经度，范围为-180~180，负数表示西经
          scale: 28, // 缩放比例
        })
      },
    })
  },


  //****************************
  starRun: function () {
    console.warn(starRun)
    if (starRun == 1) {
      return;
    }
    starRun = 1;
    count_down(this);
    this.getLocation();
  },


  //****************************
  stopRun: function () {
    starRun = 0;
    count_down(this);
  },


  //****************************
  updateTime: function (time) {

    var data = this.data;
    data.time = time;
    this.data = data;
    this.setData({
      time: time,
    })

  },


  //****************************
  getLocation: function () {
    var that = this
    wx.getLocation({

      type: 'gcj02', // 默认为 wgs84 返回 gps 坐标，gcj02 返回可用于 wx.openLocation 的坐标
      success: function (res) {
        // console.log("res----------")
        // console.log(res)

        //make datas 
        var newCover = {
          latitude: res.latitude,
          longitude: res.longitude,
        };
        var oriCovers = that.data.covers;

        // console.log("oriMeters----------")
        // console.log(oriMeters);
        var len = oriCovers.length;
        var lastCover;
        if (len == 0) {
          oriCovers.push(newCover);
        }
        len = oriCovers.length;
        var lastCover = oriCovers[len - 1];

        // console.log("oriCovers----------")
        // console.log(oriCovers, len);

        var newMeters = getDistance(lastCover.latitude, lastCover.longitude, res.latitude, res.longitude) / 1000;

        if (newMeters < 0.0015) {
          newMeters = 0.0;
        }

        oriMeters = oriMeters + newMeters;
        // console.log("newMeters----------")
        // console.log(newMeters);


        var meters = new Number(oriMeters);
        var showMeters = meters.toFixed(2);

        oriCovers.push(newCover);

        that.setData({
          latitude: res.latitude,
          longitude: res.longitude,
          markers: [],
          covers: oriCovers,
          meters: showMeters,
        });
      },
    })
  }
})





