import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# from django.template import Context, Template
from jinja2 import Template
import logging

logger = logging.getLogger('email_logs')


class SMTP:

    def __init__(self, sender: dict, email: dict, email_sender: str, email_receiver: str):
        self.host = sender["host"]
        self.port = sender["port"]
        self.username = sender["username"]
        self.password = sender["password"]
        self.tls = sender["tls"]
        self.email_sender = email_sender
        self.email_receiver = email_receiver
        self.server = None
        self.subject = email["subject"]
        self.files = email["files"]
        self.content = email["content"]
        self.message = None

    def create_connection(self):
        if self.server is None:
            self.server = smtplib.SMTP(self.host, self.port)
            self.server.ehlo_or_helo_if_needed()
            if self.tls:
                self.server.starttls()
            self.server.login(self.username, self.password)

    def close_connection(self):
        if self.server is not None:
            self.server.close()

    def attach_files(self):
        for file in self.files:
            path = Path(file)
            attach_obj = MIMEApplication(
                path.read_bytes(),
                filename=path.name,
                _subtype=path.suffix.replace('.', '')
            )
            attach_obj.add_header(
                'Content-Disposition',
                'attachment',
                filename=path.name
            )
            self.message.attach(attach_obj)

    def create_message(self, context):
        body, subject = self.render(context)
        message = MIMEMultipart()
        message["From"] = self.email_sender
        message["To"] = self.email_receiver
        message["Subject"] = subject

        message.attach(MIMEText(body, "html"))
        self.message = message

    def render(self, context):
        # content = Context(context)
        # subject = Template(self.subject).render(content)
        # body = Template(self.content).render(content)

        subject = Template(self.subject).render(context)
        body = Template(self.subject).render(context)

        return body, subject

    def send(self, context=None):
        if context is None:
            context = {}
        if self.server is not None:
            self.create_message(context)
            self.attach_files()
            logger.debug(f"{self.server.send_message(self.message)}")
        else:
            raise Exception('Server not created!')
