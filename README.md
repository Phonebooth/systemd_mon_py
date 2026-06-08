# systemd_mon_py

Monitor systemd units and trigger alerts for failed states. A Python 3.5+ port of
[systemd_mon](https://github.com/Phonebooth/systemd_mon/).

The tool runs as a daemon, using DBus to receive notifications of changes to systemd
services. If a service enters a failed state, or returns from a failed state to an active
state, notifications are triggered. There is no polling — systemd_mon sits in the
background using minimal resources.

## Requirements

* Linux with systemd (v204+)
* Python 3.5+
* System DBus packages: `python3-dbus` and `python3-gi`
* PyYAML (pip dependency, installed automatically)

### Install system packages

```
# Debian / Ubuntu
sudo apt install python3-dbus python3-gi

# Fedora / RHEL
sudo dnf install python3-dbus python3-gobject
```

## Installation

```
pip install systemd-mon-py
```

Or from source:

```
pip install .
```

## Usage

Create a YAML configuration file:

```yaml
---
verbose: true   # optional, default false
notifiers:
  slack:
    webhook_url: https://hooks.slack.com/services/TOKEN/TOKEN/TOKEN
    channel: "#alerts"
    username: systemd-mon
    icon_emoji: ":computer:"
  email:
    to: "ops@example.com"
    from: "systemdmon@myserver.com"
    smtp:
      address: smtp.gmail.com
      port: 587
      domain: example.com
      user_name: "user@example.com"
      password: "supersecret"
      authentication: plain
      enable_starttls_auto: true
units:
  - nginx.service
  - postgresql.service
  - myapp.service
```

Save it (e.g. `/etc/systemd_mon.yml`), then run:

```
systemd_mon /etc/systemd_mon.yml
```

Or equivalently:

```
python -m systemd_mon /etc/systemd_mon.yml
```

### Running as a systemd service

```ini
[Unit]
Description=SystemdMon
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/systemd_mon /etc/systemd_mon.yml
StandardOutput=journal
StandardError=journal
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Behaviour

Systemd reports state changes in fine detail (e.g. `activating -> active -> running`),
often all within a second. systemd_mon queues up states until it reaches one that is
worth notifying about, then fires a notification summarising the full history.

Recognised status summaries: **recovered**, **automatically restarted**, **restarted**,
**reloaded**, **still failed**, **failed**, **started**.

systemd_mon also sends a notification when it starts and attempts to send one when it
stops. As with the original, a SIGKILL or network failure may prevent the stop notification.

## Notifiers

### Slack

Posts a message with a colour-coded attachment to a Slack incoming webhook.

| Option | Required | Description |
|--------|----------|-------------|
| `webhook_url` | yes | Incoming webhook URL |
| `channel` | no | Override channel |
| `username` | no | Bot display name |
| `icon_emoji` | no | Bot icon emoji |
| `icon_url` | no | Bot icon URL |

### Email

Sends plain-text email via SMTP using the Python standard library.

| Option | Required | Description |
|--------|----------|-------------|
| `to` | yes | Recipient address |
| `from` | no | Sender address |
| `smtp.address` | no | SMTP host (default: localhost) |
| `smtp.port` | no | SMTP port (default: 25) |
| `smtp.user_name` | no | SMTP login username |
| `smtp.password` | no | SMTP login password |
| `smtp.domain` | no | HELO domain |
| `smtp.enable_starttls_auto` | no | Enable STARTTLS |

## Development

Run the test suite (no DBus required):

```
python -m unittest discover -s tests
```

## Differences from the Ruby original

* Hipchat notifier not included (service discontinued 2019).
* Email notifier uses `smtplib` (stdlib) instead of the `mail` gem.
* Slack notifier uses `urllib` (stdlib) instead of `slack-notifier`.
* GLib main loop runs in the main thread; callback consumer runs in a daemon thread.
* SIGTERM/SIGINT trigger a graceful shutdown and the stop notification.
