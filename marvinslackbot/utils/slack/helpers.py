# Helper functions for Slack
import re
import os
from slack_bolt import App
from slack_sdk.errors import SlackApiError


class SlackHelpers:

    def __init__(self, init_self_app=False):
        self.app = None
        if (init_self_app):
            self.app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
        self.user_id_pattern = r"<@!?([A-Z0-9]+)>"

    # Sets the slack app
    def set_app(self, app):
        self.app = app

    # Replace user_id and username with real_name
    def replace_usernames(self, text):
        names = {id.group(): self.userid_to_realname(
            id.group()[2:-1]) for id in re.finditer(self.user_id_pattern, text)}
        return re.sub(self.user_id_pattern, lambda match: names[match.group()], text)

    # Convert user_id to Slack real_name
    def userid_to_realname(self, user_id):
        try:
            res = self.app.client.users_info(user=user_id)
            real_name = res['user']['real_name']
        except:
            real_name = user_id
        return real_name

    # fetch all messages in a thread
    def fetch_thread_messages(self, channel_id, thread_ts):
        try:
            response = self.app.client.conversations_replies(
                channel=channel_id, ts=thread_ts)
            messages = []
            for message in response["messages"]:
                messages.append({
                    "user_id": message["user"],
                    "user": self.userid_to_realname(message["user"]),
                    "message": self.replace_usernames(message["text"])
                })
            while response["has_more"]:
                response = self.app.client.conversations_replies(
                    channel=channel_id,
                    ts=thread_ts,
                    cursor=response["response_metadata"]["next_cursor"]
                )
                for message in response["messages"]:
                    messages.append({
                        "user_id": message["user"],
                        "user": self.userid_to_realname(message["user"]),
                        "message": self.replace_usernames(message["text"])
                    })
        except SlackApiError as e:
            print("Error fetching thread messages:", e)
            return []
        # returns a list of dicts with username and message
        return messages

    def get_bot_id(self):
        try:
            response = self.app.client.auth_test()
            return response["user_id"]
        except SlackApiError as e:
            return []

    def extract_timestamp_and_channel(self, url):
        regex = r'https://(.+)\.slack\.com/archives/(?P<channel>[A-Za-z0-9]+)/p(?P<timestamp>\d+)'
        match = re.match(regex, url)
        if match:
            channel = match.group('channel')
            timestamp = match.group('timestamp')
            timestamp = timestamp[:10] + '.' + timestamp[10:]
            return channel, timestamp

        return None

    def get_channel_name(self, channel_id):
        try:
            channel_info = self.app.client.conversations_info(channel=channel_id)
            channel_name = channel_info["channel"]["name"]
            return channel_name
        except SlackApiError as e:
            return channel_id

    def delete_message(self, channel_id, ts):
        try:
            response = self.app.client.chat_delete(channel=channel_id, ts=ts)
            if response['ok']:
                message = f'Message deleted successfully in #{self.get_channel_name(channel_id)}'
            else:
                message = f'Error deleting message: {response["error"]}'
        except SlackApiError as e:
            message = f'Error deleting message: {e}'
        return message

    def post_message(self, channel, text=None, blocks=None):
        return self.app.client.chat_postMessage(channel=channel, text=text, blocks=blocks)
    
    def message_update(self, channel, ts, text=None, blocks=None):
        return self.app.client.chat_update(channel=channel, ts=ts, text=text, blocks=blocks)
