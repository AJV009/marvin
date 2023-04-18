from slack_bolt import App
from marvin.utils.slack.connect import SlackConnection
from marvin.utils.slack.helpers import SlackHelpers
from marvin.utils.openai.endpoint import OpenAIHelpers
from marvin.utils.utils import utils as marv_utils
from dotenv import load_dotenv
import os
load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.event("app_mention")
def handle_mention(body, say):
    # Start the process
    if ('thread_ts' in body['event']):
        # Acknowledge the event
        say(openai.thinking(), thread_ts=body["event"]["ts"])
        messages = slack_helpers.fetch_thread_messages(
            body['event']['channel'], body['event']['thread_ts'])
    else:
        messages = [{
            "user_id": body["event"]["user"],
            "user": slack_helpers.userid_to_realname(body["event"]["user"]),
            "message": slack_helpers.replace_usernames(body["event"]["text"])
        }]

    if (messages):
        data = openai.set_data(messages)
        if (data["moderation"]):
            say(data["moderation"], thread_ts=body["event"]["ts"])
        else:
            model = marv_utils.extract_model(messages)
            say(openai.chat(model), thread_ts=body["event"]["ts"])

if __name__ == "__main__":
    # Initialize SlackHelpers
    slack_helpers = SlackHelpers()
    slack_helpers.set_app(app)
    # Initialize OpenAIHelpers
    openai = OpenAIHelpers()
    openai.thinking_setup()
    # Initialize SlackConnection (should be last)
    slack_connect = SlackConnection(app)
    slack_connect.socket()
