import json

# formatted print of the Python JSON object
def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

# print python object
def oprint(obj):
    print(dir(obj))

