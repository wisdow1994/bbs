from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            return True
        except:
            return False


def send_mail(subject, receivers, body=None, html=None):
    # 必须要有接收者，没有就断言失败
    app = current_app._get_current_object()  # 程序上下文,当前程序的实例
    # 如果body和html都为空，那么就返回False，因为没有东西可以发送
    if not body and not html:
        return False
    # 如果是字符串，要包裹成数组
    if isinstance(receivers, str):
        receivers = [receivers]
    msg = Message(subject=subject, sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=receivers, body=body, html=html)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
