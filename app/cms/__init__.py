from flask import Blueprint

cms = Blueprint('cms', __name__, subdomain='cms')

from . import views, errors

from app.models import Permission


@cms.app_context_processor  # 上下文处理器让变量在所有模板中可以使用
def inject_permissions():
    return dict(Permission=Permission)
