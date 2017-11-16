/**
 * Created by Administrator on 2016/12/14.
 对jquery的ajax的封装,多了一个flask_wtfd的CSRFToke
不需要每个ajax写'csrf_token':$('input[name=csrf_token]').val()
 */


'use strict';

var xtajax = {
	'get':function(args) {
		args['method'] = 'GET';
		this.ajax(args);
	},
	'post':function(args) {
		args['method'] = 'POST';
		this.ajax(args);
	},
	'ajax':function(args) {
		// 设置csrftoken
		this._ajaxSetup();
		$.ajax(args);
	},
	'_ajaxSetup': function() {
		$.ajaxSetup({
			'beforeSend':function(xhr,settings) {
				if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    // var csrftoken = $('input[name=csrf_token]').attr('value');
                    //这种形式就不适合wtf.quick_form(form)这种形式了
                    // var csrftoken = "{{ csrf_token() }}"
                    //应该要学会查看浏览器的控制台分析,可以直接定位到引发错误的js代码位置
                    var csrftoken = $('meta[name=csrf-token]').attr('content');
                     xhr.setRequestHeader("X-CSRFToken", csrftoken)
                }
			}
		});
	}
}