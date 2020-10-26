from threading import Thread
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import current_app
from flask_mail import Message
from application import mail
import os
from time import sleep   

# from threading import Thread
# from flask import current_app
# from flask_mail import Message
# from application import mail
# #from .decorators import async

# def threading(f):
#     def wrapper(*args, **kwargs):
#         thr = Thread(target=f, args=args, kwargs=kwargs)
#         thr.start()
#     return wrapper

# TODO: Doesn't work with the fancy async & application factory system.
def _send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as err:
            app.logger.error("Error during mail send: {0}".format(err))


def send_email(subject, sender, recipients, text_body, html_body):
    print("recipients: ", recipients)
    print("subject: ", subject)
    print("sender: ", sender)
    app = current_app._get_current_object()
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    #msg.html = html_body
    thr= Thread(target=_send_async_email,
           args=[app, msg])
    thr.start()
    return thr
    #send_async_email(app, msg)