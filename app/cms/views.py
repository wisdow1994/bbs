from flask import render_template, redirect, url_for, flash, request, abort, session, make_response
from flask_login import logout_user, login_required, login_user, current_user
from app import db
from app.common_forms import (LoginForm, ChangePasswordForm, ChangeEmailForm, CreateForm, CMSEditBoardForm)
from app.models import User, Role, Permission, Board, Post, Comment, PostStar
from . import cms
from ..utils import json, email
from ..utils.cache import captcha
from ..utils.decorators import permission_required, super_admin_required


@cms.route('/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMIN)
def index():
    return render_template('cms/cms_index.html')


@cms.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticated(form.email.data, form.password.data)
        if user and user.ban_bool:  # 普通用户在前往主页的时候被拦截
            login_user(user, remember=form.remember_me.data)  # 根据布尔值,是否记录用户会话
            return redirect(request.args.get('next') or url_for('cms.index'))
        abort(403)  # 被禁用那么返回403
    return render_template('cms/cms_login.html', form=form)


@cms.route('/logout')
@login_required
@permission_required(Permission.ADMIN)
def logout():
    logout_user()
    flash('你已经注销用户')
    return redirect(url_for('cms.login'))


@cms.route('/change-password', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMIN)
def change_password():  # 修改当前管理员的密码
    if request.method == 'GET':
        return render_template('cms/cms_change_password.html', form=ChangePasswordForm())
    else:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            if current_user.verify_password(form.old_password.data):
                current_user.password = form.password.data
                db.session.add(current_user)
                flash('你的密码修改成功!')
                return json.json_result()
                # return redirect(url_for('cms.index'))
            else:
                return json.json_params_error(message='原密码错误')
        else:
            message = form.get_error()
            return json.json_params_error(message)


@cms.route('/profile')
@login_required
@permission_required(Permission.ADMIN)
def profile():  # 当前管理员的资料
    return render_template('cms/cms_profile.html')


@cms.route('/send_token')
@login_required
@permission_required(Permission.ADMIN)
def send_token():  # 发送验证码
    to_email = request.args.get('email')  # 使用获取明文的邮箱数据
    # if current_user.email == to_email:
    #     return json.json_params_error(message='新邮箱与老邮箱一致，无需修改！')
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


@cms.route('/change_email', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMIN)
def change_email():  # 管理员修改邮箱
    if request.method == 'GET':
        return render_template('cms/cms_change_email.html')
    else:
        form = ChangeEmailForm(request.form)
        if form.validate_on_submit():
            email = form.email.data
            current_user.email = email
            db.session.commit()
            return json.json_result()
        else:
            return json.json_params_error(message=form.get_error())


@cms.route('/cms_user_list', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMIN)
def cms_user_list():  # 管理员或者超级管理员，能够看到普通用户,功能类似,所以共用一个html模板
    users = Role.query.filter_by(name='用户').first().users.all()
    return render_template('cms/cms_admin_list.html', users=users, point='cms.cms_add_user', title='用户')


@cms.route('/cms_admin_list', methods=['GET', 'POST'])
@login_required
@super_admin_required
def cms_admin_list():  # 超级管理员才能看到这个管理员列表
    users = Role.query.filter_by(name='管理员').first().users.all()
    return render_template('cms/cms_admin_list.html', users=users, point='cms.cms_add_admin', title='管理员')


@cms.route('/cms_add_admin', methods=['GET', 'POST'])
@login_required
@super_admin_required
def cms_add_admin():  # 创建管理员,超级管理员只能创建管理员,不能自己创建超级管理员
    if request.method == 'GET':
        return render_template('cms/cms_add_admin.html', form=CreateForm(), title='管理员')
    else:
        form = CreateForm(request.form)
        print('验证通过之前')
        if form.validate_on_submit():
            user = User(email=form.email.data, username=form.username.data, password=form.password.data)
            user.role = Role.query.filter_by(name="管理员").first()
            print('form验证通过')
            db.session.add(user)
            db.session.commit()
            return json.json_result()
        else:
            return json.json_params_error(message=form.get_error())


@cms.route('/cms_add_user', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMIN)
def cms_add_user():  # 创建普通用户,超级管理员/管理员
    if request.method == 'GET':
        return render_template('cms/cms_add_admin.html', form=CreateForm(), title='用户')
    else:
        form = CreateForm(request.form)
        print('验证通过之前')
        if form.validate_on_submit():
            user = User(email=form.email.data, username=form.username.data, password=form.password.data)
            print('form验证通过')
            db.session.add(user)
            db.session.commit()
            return json.json_result()
        else:
            return json.json_params_error(message=form.get_error())


@cms.route('/change_active/<int:id>/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMIN)
def change_active(id):  # 禁用一个管理员或者普通用户
    user = User.query.get_or_404(id)  # django中的形式:get(pk=id)
    user.ban_bool = bool(int(request.args.get('ban_Bool')))  # 根据get方式传入的bool参数设置ban_bool的激活状态
    # 注意一点，通过get传过来的0是一个字符串,转换为bool还是True
    db.session.add(user)
    db.session.commit()
    if user.ban_bool:
        flash('已经恢复<{}-{}>'.format(user.role.name, user.username))
    flash('已经禁用<{}-{}>'.format(user.role.name, user.username))
    if user.role.name == '用户':
        return redirect(request.args.get('next') or url_for('cms.cms_user_list'))  # 返回用户列表
    return redirect(request.args.get('next') or url_for('cms.cms_admin_list'))  # 返回到管理员列表


@cms.route('/user_profile/<id>', methods=['GET', 'POST'])
@login_required
def user_profile(id):  # 用户资料详情
    user = User.query.get_or_404(id)
    return render_template('cms/cms_user_profile.html', user=user)


@cms.route('/boards')
@login_required
@permission_required(Permission.ADMIN)
def cms_boards():
    boards = Board.query.all()
    return render_template('cms/cms_boards.html', boards=boards)


@cms.route('/add_board/', methods=['POST'])
@login_required
@permission_required(Permission.ADMIN)
def add_board():  # 新增一个模块
    name = request.form.get('real_name')
    # 判断是否有name这个参数
    if not name:
        return json.json_params_error(message='必须指定板块的名称！')

    # 2. 判断这个名字在数据库中是否存在
    board = Board.query.filter_by(name=name).first()
    if board:
        return json.json_params_error(message='该板块已经存在，不能重复添加！')

    # 3. 创建板块模型
    board = Board(name=name)
    board.author = current_user
    db.session.add(board)
    db.session.commit()
    return json.json_result()


@cms.route('/edit_board/', methods=['POST'])
@login_required
@permission_required(Permission.ADMIN)
def edit_board():  # 修改模块的名字
    form = CMSEditBoardForm(request.form)
    if form.validate():
        board_id = form.board_id.data
        name = form.name.data
        board = Board.query.get(board_id)
        board.name = name
        db.session.commit()
        return json.json_result()
    else:
        return json.json_params_error(message=form.get_error())


@cms.route('/delete_board/', methods=['POST'])
@login_required
@permission_required(Permission.ADMIN)
def delete_board():  # 删除模块
    board_id = request.form.get('board_id', 2)
    print('参数是2')
    if not board_id:
        return json.json_params_error(message='没有指定板块id！')

    board = Board.query.filter_by(id=board_id).first()
    if not board:
        return json.json_params_error(message='该板块不存在，删除失败！')

    # 判断这个板块下的帖子数是否大于0，如果大于0就不让删除
    # if board.posts.count() > 0:
    #     return xtjson.json_params_error(message=u'该板块下的帖子数大于0，不能删除！')
    db.session.delete(board)
    db.session.commit()
    return json.json_result()


@cms.route('/cms_comments')
@login_required
@permission_required(Permission.ADMIN)
def cms_comments():  # 帖子列表
    pass


@cms.route('/set_sort/')
def set_sort():
    """根据sort_id的数字设置排序的规则
    1，最新帖子，2，精华帖子， 3， 点赞最多， 4，评论最多
    board_id用来按照板块排序"""
    if request.args.get('sort_id'):
        session['sort_id'] = request.args.get('sort_id')
        print(request.args.get('sort_id'))
        return redirect(url_for('cms.cms_posts'))
    elif request.args.get('board_id'):
        session['board_id'] = request.args.get('board_id')
        print(request.args.get('board_id'))
        return redirect(url_for('cms.cms_posts'))


@cms.route('/cms_posts')
@login_required
@permission_required(Permission.ADMIN)
def cms_posts():  # 帖子列表
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
        query = query.filter(Post.board_id == board_id)
    pagination = query.paginate(page, 12, error_out=False)
    posts = pagination.items
    return render_template('cms/cms_posts.html', boards=boards, posts=posts,
                           post_all_count=Post.query.filter_by(is_remove=False).count(),
                           pagination=pagination, sort_type=sort_id, board_type=board_id)


@cms.route('/high_light', methods=['POST'])
@login_required
@permission_required(Permission.ADMIN)
def high_light():  # 加精或者取消
    high_light = request.form.get('high_light')
    post_id = request.form.get('post_id')
    print(high_light, type(high_light))
    post = Post.query.get_or_404(post_id)
    post.high_light = bool(int(high_light))
    return json.json_result()


@cms.route('/remove_post', methods=['POST'])
@login_required
@permission_required(Permission.ADMIN)
def remove_post():  # 物理上没有删除这篇文章,只是被隐藏起来
    post_id = request.form.get('post_id')
    post = Post.query.get_or_404(post_id)
    post.is_remove = True
    return json.json_result()
