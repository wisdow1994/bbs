// 初始化编辑器
$(function () {
    var editor = new wangEditor('editor');
    editor.create();
    window.editor = editor;
});

// 发布帖子的执行事件
$(function () {
   $("#submit").click(function (event) {
       event.preventDefault();

       var titleInput = $('input[name=title]');
       var captchaInput = $('input[name=graph_captcha]');

       var title = titleInput.val();
       var board_id = $('.board-select').val();
       var content = window.editor.$txt.html();
       var graph_captcha = captchaInput.val();

       xtajax.post({
           'url': '/add_post',
           'data':{
               'title': title,
               'board_id': board_id,
               'content': content,
               'graph_captcha': graph_captcha
           },
           'success': function (data) {
               if(data['code'] == 200){
                   xtalert.alertConfirm({
                       'msg': '恭喜！帖子发表成功！',
                       'cancelText': '回到首页',
                       'confirmText': '再发一篇',
                       'cancelCallback': function () {
                           window.location = '/';
                       },
                       'confirmCallback': function () {
                           titleInput.val('');
                           window.editor.clear();
                           captchaInput.val('');
                           $('#graph-captcha-btn').click();
                           window.location = '/add_post';
                       }
                   });
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
