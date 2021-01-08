from threading import Thread
import logging
from werkzeug.urls import url_parse
from flask import current_app
from flask_mail import Message
from application import mail
import os
from time import sleep   
from flask.templating import render_template
from utils.decorators import async_task
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import flask
from flask import jsonify
import json

# Team function
# def send_team_invite_email(user):
#     token = user.generate_confirmation_token()
#     send_email(('[Tasker] Reset Your Password'),
#                #sender=current_app.config['ADMINS'][0],
#                sender=current_app.config['MAIL_USERNAME'],
#                recipients=[user.email],
#                text_body=render_template('auth/confirm.txt',
#                                          user=user, token=token),
#                html_body=render_template('auth/confirm.html',
#                                          user=user, token=token))                                        


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    print("flask.request.host: ", flask.request.host)
    print("flask.request.host_url: ", flask.request.host_url)
    
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg,
        flask.request.host_url,
        sender,
        recipients,
        text_body,
        html_body)).start()

def send_async_email(app, msg, flask_url, sender, recipients, text_body, html_body):
    
    with app.app_context():
        app.config['MAIL_DEBUG'] = True
        msg.sender = os.getenv('MAIL_DEFAULT_SENDER')
        url = flask_url + 'api/v1/auth/send_token'
        d = {}
        d['sender'] = os.getenv('MAIL_DEFAULT_SENDER')
        d['recipients'] = []
        for i in recipients:
            d['recipients'].append(i)
        recipients
        d['text_body'] = text_body
        d['html_body'] = html_body
        print(msg)
        print("msg type: ", type(msg))
        mail.send(msg)