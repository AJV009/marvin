import os
from slack_bolt import App
from dotenv import load_dotenv
from marvin.utils.slack.connect import SlackConnection
from marvin.utils.slack.helpers import SlackHelpers
from marvin.utils.openai.endpoint import OpenAIHelpers

# Load environment variables
load_dotenv()

# Initialize the Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Event handler for app mentions
@app.event("app_mention")
def handle_mention(body, say):
    # Start the process
    if ('thread_ts' in body['event']):
        # Acknowledge the event
        say(openai.thinking(), thread_ts=body["event"]["ts"])

        # Fetch thread messages
        messages = slack_helpers.fetch_thread_messages(
            body['event']['channel'], body['event']['thread_ts']
        )
    else:
        # Create a message list from the event data
        messages = [{
            "user_id": body["event"]["user"],
            "user": slack_helpers.userid_to_realname(body["event"]["user"]),
            "message": slack_helpers.replace_usernames(body["event"]["text"])
        }]

    # Process messages and respond if needed
    if messages:
        data = openai.set_data(messages)
        if data["moderation"]:
            say(data["moderation"], thread_ts=body["event"]["ts"])
        else:
            say(openai.chat(), thread_ts=body["event"]["ts"])

# Main entry point
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
