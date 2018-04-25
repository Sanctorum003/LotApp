# 2018.3.6
1. app.js 
> 108:  isAdmin:false,//是否为管理员  

2. index.js
> 204:  app.globalData.isAdmin = app.globalData.serUserInfo.isAdmin // 检查是否为管理员  

3. myPage.js
> 9:    isAdmin:false //是否为管理员  
> 12:   this.setData({ isAdmin: app.globalData.isAdmin })

4. myPage.wxml
> 16:    <view class="my-item" wx:if="{{isAdmin}}" >