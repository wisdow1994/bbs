from wtforms import (StringField, PasswordField, BooleanField, SubmitField, ValidationError, IntegerField,
                     TextAreaField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, URL

from ..utils.cache import captcha
from ..models import User
from ..common_forms import BaseForm, GraphCaptchaForm


class RegisterForm(GraphCaptchaForm):
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])

    email_captcha = StringField(validators=[DataRequired(message='必须输入邮箱验证码！')])

    username = StringField('用户昵称', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[\u4e00-\u9fa5A-Za-z0-9_.@]+$', flags=0, message='用户名只能包含中文,大小写字母,数字,小数点,下划线,@!')])

    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='两次输入的密码不一致!')])

    password2 = PasswordField('确认密码', validators=[DataRequired()])

    def validate_email_captcha(self, field):
        email_captcha = field.data
        email = self.email.data
        cache_captcha = captcha.get(email)
        if not cache_captcha or cache_captcha.lower() != email_captcha.lower():
            raise ValidationError(message='邮箱验证码错误!')
        return True

    def validate_email(self, field):  # validate_开头的函数和常规验证函数一样被调用
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('此邮箱已被注册!')
        return True

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('此昵称已被人使用!')
        return True


class LoginForm(BaseForm):
    email = StringField('电子邮箱/用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('一个月免登陆')
    graph_captcha = StringField(validators=[DataRequired(message='必须输入图形验证码！')])
    submit = SubmitField('登陆')


class AddPostForm(GraphCaptchaForm):
    title = StringField(validators=[DataRequired(message='必须输入标题！')])
    content = StringField(validators=[DataRequired(message='必须输入内容！')])
    board_id = IntegerField(validators=[DataRequired(message='必须输入板块id！')])


class AddCommentForm(BaseForm):
    post_id = IntegerField(validators=[DataRequired(message='必须包含所属文章id！')])
    comment_id = StringField(validators=[Length(0, 64)])  # 可以为空,因为一个表单验证对评论和二级评论使用
    content = StringField(validators=[DataRequired(message='必须输入内容！')])


class PostStarForm(BaseForm):
    post_id = IntegerField(validators=[DataRequired(message='必须包含所属文章id！')])
    is_star = BooleanField(validators=[DataRequired(message='必须输入行为!')])


class EditProfileForm(BaseForm):
    username = StringField('用户昵称', validators=[DataRequired(), Length(1, 64),
        Regexp('^[\u4e00-\u9fa5A-Za-z0-9_.@]+$', flags=0, message='用户名只能包含中文,大小写字母,数字,小数点,下划线,@!')])
    real_name = StringField('真实姓名', default='未填写', validators=[Length(0, 64)])
    location = StringField('所在城市', default='未填写', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我', default='未填写', validators=[Length(0, 64)])
    avatar = StringField('头像url', validators=[URL(message='头像格式不对！')])

