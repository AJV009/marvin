import openai
import json
import os
from os.path import exists
import random
from marvin.utils.slack.helpers import SlackHelpers


class OpenAIHelpers:
    def __init__(self):
        openai.organization = os.environ.get("OPENAI_ORG_ID")
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        self.thiking_file = "marvin/data/thinking.txt"
        self.thinking_thoughts = []
        self.slack_helpers = SlackHelpers(init_self_app=True)
        self.messages = []
        with open("marvin/data/prompts.json", "r") as f:
            self.prompts = json.load(f)
        with open("marvin/data/flags.json", "r") as f:
            self.flags = json.load(f)

    # Prefetch thinking thoughts
    def thinking_setup(self):
        if (exists(self.thiking_file)):
            with open(self.thiking_file, "r") as f:
                lines = f.readlines()
                if len(lines) > 0:
                    self.thinking_thoughts = lines
        if (len(self.thinking_thoughts) <= 0):
            self.thinking_thoughts = ["I'm thinking..."]

    # Returns a random thinking thought
    def thinking(self):
        if (len(self.thinking_thoughts) > 0):
            return self.flags["init_thinking"] + random.choice(self.thinking_thoughts)

    # Sets the data for the chat
    def set_data(self, messages):
        self.messages = messages
        if (len(messages) > 0):
            return {"data_type": "thread", "moderation": False}
        else:
            return {"data_type": "single", "moderation": self.moderate(messages["message"])}

    # Moderates the text
    def moderate(self, text):
        moderation_response = self.openai.Moderation.create(input=text)
        if moderation_response["results"][0]["flagged"]:
            return self.flags["warning"]
        return False

    # Prepares the data for the chat API
    def data_prep(self):
        openai_messages = [
            {"role": "system", "content": self.prompts["system"]}]
        if (len(self.messages) > 0):
            bot_id = self.slack_helpers.get_bot_id()
            for message in self.messages:
                # check for bot messages
                if (message["user_id"] == bot_id):
                    # avoid messages with flags
                    if (not message["message"].startswith(tuple(self.flags.values()))):
                        openai_messages.append({
                            "role": "assistant",
                            "content": message["message"]
                        })
                else:
                    openai_messages.append({
                        "role": "user",
                        "content": message["user"] +': '+message["message"]
                    })
            self.messages = openai_messages

    # Sends the chat request to OpenAI
    def chat(self):
        self.data_prep()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
        )
        return response['choices'][0]['message']['content']
