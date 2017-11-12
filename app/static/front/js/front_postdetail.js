$(function () {
    $('#star-btn').click(function (event) {
        event.preventDefault();
        var post_id = $(this).attr('data-post-id');
        var is_star = parseInt($(this).attr('data-is-star'));
        xtajax.ajax({
            'url': '/post_star',
            'type': 'post',
            'data': {
                'post_id': post_id,
                'is_star': !is_star
            },
            'success': function (data) {
                if(data['code'] == 200){
                    var msg = '';
                    if(is_star){
                        msg = '取消赞成功！';
                    }else {
                        msg = '点赞成功！';
                    }
                    xtalert.alertSuccessToast(msg);
                    setTimeout(function () {
                        window.location.reload();
                    },500);
                }else{
                    xtalert.alertInfoToast(data['message']);
                }
            }
        })
    });
});
