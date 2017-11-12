from flask import render_template, redirect, url_for, flash, request, jsonify, make_response, views, session
from flask_login import logout_user, login_required, login_user, current_user
from app import db
import qiniu
import constants
from config import Config
from manage import app
from .froms import RegisterForm, LoginForm, AddPostForm, AddCommentForm, PostStarForm, EditProfileForm
from app.models import User, Role, Permission, Board, Post, Comment, PostStar
from . import auth
from ..utils import json, email
from ..utils.cache import captcha
from ..utils.decorators import permission_required, super_admin_required


@auth.before_app_request
def before_request():
    # 用于更新用户的最后更新时间，每次请求之前都会更新,那么这个最后访问时间是给别人看的了
    '''before each request, even if outside of a blueprint.'''
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    return render_template('front/front_profile.html', user=user)


@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        print('是一个post请求')
        form = EditProfileForm(request.form)
        print('数据验证之前')
        if form.is_submitted():
            # 现在表单验证通过不了
            print('数据验证成功')
            current_user.real_name = form.real_name.data
            current_user.avatar = form.avatar.data
            current_user.username = form.username.data
            current_user.location = form.location.data
            current_user.about_me = form.about_me.data
            db.session.add(current_user)
            return json.json_result()
        return json.json_params_error(message='数据格式不正确!')
    return render_template('front/front_edit_profile.html')


@auth.route('/set_sort/')
def set_sort():
    """根据sort_id的数字设置排序的规则
    1，最新帖子，2，精华帖子， 3， 点赞最多， 4，评论最多
    board_id用来按照板块排序"""
    resp = make_response(redirect(url_for('auth.index')))
    if request.args.get('sort_id'):
        session['sort_id'] = request.args.get('sort_id')
        # resp.set_cookie('sort_id', request.args.get('sort_id'), max_age=24*60*60)
        return resp
    elif request.args.get('board_id'):
        session['board_id'] = request.args.get('board_id')
        # resp.set_cookie('board_id', request.args.get('board_id'), max_age=24*60*60)
        return resp


@auth.route('/')
def index():
    """主页,已经分页,并支持1，最新帖子，2，精华帖子， 3， 点赞最多， 4，评论最多排序"""
    boards = Board.query.all()  # 板块
    page = request.args.get('page', 1, type=int)  # 分页的第几页数

    sort_id = int(session.get('sort_id', 1))  # 不接受默认值,那么使用位或操作
    print('sort_id是', sort_id)
    """根据sort_id的数字设置排序的规则
        1，最新帖子，2，精华帖子， 3， 点赞最多， 4，评论最多"""
    # 默认按照最新发布时间排序, 并且根据sort_id显式的展示排序的方式
    if sort_id == 1:
        query = Post.query.order_by(Post.create_time.desc())
    elif sort_id == 2:
        query = Post.query.filter_by(is_remove=False).filter_by(high_light=True).order_by(
            Post.create_time.desc())
    elif sort_id == 3:
        query = db.session.query(Post).outerjoin(PostStar).group_by(Post.id).order_by(
            db.func.count(PostStar.id).desc(), Post.create_time.desc())
    elif sort_id == 4:
        query = db.session.query(Post).outerjoin(Comment).group_by(Post.id).order_by(
            db.func.count(Comment.id).desc(), Post.create_time.desc())
    board_id = int(session.get('board_id', 0))  # get不接受关键字参数
    print('session中获取的board_id: ', session.get('board_id'))
    print('根据排序board_id是', board_id, type(board_id))
    # 根据board_id来显示文章所属的板块,默认为0时显示所有文章
    if board_id > 0:  # board_id等于0显示所有文章
        query = query.filter(Post.board_id==board_id)
    pagination = query.paginate(page, 12, error_out=False)
    posts = pagination.items
    return render_template('front/front_index.html', boards=boards, posts=posts,
                           post_all_count=Post.query.filter_by(is_remove=False).count(),
                           pagination=pagination, sort_type=sort_id, board_type=board_id)


@auth.route('/detail/<int:post_id>/')
def detail(post_id):  # 文章详情页
    post = Post.query.get_or_404(post_id)
    post.read_count += 1  # 阅读次数+1
    star_id_set = [star.author.id for star in post.stars]
    return render_template('front/front_detail.html', post=post, star_id_set=star_id_set)


class RegisterView(views.MethodView):

    def get(self, message=None, **kwargs):
        context = {
            'message': message,
        }
        context.update(kwargs)
        return render_template('auth/auth_register.html', **context)

    def post(self):
        form = RegisterForm(request.form)
        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data
            user = User(email=email, username=username, password=password)
            db.session.add(user)
            print('验证成功')
            return redirect(url_for('auth.index'))
        else:
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            password2 = request.form.get('password2')
            return self.get(message=form.get_error(), email=email, username=username,
                            password=password, password2=password2)


