$(function () {
    $('#submit').click(function (event) {
        // var $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
        event.preventDefault();
        //禁用按钮的默认提交行为,改用ajax的post提交数据
        var emailInput = $('input[name=email]');
        var roleSelect = $('select[name=role]');
        var usernameInput = $('input[name=username]');

        xtajax.ajax({
            'url': $SCRIPT_ROOT,
            'type':'POST',
            'data': {
                'email': emailInput.val(),
                'role': roleSelect.val(),
                'username': usernameInput.val()
            },
            'success':function (data) {
                if(data['code'] == 200){
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
