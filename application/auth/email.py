from flask import render_template, current_app
from application.email import send_email
from flask_mail import Message
from application import mail
import os
import logging
import sys

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(('[Tasker] Reset Your Password'),
               sender=current_app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_confirmation_email(user):
    token = user.generate_confirmation_token()
    send_email(('[Tasker] Confirm your account'),
               sender=current_app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('auth/email/confirm.txt',
                                         user=user, token=token),
               html_body=render_template('auth/email/confirm.html',
                                         user=user, token=token))                                        

# def send_password_reset_email(user):
#     # print("send password reset email")
#     # mail_pass = os.getenv('MAIL_PASSWORD')
#     # print("mail pass: ", mail_pass)
#     # token = user.get_reset_password_token()
#     # #text_body=render_template('email/reset_password.txt', user=user, token=token),
#     # msg = Message(subject='Lyhyt viesti', sender='tasker.info.noreply@gmail.com', recipients=['kauppi.ari@gmail.com'], body="Sent an email")
#     # send_email(msg)

