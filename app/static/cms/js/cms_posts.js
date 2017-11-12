$(function () {
    $('.hightlight-btn').click(function (event) {
        event.preventDefault();
        var post_id = $(this).attr('data-post-id');
        var high_light = parseInt($(this).attr('data-is-highlight'));
        console.log(high_light);
        xtajax.ajax({
            'url': '/high_light',
            'type': 'POST',
            'data': {
                'post_id': post_id,
                'high_light': high_light
            },
            'success': function (data) {
                if(data['code'] == 200){
                    var msg = '';
                    if(!high_light){
                        msg = '取消加精成功！';
                    }else{
                        msg = '加精成功！';
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


// 这个是用来做移除帖子的操作
$(function () {
    $(".remove-btn").click(function (event) {
        event.preventDefault();
        var post_id = $(this).attr('data-post-id');
        xtajax.post({
            'url': '/remove_post',
            'data':{
                'post_id': post_id
            },
            'success':function (data) {
                if(data['code'] == 200){
                    var msg = '帖子移除成功！';
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

// 排序的事件
$(function () {
    $('#sort-select').change(function (event) {
       var value = $(this).val();
       var newHref = xtparam.setParam('/set_sort/','sort_id',value);
       //别人采用的是window.location.href当前页面收集sort_id的值,但是由于我的分页做得?index=num,会引起冲突
       window.location = newHref;
   });
});

// 板块过滤的
$(function () {
    $("#board-filter-select").change(function (event) {
       var value = $(this).val();
       var newHref = xtparam.setParam('/set_sort/','board_id',value);
       window.location = newHref;
   });
});