auth.add_url_rule('/register', view_func=RegisterView.as_view('auth.register'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password2.data
        user = User(email=email, username=username, password=password)
        db.session.add(user)
        return redirect(url_for('auth.index'))
        print('验证通过')
    return render_template('auth/auth_register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticated(form.email.data, form.password.data)
        if user:  # 普通用户在前往主页的时候被拦截
            login_user(user, remember=form.remember_me.data)  # 根据布尔值,是否记录用户会话
            return redirect(request.args.get('next') or url_for('auth.index'))
    return render_template('auth/auth_login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经注销用户')
    return redirect(url_for('auth.index'))


@auth.route('/generate')
def generate_imageCaptcha():  # 用来返回图片流
    from ..utils.cache.imageCache import ImageCaptcha
    from io import BytesIO
    text, image = ImageCaptcha.gene_code()
    # StringIO相当于是一个管道
    out = BytesIO()
    # 把image塞到StingIO这个管道中
    image.save(out, 'png')
    # 将StringIO的指针指向开始的位置
    out.seek(0)

    # 生成一个响应对象，out.read是把图片流给读出来
    response = make_response(out.read())
    # 指定响应的类型
    response.content_type = 'image/png'
    captcha.set(text.lower(), text.lower(), timeout=300)
    return response


@auth.route('/send_token')
def send_token():  # 发送验证码
    to_email = request.args.get('email')  # 使用获取明文的邮箱数据
    if captcha.get(to_email):
        return json.json_params_error('该邮箱已经发送验证码了！')
    import random
    import string
    source = string.ascii_letters + string.digits  # 生成所有大小写字母和数字的字符串
    token_list = random.sample(source, 6)  # 随机生成六位数的验证码列表
    token = ''.join(token_list)  # 转换为字符串

    if email.send_mail(subject='邮件验证码', receivers=to_email, body='邮箱验证码是：' + token):
        # 1. 为了下次可以验证邮箱和验证码
        # 2. 为了防止用户不断的刷这个接口
        captcha.set(to_email, token)  # 设置进缓存中
        return json.json_result()  # 返回code=200的json
    else:
        return json.json_server_error()


@auth.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    """发表新帖子"""
    if request.method == 'GET':
        boards = Board.query.all()
        return render_template('front/front_addpost.html', boards=boards)
    else:
        form = AddPostForm(request.form)
        print('验证之前')
        if form.validate_on_submit():
            print('验证成功')
            title = form.title.data
            content = form.content.data
            board_id = form.board_id.data
            post = Post(title=title, content=content, board_id=board_id)
            post.author = current_user._get_current_object()
            db.session.add(post)
            print('成功')
            return json.json_result()
        else:
            return json.json_params_error(message='表单验证失败!')


@auth.route('/add_comments', methods=['GET', 'POST'])
@login_required
def add_comments():
    """发表评论或者回复父评论"""
    if request.method == 'GET':
        content = {
            'post': Post.query.get_or_404(request.args.get('post_id'))
        }
        print('get请求')
        comment_id = request.args.get('comment_id', None)  # 有可能为空
        if comment_id:
            content['parent_comment'] = Comment.query.get_or_404(comment_id)
        return render_template('front/front_addcomment.html', **content)
    else:
        form = AddCommentForm(request.form)
        print('post请求')
        if form.validate_on_submit():
            content = form.content.data
            post = Post.query.get_or_404(form.post_id.data)
            comment = Comment(content=content, author=current_user._get_current_object())
            comment_id = form.comment_id.data
            if comment_id:  # 有父评论的情况
                parent_comment = Comment.query.get_or_404(int(comment_id))
                comment.parent_comment = parent_comment
            comment.post = post  # 没有父评论的情况下
            db.session.add(comment)
            return json.json_result()


@auth.route('/post_star', methods=['POST'])
@login_required
def post_star():  # 帖子点赞
    form = PostStarForm(request.form)
    if form.validate_on_submit():
        post_id = form.post_id.data
        post = Post.query.get_or_404(post_id)
        is_star = form.is_star.data
        if is_star:
            star = PostStar(author=current_user._get_current_object(), post=post)
            db.session.add(star)
            # db.session.commit()
            return json.json_result()
        else:
            star = PostStar.query.filter_by(author_id=current_user.id, post_id=post_id).first()
            db.session.delete(star)
            return json.json_result()


@auth.route('/qiniu_token/')
def qiniu_token():  # 上传图片或者视频
    # 授权
    q = qiniu.Auth(Config.QINIU_ACCESS_KEY, Config.QINIU_SECRET_KEY)
    # 选择七牛的云空间
    bucket_name = 'demo'  # 七牛的存储空间
    # 生成token
    token = q.upload_token(bucket_name)
    return jsonify({'uptoken': token})
