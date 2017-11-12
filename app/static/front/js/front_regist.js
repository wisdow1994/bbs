$(function () {
   $('#send-captcha-btn').click(function (event) {
       event.preventDefault();
       var self = $(this);
       // 获取邮箱
       var email = $('input[real_name=email]').val();

       if(!email){
           xtalert.alertInfoToast('请填写邮箱！');
           return;
       }
       xtajax.get({
           'url': '/send_token',
           'data': {
               'email': email
           },
           'success': function (data) {
               if(data['code'] == 200){
                   xtalert.alertSuccessToast('验证码已发送，请注意查收！');
                   var timeCount = 300;
                   self.attr('disabled','disabled');
                    self.css('cursor','default');
                   var timer = setInterval(function () {
                       self.text(timeCount);
                       timeCount--;
                       if(timeCount <= 0){
                           self.text('发送验证码');
                           self.removeAttr('disabled');
                           clearInterval(timer);
                           self.css('cursor','pointer');
                       }
                   },1000);
               }else{
                   xtalert.alertInfoToast(data['message']);
               }
           }
       });
   });
});

$(function () {
    var btn = $('#graph-captcha-btn');
    btn.css('cursor','pointer');
    btn.click(function (event) {
        event.preventDefault();
        var imgTag = $(this).children('img');
        var oldSrc = imgTag.attr('src');
        var newSrc = oldSrc + '?xx=' + Math.random();
        imgTag.attr('src',newSrc);
    });
});
