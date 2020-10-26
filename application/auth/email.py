from flask import render_template, current_app
from application.email import send_email
import os


def send_password_reset_email(user):
    print("send password reset email")
    token = user.get_reset_password_token()
    send_email("Tasker password reset",
                #sender=current_app.config['MAIL_USERNAME'],
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[user.email],
                text_body=render_template('email/reset_password.txt',
                                            user=user, token=token),
                html_body=render_template('email/reset_password.html',
                                         user=user, token=token))