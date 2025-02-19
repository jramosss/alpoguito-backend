import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from Event import Event
from utils import generate_html_for_events

TEST_EMAIL = 'jramostod@gmail.com'
RECIPIENTS = [
    TEST_EMAIL
]

smtp_server = '0.0.0.0'
smtp_port = 1025

def send_email(events: list[Event]):
    msg = MIMEMultipart()
    msg['Subject'] = 'Eventos de musica a ciegas este mes'
    me = TEST_EMAIL
    msg['From'] = me
    msg['To'] = ', '.join(RECIPIENTS)
    msg['Content-Type'] = 'text/html'
    msg.attach(MIMEText(generate_html_for_events(events), 'html'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.sendmail(me, RECIPIENTS, msg.as_string())
        server.quit()