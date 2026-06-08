import json

try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, Request, URLError

from systemd_mon.notifiers.base import Base


class Slack(Base):
    def __init__(self, options):
        super(Slack, self).__init__(options)
        if not self.options.get("webhook_url"):
            raise ValueError("Slack notifier requires 'webhook_url'")

    def notify_start(self, hostname):
        message = "SystemdMon is starting on {0}".format(hostname)
        self._post("", attachments=[{
            "fallback": message,
            "text": message,
            "color": "good",
        }])

    def notify_stop(self, hostname):
        message = "SystemdMon is stopping on {0}".format(hostname)
        self._post("", attachments=[{
            "fallback": message,
            "text": message,
            "color": "danger",
        }])

    def notify(self, notification):
        unit = notification.unit
        message = "{0}: systemd unit {1} on {2} {3}".format(
            notification.type_text(),
            unit.name,
            notification.hostname,
            unit.state_change.status_text(),
        )
        attach = {
            "fallback": "{0}: {1} ({2})".format(
                message, unit.state.active, unit.state.sub),
            "color": self._color(notification.type),
            "fields": self._fields(notification),
        }
        self.debug("sending slack message with attachment: ")
        self.debug(str(attach))
        self._post(message, attachments=[attach])
        self.log("sent slack notification")

    def _fields(self, notification):
        fields = [
            {"title": "Hostname", "value": notification.hostname, "short": True},
            {"title": "Unit", "value": notification.unit.name, "short": True},
        ]
        changes = notification.unit.state_change.diff()
        for row in changes:
            v = row[-1]
            fields.append({"title": v.display_name, "value": v.value, "short": True})
        return fields

    def _color(self, ntype):
        return {
            "alert": "danger",
            "warning": "#FF9900",
            "info": "#0099CC",
        }.get(ntype, "good")

    def _post(self, text, attachments=None):
        payload = {"text": text}
        for key in ("channel", "username", "icon_emoji", "icon_url"):
            if self.options.get(key):
                payload[key] = self.options[key]
        if attachments:
            payload["attachments"] = attachments

        data = json.dumps(payload).encode("utf-8")
        req = Request(
            self.options["webhook_url"],
            data=data,
            headers={"Content-Type": "application/json"},
        )
        urlopen(req)
