# #from application import mail
# from flask_mail import Message
# from application.api import bp
# from flask import jsonify, request, url_for, abort
# from flask import current_app
# import flask
# from logging.handlers import SMTPHandler, RotatingFileHandler
# import smtplib, ssl
# from smtplib import SMTPAuthenticationError, SMTPException, SMTPServerDisconnected
# @bp.route('/auth/send_token', methods=["POST"])
# def send_token():
#     """ Sends token """
#     #message = flask.request.args.get('message')

#     message = request.get_json(force=True)
#     sender = message['sender']
#     recipients_list = message['recipients']
#     print("recipients_list: ", recipients_list)
#     recipients = []
#     text_body =message['text_body']
#     print("text_body: ", text_body)
#     html_body = message['html_body']
#     print("html_body: ", html_body)
#     mail_settings = {
#     "MAIL_SERVER": 'smtp.gmail.com',
#     "MAIL_PORT": 465,
#     "MAIL_USE_TLS": False,
#     "MAIL_USE_SSL": True,
#     "MAIL_USERNAME": 'tasker.info.noreply@gmail.com',
#     "MAIL_DEBUG": True
#     }
#     app = current_app._get_current_object()
#     app.config.update(mail_settings)

#     msg = Message(subject="Token", sender=sender, recipients=recipients_list, body="lyhyt viesti")
#     # try:
#     #     with app.app_context():
#     #         print("Lähetettävä viesti: ")
#     #         print(msg)
#     #         mail.send(msg)
#     retcode = 0
#     try:
#         mail.send(msg)
#     except SMTPAuthenticationError as e:
#         retcode = 2
#     except SMTPServerDisconnected as e:
#         retcode = 3
#     except SMTPException as e:
#         retcode=1
    
#     if retcode != 0:
#         print("retcode: ", retcode)
#     print("=============== RETCODE OLI NOLLA! ====================")
#     print("Lähetetty viesti ")
#     print(msg)
#     print("--------------------------")

#     from flask_mail import Mail
#     m = Mail(app)
#     m.send(msg)


    
#     # except SMTPException as err:
#     #     print(err.message)
#     #     current_app.logger.error("Failed to send email: {error}".format(error=err))
#     #     return "Oops! An error occurred when sending the email"


#     print("=============")
#     print("APIsta päivää, kuinka voin auttaa?")
#     #print(message)
#     print("Apin saama sender: ", message['sender'])
#     return jsonify(message)

