from slack_bolt.adapter.socket_mode import SocketModeHandler
import os


class SlackConnection:
    def __init__(self, app):
        self.app = app

    def socket(self):
        handler = SocketModeHandler(self.app, os.environ.get("SLACK_APP_TOKEN"))
        handler.start()

