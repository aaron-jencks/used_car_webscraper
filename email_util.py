import smtplib
import ssl

from email.mime.text import MIMEText


class EmailServer:
    """Wraps the email protocol of python into an easy to use api"""

    def __init__(self, sender_email: str = "noreply.aaronjencks@gmail.com",
                 smtp: str = "smtp.gmail.com", port: int = 465):
        """Creates an smtp server with the given sender email and smtp address,
        requires that you login upon initialization"""
        self.sender = sender_email
        self.password = input("Email Password? ")
        self.smtp = smtp
        self.port = port
        self.ssl_context = ssl.create_default_context()
        self.server = None
        self.is_running = False
        self.backlog = []

    def __del__(self):
        self.stop()

    def __send_mime(self, mime: MIMEText):
        """Sends an email if the server is running, if the server is not running, then puts it into the backlog"""
        if self.is_running:
            self.server.sendmail(self.sender, mime["To"], mime.as_string())
        else:
            self.backlog.append(mime)

    def start(self):
        """Starts the server, and sends any backlogged messages"""
        self.server = smtplib.SMTP_SSL(self.smtp, self.port, context=self.ssl_context)
        self.server.login(self.sender, self.password)

        self.is_running = True

        if len(self.backlog) > 0:
            for m in self.backlog:
                self.__send_mime(m)
            self.backlog = []

    def stop(self):
        """Stops the server, if it's running, otherwise does nothing"""
        if self.is_running:
            self.is_running = False
            self.server.quit()

    def send_mail(self, tgt: str, subj: str = "", msg: str = ""):
        """Sends an email if the server is running, if the server is not running, then puts it into the backlog"""
        message = MIMEText(msg, 'html')
        message["Subject"] = subj
        message["From"] = self.sender
        message["To"] = tgt

        if self.is_running:
            self.server.sendmail(self.sender, tgt, message.as_string())
        else:
            self.backlog.append(message)
