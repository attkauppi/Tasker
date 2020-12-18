from flask import render_template, current_app
from application.email import send_email
from flask_mail import Message
from application import mail
import os
import logging
import sys

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(('[Microblog] Reset Your Password'),
               #sender=current_app.config['ADMINS'][0],
               sender=current_app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


# def send_password_reset_email(user):
#     # print("send password reset email")
#     # mail_pass = os.getenv('MAIL_PASSWORD')
#     # print("mail pass: ", mail_pass)
#     # token = user.get_reset_password_token()
#     # #text_body=render_template('email/reset_password.txt', user=user, token=token),
#     # msg = Message(subject='Lyhyt viesti', sender='tasker.info.noreply@gmail.com', recipients=['kauppi.ari@gmail.com'], body="Sent an email")
#     # send_email(msg)


#     #current_app.logger.info('{cls}.GET called'.format(cls=self.__class__.__name__))
#     logging.basicConfig(level=logging.DEBUG)
#     token = user.get_reset_password_token()
#     #send_email(subject='Reset password',
#     message = {
#         "subject": "a simple test",
#         "recipients": ['kauppi.ari@gmail.com'],
#         "text_body": "This is the content",
#         "html_body": None,
#         "sender": 'tasker.info.noreply@gmail.com'}
#     # message = dict(subject = 'reset email',
#     #            recipients=['kauppi.ari@gmail.com'],
#     #            text_body=render_template('email/reset_password.txt',
#     #                                      user=user, token=token),
#     #            #text_body="Hei",
#     #            #html_body=None,
#     #            html_body=render_template('email/reset_password.html',
#     #                                      user=user, token=token),
#     #            sender=['tasker.info.noreply@gmail.com'])
#     #            #html_body=None)
#     print(message)
#     try:
#         send_email(**message)
#         # send_email(_('[Microblog] Reset Your Password'),
#         #        sender=current_app.config['ADMINS'][0],
#         #        recipients=[user.email],
#         #        text_body=render_template('email/reset_password.txt',
#         #                                  user=user, token=token),
#         #        html_body=render_template('email/reset_password.html',
#         #                                  user=user, token=token))
#         # print("Email sent!")
#     except Exception as err:
#         logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

#         print("e.message: ", err)
        #return f"{err.__class__.__name__}: {err}"
        #current_app.logger.error("Failed to send email: {error}".format(error=err))
        #print("Oops! An error occurred when sending the email")
        #return "Oops! An error occurred when sending the email"
    #return "Mail has been sent"
    #sender='tasker.info.noreply@gmail.com'
    #recipients=user.email, 
    #text_body=render_template('email/reset_password.txt', user=user, token=token),
    #html_body=render_template('email/reset_password.html', user=user, token=token)
    #)
    #send_email("Tasker password reset", 
    #send_email()
    #             #sender=current_app.config['MAIL_USERNAME'],
    #             sender=current_app.config['MAIL_USERNAME'],
    #             recipients=[user.email],
    #             text_body=render_template('email/reset_password.txt',
    #                                         user=user, token=token),
    #             html_body=render_template('email/reset_password.html',
    #                                      user=user, token=token))