// 初始化编辑器
$(function () {
    var editor = new wangEditor('editor');
    editor.create();
    window.editor = editor;
});

$(function () {
   $("#submit").click(function (event) {
       event.preventDefault();
        var post_id = $(this).attr('data-post-id');
        //通过button绑定的data-post-id来获取post.id的值
        var comment_id = $(".origin-comment-group").attr('data-comment-id');
        //所属父评论的id
        var content = window.editor.$txt.html();

        xtajax.post({
            'url': '/add_comments',
            'data': {
                'post_id': post_id,
                'content': content,
                'comment_id': comment_id
            },
            'success': function (data) {
                if(data['code'] == 200){
                    xtalert.alertSuccessToast('恭喜! 评论成功!');
                    setTimeout(function () {
                        window.location = '/detail/'+post_id+'/';
                    },500);
                //    延迟四秒钟后返回文章详情页
                }else{
                    xtalert.alertInfoToast(data['message']);
                }
            }
        })
    });
});


// 初始化七牛的事件

$(function () {
    var progressBox = $('#progress-box');
    var progressBar = progressBox.children(0);
    var uploadBtn = $('#upload-btn');
   xtqiniu.setUp({
       'browse_btn': 'upload-btn',
       'success': function (up,file,info) {
           var fileUrl = file.name;
           if(file.type.indexOf('video') >= 0){
               // 视频
               var videoTag = "<video width='640' height='480' controls><source src="+fileUrl+"></video>";
               window.editor.$txt.append(videoTag);
           }else{
                var imgTag = "<img src="+fileUrl+">";
                window.editor.$txt.append(imgTag);
           //把包含图片绝对路径的url追加进去
           }
       },

       'fileadded': function () {
           //上传开始
           progressBox.show();
           uploadBtn.button('loading');
       },
       'progress': function (up,file) {
           var percent = file.percent;
           //获得进度条的当前百分比
           progressBar.attr('aria-valuenow',percent);
           progressBar.css('width',percent+'%');
           progressBar.text(percent+'%');
       },
       'complete': function () {
           //文件上传后完成后执行
           progressBox.hide();
           progressBar.attr('aria-valuenow',0);
           progressBar.css('width','0%');
           progressBar.text('0%');
           uploadBtn.button('reset');
       }
   });
});