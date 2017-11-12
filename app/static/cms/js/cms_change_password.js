$(function () {
    $('#submit').click(function (event) {
        event.preventDefault();
        //禁用按钮的默认提交行为,改用ajax的post提交数据
        var old_passwordInput = $('input[name=old_password]');
        var passwordInput = $('input[name=password]');
        var password2Input = $('input[name=password2]');

        var old_password = old_passwordInput.val();
        var password = passwordInput.val();
        var password2 = password2Input.val();
        xtajax.ajax({
            'url': '/change-password',
            'type':'POST',
            'data': {
                'old_password': old_password,
                'password': password,
                'password2': password2
            },
            'success':function (data) {
                var code = data['code'];
                if (code == 200){
                    old_passwordInput.val('');
                    passwordInput.val('');
                    password2Input.val('');
                    xtalert.alertSuccessToast('密码修改成功!');
                }else{
                    xtalert.alertInfoToast(message);
                }
            },
            'fail': function (error) {
                xtalert.alertNetworkError();
            }
        });
    });
});
