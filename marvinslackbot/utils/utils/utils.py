import json

# formatted print of the Python JSON object
def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

# print python object
def oprint(obj):
    print(dir(obj))

# Extract the model from the messages
def extract_model(messages):
    for message in reversed(messages):
        if "[MARVIN-GPT4]" in message["message"]:
            return "gpt-4"
    return "gpt-3.5-turbo"
