#!./venv/bin/python

"""
Script containing mail functions/objects.
"""

import configparser
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
import base64

#Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read("conf/config.ini")
SECTION = "mailer_calls"

MAILER = CONFIG['mailer_calls']

logger = logging.getLogger(SECTION)

def mailer(subject, body):
    """
    Accepts subject and body for sending an email.
    """

    message = f"Subject: {subject}\n\n{body}"
    msg = MIMEText(message)

    msg["From"] = MAILER['from']
    msg["To"] = MAILER['to']
    msg["Subject"] = subject

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(MAILER['server'], MAILER['port'], context=context) as server:
        try:
            login_attempt = server.login(MAILER['from'], base64.b64decode(MAILER['passw']).decode("utf-8"))
            logger.debug(login_attempt)
            try:
                logger.info(f'Sending mail for {subject} to {msg["To"]}')
                email_send = server.send_message(msg, MAILER['from'], MAILER['to'])
                logger.debug(email_send)
                return "Mail Sent!"                
            except Exception as exp:
                logger.exception(exp)
                return str(exp)
        except Exception as exp:
            logger.exception(exp)
            return str(exp)

def main():
    """
    Main function.
    """

    logging.basicConfig(filename=CONFIG[SECTION]['log'],\
                    level=CONFIG[SECTION]['level'],\
                    format='%(asctime)s::%(name)s::%(funcName)s::%(levelname)s::%(message)s',\
                    datefmt="%Y-%m-%dT%H:%M:%S%z")

    logger.info("############# MAILER ##############")

    subject = "Karan Test."
    body = "content content content content content content content content"
    mailer(subject, body)

if __name__ == "__main__":
    main()
