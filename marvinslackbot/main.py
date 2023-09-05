import os
from datetime import datetime, timedelta
import time
import copy
import requests
from slack_bolt import App
from dotenv import load_dotenv
from marvinslackbot.utils.slack.connect import SlackConnection
from marvinslackbot.utils.slack.helpers import SlackHelpers
from marvinslackbot.utils.openai.endpoint import OpenAIHelpers

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

# Command to delete Marvin posted messages
@app.command("/marvin-delete")
def handle_delete_command(ack, respond, command):
    url = command['text']
    ack()
    if not url:
        respond('Please provide a message URL', response_type='ephemeral')
        return
    result = slack_helpers.extract_timestamp_and_channel(url)
    if not result:
        respond('Invalid message URL', response_type='ephemeral')
        return
    channel_id, timestamp = result
    message = slack_helpers.delete_message(channel_id, timestamp)
    respond(message, response_type='ephemeral')

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

# [TEMPORARY] Notion automation for a specific user
@app.command("/week-log")
def summarize_week(ack, respond, command):
    ack()
    init_message = "/week-log triggered. \n[S1] *Fetching data from Notion 'AI Integration Workspace' page.*\n"
    trigger_happy = slack_helpers.post_message(command["channel_id"], init_message)

    try:
        today = datetime.now().date()
        days_until_last_monday = today.weekday() + 7 if today.weekday() <= 3 else today.weekday()
        last_monday = today - timedelta(days=days_until_last_monday)
        days_until_friday = 4 - today.weekday() if today.weekday() <= 3 else (4 + 7) - today.weekday()
        last_friday = last_monday + timedelta(days=days_until_friday)
        if last_friday > today:
            last_monday -= timedelta(days=7)
            last_friday -= timedelta(days=7)

        db_query = f"https://api.notion.com/v1/databases/{os.environ.get('NOTION_DB_ID')}/query"
        page_query = "https://api.notion.com/v1/pages/"
        block_query = "https://api.notion.com/v1/blocks/"

        headers = {
            "Authorization": "Bearer " + os.environ.get('NOTION_INTEGRATION_SECRET'),
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

        data = {
            "filter": {
                "property": "Date", 
                "date": {
                    "on_or_after": str(last_monday),
                    "on_or_before": str(last_friday + timedelta(days=2)) # taking Sunday into account
                }
            } 
        }

        complete_notion_context = ""
        res = requests.post(db_query, json=data, headers=headers)
        tasks = res.json()['results']
        tasks.reverse()
        t_id = 1
        init_message += (f"[S2] *Found {str(len(tasks))} notes between {last_monday} to {last_friday}* \n")
        for task in tasks:
            current_page_query = page_query+task['id']+"/properties/title"
            res = requests.get(current_page_query, headers=headers)
            page = res.json()['results'][0]
            page_title = page['title']['plain_text']
            complete_notion_context += ("Note " + str(t_id) + "\n Title: " + page_title + "\n")

            SKIP_BLOCK = False
            if not SKIP_BLOCK:            
                current_page_block_children = block_query+task['id']+"/children"
                res = requests.get(current_page_block_children, headers=headers)
                blocks = res.json()['results']
                block_text = ""
                for block in blocks:
                    if "paragraph" in block:
                        rich_texts = block['paragraph']['rich_text']
                        for rich_text in rich_texts:
                            block_text += rich_text['plain_text'] + "\n"
                complete_notion_context += ("Content: " + block_text + "\n\n")
            init_message += (f"Processed Note *{str(t_id)}: {page_title}* (Created on {task['created_time']}) \n")
            _ = slack_helpers.message_update(command["channel_id"], trigger_happy['ts'], init_message)

            t_id += 1

        init_message += ("\n[S3] *Data fetch complete. Summarizing the data using GPT-4.*\n")
        _ = slack_helpers.message_update(command["channel_id"], trigger_happy['ts'], init_message)

        openai_system_message = {"role": "system", "content": """
You are my very useful personal assistant.
Following are some things to keep in mind:
1. You have been placed inside a Notion workspace to help me create note or tasks summary. Every week I report to my investors about my progress.
2. When I give you a list of task notes, you understand it and summarize it for me. Don't skip any note in the summary. 
3. Keep it less dreamy and more realistic.
4. Add additional information if you think it is necessary.
5. Since the investors see this report it needs to be professional, well formatted, easy to understand and also filled with details in a way that pleases them and more potential investors.
6. Use markdown formatting. Keep it in bullet points.
7. Never ask the user or me anything, since we can't respond to you. Its a one way request.
8. Never mention of the investors, because we don't want to be looking like pleading to them.
9. Keep it short, concise and to the point. Don't inlcude any unnecessary information. 
10. Your response is directly shared with the investors without moderation, so no need to say stuff like `here is a summary` or `this is a summary` or 'we are doing this and that'.
Remember your only task is to simple return a summarised report in bullets 
        """}

        openai_user_message = {"role": "user", "content": f"""
    Following are the details extracted from the 'AI Integration Workspace' notion database.
    ```
    {complete_notion_context}
    ```
    Summarize the above information, make bullet points, and add additional information if you think it is necessary.
        """}

        openai_message_array = [openai_system_message, openai_user_message]
        SKIP_GENERATION = False
        if not SKIP_GENERATION:
            init_openai = openai.return_openai()
            openai_response = init_openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=openai_message_array,
                temperature=0,
                stream=True  # this time, we set stream=True
            )

            complete_openai_response = ""
            update_interval = 2  # Set the update interval to 2 seconds
            last_update_time = time.time()

            slack_response_template = f"{init_message} [S4] *Summarised data:* \n"

            for chunk in openai_response:
                if 'content' in chunk['choices'][0]['delta']:
                    complete_openai_response += chunk['choices'][0]['delta']['content']

                current_time = time.time()
                if current_time - last_update_time >= update_interval:
                    slack_response_block = copy.deepcopy(slack_response_template)
                    slack_response_block += complete_openai_response
                    _ = slack_helpers.message_update(command["channel_id"], trigger_happy['ts'], slack_response_block)
                    last_update_time = current_time

            # After processing all chunks, make one final update if needed
            if complete_openai_response:
                slack_response_block = copy.deepcopy(slack_response_template)
                slack_response_block += complete_openai_response
                _ = slack_helpers.message_update(command["channel_id"], trigger_happy['ts'], slack_response_block)
    except Exception as e:
        print(e)
        _ = slack_helpers.message_update(command["channel_id"], trigger_happy['ts'], "Error occured: " + str(e) + "\n\nMessage will be auto deleted in 20 seconds.")
        time.sleep(20)
        _ = slack_helpers.delete_message(command["channel_id"], trigger_happy['ts'])


# Main entry point
if __name__ == "__main__":
    print("Script is running and monitoring for changes...")
    # Initialize SlackHelpers
    slack_helpers = SlackHelpers()
    slack_helpers.set_app(app)

    # Initialize OpenAIHelpers
    openai = OpenAIHelpers()
    openai.thinking_setup()

    # Initialize SlackConnection (should be last)
    slack_connect = SlackConnection(app)
    slack_connect.socket()
