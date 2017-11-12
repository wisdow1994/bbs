/**
 * Created by Administrator on 2017/3/18.
 */

$(function () {
    $('#submit').click(function (event) {
        event.preventDefault();

        var emailInput = $('input[name=email]');
        var usernameInput = $('input[name=username]');
        var passwordInput = $('input[name=password]');
        var password2Input = $('input[name=password2]');

        var email = emailInput.val();
        var username = usernameInput.val();
        var password = passwordInput.val();
        var password2 = password2Input.val();

        if(!email){
            xtalert.alertInfoToast('请输入邮箱!');
            return;
        }
        if(!username){
            xtalert.alertInfoToast('请输入用户名!');
            return;
        }
        if(!password){
            xtalert.alertInfoToast('请输入密码!');
            return;
        }
        if(!password2){
            xtalert.alertInfoToast('请确认密码!');
            return;
        }
        if(password !== password2){
            xtalert.alertInfoToast('两次密码不一致!');
            return;
        }

        xtajax.ajax({
            'url': '/cms_add_admin',
            'type': 'POST',
            'data': {
                'email': email,
                'username': username,
                'password': password,
                'password2': password2
            },
            'success': function (data) {
                var code = data['code'];
                if(code == 200){
                    emailInput.val('');
                    usernameInput.val('');
                    passwordInput.val('');
                    password2Input.val('');
                    xtalert.alertSuccessToast('恭喜！管理员添加成功！');
                }else{
                    xtalert.alertInfoToast(data['message']);
                }
            }
        })
    });
});
