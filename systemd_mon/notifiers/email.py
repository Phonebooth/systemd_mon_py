import smtplib

from email.mime.text import MIMEText

from systemd_mon.errors import NotifierError
from systemd_mon.formatters.state_table_formatter import StateTableFormatter
from systemd_mon.notifiers.base import Base


class Email(Base):
    def __init__(self, options):
        super(Email, self).__init__(options)
        if not self.options.get("to"):
            raise NotifierError("The 'to' address must be set to use the email notifier")

    def notify_start(self, hostname):
        self.log("notify_start called")

    def notify_stop(self, hostname):
        self.log("notify_stop called")

    def notify(self, notification):
        unit = notification.unit
        subject = "{0}: {1} on {2}: {3}".format(
            notification.type_text(),
            unit.name,
            notification.hostname,
            unit.state_change.status_text(),
        )
        body = "Systemd unit {0} on {1} {2}: {3} ({4})\n\n".format(
            unit.name,
            notification.hostname,
            unit.state_change.status_text(),
            unit.state.active,
            unit.state.sub,
        )
        if unit.state_change.length() > 1:
            body += StateTableFormatter(unit).as_text()
        body += "\nRegards, SystemdMon"

        self._send_mail(subject, body)
        self.log("sent email notification")

    def _send_mail(self, subject, body):
        self.debug("Sending email to {0}:".format(self.options["to"]))
        self.debug(' -> Subject: "{0}"'.format(subject))
        self.debug(' -> Message: "{0}"'.format(body))

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["To"] = self.options["to"]
        msg["From"] = self.options.get("from", "systemdmon@localhost")

        smtp_opts = self.options.get("smtp", {})
        host = smtp_opts.get("address", "localhost")
        port = int(smtp_opts.get("port", 25))

        with smtplib.SMTP(host, port,
                          local_hostname=smtp_opts.get("domain")) as conn:
            if smtp_opts.get("enable_starttls_auto"):
                conn.starttls()
            user = smtp_opts.get("user_name")
            password = smtp_opts.get("password")
            if user and password:
                conn.login(user, password)
            conn.send_message(msg)
