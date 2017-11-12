from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

from .utils.cache import captcha
from .models import User, Role, Board


class BaseForm(FlaskForm):
    def get_error(self):
        _, value = self.errors.popitem()  # 随机/从最后pop一个字典,拆包获得value
        return value


class GraphCaptchaForm(BaseForm):  # 把验证图形验证码抽象出来
    graph_captcha = StringField(validators=[DataRequired(message='必须输入图形验证码！')])

    def validate_graph_captcha(self, field):
        graph_captcha = field.data
        cache_captcha = captcha.get(graph_captcha.lower())
        if not cache_captcha or cache_captcha.lower() != graph_captcha.lower():
            raise ValidationError(message='图形验证码错误！')
        return True


class CMSEditBoardForm(BaseForm):
    board_id = IntegerField(validators=[DataRequired(message=u'必须输入板块id！')])
    name = StringField(validators=[DataRequired(message=u'必须输入板块名称！')])

    def validate_board_id(self,field):
        board_id = field.data
        board = Board.query.filter_by(id=board_id).first()
        if not board:
            raise ValidationError(message=u'该板块不能存在！')
        return True

    def validate_name(self,field):
        name = field.data
        board = Board.query.filter_by(name=name).first()
        if board:
            raise ValidationError(message=u'该名称已经存在，不能修改！')
        return True


class CreateForm(BaseForm):
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])

    username = StringField('用户昵称', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[\u4e00-\u9fa5A-Za-z0-9_.@]+$', flags=0, message='用户名只能包含中文,大小写字母,数字,小数点,下划线,@!')])

    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='两次输入的密码不一致!')])

    password2 = PasswordField('确认密码', validators=[DataRequired()])

    submit = SubmitField('创建')

    def validate_email(self, field):  # validate_开头的函数和常规验证函数一样被调用
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('此邮箱已被注册!')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('此昵称已被人使用!')


class LoginForm(BaseForm):
    email = StringField('电子邮箱/用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('一个月免登陆')
    submit = SubmitField('登陆')


class ChangePasswordForm(BaseForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])

    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次输入的密码不一致!')])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('修改密码')


class ChangeEmailForm(BaseForm):
    email = StringField(validators=[DataRequired(message='必须输入邮箱！'), Email(message='邮箱格式不满足！')])
    token = StringField(validators=[DataRequired(message='必须输入验证码！')])

    def validate_token(self, field):
        email = self.email.data
        token = field.data
        token_cache = captcha.get(email)
        if not token_cache or token_cache.lower() != token:
            raise ValidationError(message='验证码错误！')
        return True


class EditProfileForm(BaseForm):
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])

    username = StringField('用户昵称', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[\u4e00-\u9fa5A-Za-z0-9_.@]+$', flags=0, message='用户名只能包含中文,大小写字母,数字,小数点,下划线,@!')])

    role = SelectField('权限', coerce=int)

    submit = SubmitField('修改')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        # 下拉菜单的元素由元组组成,第一个数字是存储的role.id,第二个是菜单显示的文本,排除掉超级管理员
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all() if role.name != '超级管理员']


