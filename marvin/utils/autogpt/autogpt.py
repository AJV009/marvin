from marvin.utils.autogpt.web_helper import WebHelper

class AutoGPT:

    def __init__(self, messages):
        self.altered_messages = []
        self.contructed_user_prompt = None
        self.webhelper = WebHelper()
        self.messages = self.process(messages)

    def process(self, messages):

        # extract url data from messages
        for i, message in enumerate(messages):
            if message["role"] == "user":
                url_data = self.webhelper.extract_url_data_from_text(message["content"])
                if url_data:
                    for data in url_data:
                        # insert url_data just after the message
                        messages.insert(i + 1, data['prompt'])

        return messages

    def get_messages(self):
        return self.messages

    def get_model(self):
        return "gpt-4"
