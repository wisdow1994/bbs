from flask import Blueprint

auth = Blueprint('auth', __name__)


from . import views, errors
from app.models import Permission


@auth.app_context_processor  # 上下文处理器让变量在所有模板中可以使用
def inject_permissions():
    return dict(Permission=Permission)