from threading import Thread
import logging
#from logging.handlers import SMTPHandler, RotatingFileHandler
from werkzeug.urls import url_parse
from flask import current_app
from flask_mail import Message
from application import mail
import os
from time import sleep   
from flask.templating import render_template
from utils.decorators import async_task
#from flask_mail import Mail, Message
import logging
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[current_app._get_current_object(), msg])
    thr.start()
    return thr
    # Thread(target=send_async_email,
    #        args=(current_app._get_current_object(), msg)).start()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)