from flask import render_template
from . import cms


# @cms.errorhandler这种形式只能给蓝图内的视图使用,下面可以注册全站使用的errors
@cms.app_errorhandler(401)
def forbidden_error(e):  # 没有权限
    return render_template('401.html'), 401


@cms.app_errorhandler(403)
def unauthorized_error(e):  # 已经拉黑,拒绝操作
    return render_template('403.html'), 403


@cms.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@cms.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500