from flask_script import Server
from flask_migrate import Manager, MigrateCommand, Migrate

from sqlalchemy.exc import IntegrityError
from random import seed, randint
import forgery_py

from app import create_app, db
from app.models import User, Role, Board, Post, Comment

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)
manager.add_command('server', Server)


@manager.command
def generate_fake_user(count=15):  # 生成虚拟数据,先不用管它的写法
    seed()
    for i in range(count):
        u = User(email=forgery_py.internet.email_address(),
                 username=forgery_py.internet.user_name(True),
                 password=forgery_py.lorem_ipsum.word())
        if 8 < i < 15:
            u.role = Role.query.filter_by(name="管理员").first()
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    user_count = User.query.count()
    print('生成{}位虚拟用户'.format(user_count))
    for i in range(40):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(title=forgery_py.lorem_ipsum.title(),
                 content=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                 board_id=3, author=u)
        db.session.add(p)
        db.session.commit()
    print('生成了40篇虚拟')

# @manager.option('--username', '-u', dest='real_name', default='李存勖')
# @manager.option('--email', '-e', dest='email', default='18873614432@163.com')
# @manager.option('--password', '-p', dest='password', default='123456')
@manager.command
# def create_super_admin(username, email, password):
def create_super_user():
    # if User.query.filter_by(email=email).first():
    #     return '该用户已存在'
    # user = User(username=username, email=email, password=password)
    Role.insert_roles()  # 同时创建了3个写好的用户组
    user = User(username='李存勖', email='18873614432@163.com', password='1')
    user.role = Role.query.filter_by(name='超级管理员').first()
    db.session.add(user)
    db.session.commit()
    board1 = Board(name='python', author=user)
    board2 = Board(name='flask', author=user)
    board3 = Board(name='django', author=user)
    db.session.add_all([board1, board2, board3])
    db.session.commit()
    print('超级管理员< {} >添加成功', '板块添加成功'.format(user.username))


@manager.shell
def make_shell_context():
    return dict(db=db, User=User, app=app, Role=Role, Post=Post, Board=Board, Comment=Comment)


if __name__ == '__main__':
    manager.run()
