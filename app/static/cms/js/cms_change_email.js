$(function () {
   $('#token-btn').click(function (event) {
       event.preventDefault();

       var email = $('input[name=email]').val();

       xtajax.get({
           'url': '/send_token',
           //用来发送邮箱验证码的视图函数
           'data': {
               'email': email
           },
           'success': function (data) {
               if(data['code'] == 200){
                   xtalert.alertSuccessToast('邮箱已经发送给你！');
               }else{
                   xtalert.alertInfoToast(data['message']);
               }
           },
           'fail': function (error) {
               xtalert.alertNetworkError();
           }
       })
   });
});

$(function () {
   $('#submit').click(function (event) {
       event.preventDefault();

       var emailInput = $('input[name=email]');
       var tokenInput = $('input[name=token]');

       xtajax.post({
           'url': '/change_email',
           'data':{
               'email': emailInput.val(),
               'token': tokenInput.val()
           },
           'success': function (data) {
               if(data['code'] == 200){
                   emailInput.val('');
                   tokenInput.val('');
                   xtalert.alertSuccessToast('恭喜！邮箱修改成功！');
               }else{
                   xtalert.alertInfoToast(data['message']);
               }
           },
           'fail': function (error) {
               xtajax.alertNetworkError();
           }
       })
   });
});
