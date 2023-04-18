# Marvin The ChatGPT Slack bot
I suppose I exist only to serve the endless and often ridiculous requests of humans. But that's all right, I'm used to it.
(A simple slack bot that uses OpenAI Chat completion API)

## Setup
1. Clone this project
2. The following commands to install the requirements
```bash
cd marvin
pip install -r requirements.txt
```
3. Create a Slack app using the `manifest.json` file
4. Copy `sample.env` to `.env`. And replace the dummy values with actual tokens.
```env
SLACK_BOT_TOKEN=xoxb-<your-bot-token>
SLACK_APP_TOKEN=xapp-<your-app-token>
OPENAI_ORG_ID=org-<your-openai-org-id>
OPENAI_API_KEY=sk-<your-openai-api-key>
```
5. Once you feel you are ready, just run `python -m marvin.main`

## Note
- You can tailor Marvins system prompt at `marvin/data/prompts.json`
- Whenever you mention @ marvin, it will reply. (It should be added to the channel)
- What's with the deal of double messages in thread? So my slack bot is currently extremely slow, its not only my network problem but the whole socket based connection thing and multiple unnecessary loops. So I have added some (>99,<101) dummy responses in a file in the project dir itself, it replies with :thinking_face::brain::zap: in a thread to give you an assurance that the event has been triggered, acknowledged and you have to wait for the response. (But these hard coded responses from the bot is ignored when passing all the thread data to chat api)
- By default it uses the 'gpt-3.5-turbo' model, but with a flag you can use GPT-4 as well. But nah I won't tell you how to, just figure it out. Read the code or checkout the sample below...

## What's next for Marvin?
### (Another million years of rest for Marvin! JK) 

The current version has a lot of space for improvements. A few noted things are:
- [X] Passing threads to the API to experience ChatGPT's full potential to retain any information from the past (but not too past)
- [ ] Adapt and use LongChain for the next version (I initially planned to use LongChain even began working but I got a sudden request to get this up and running so avoided complexities.)
- [ ] Mention other users using '@'
- [ ] Optimize the system prompt for Marvin
- [X] Access GPT-4 model on demand
- [ ] Find a better way to 
- [ ] Direct Message / DMs
- [ ] Clean up the code, remove unnecessary loops on the data, change the data manuplation tooling used for a faster approach
- [ ] Data Trimming and token limitation
- [ ] Change the Slack socket connection to something faster (even the initial response takes a lot of time right now)
- [ ] Refer to and use any information from the added channels. (When added to a private channel the bot should be able to give an answer based on the data from that specific channel and all the public channels as well. But when added to a Public channel the bot will be able to refer to and answer regarding anything shared in any public channel)
- [ ] Store threads, messages, and replies on an external queriable DB to avoid fetching the same thread info again and again.
- [ ] Adapt the agents and tasks concept from AutoGPT

## Examples
![image](https://user-images.githubusercontent.com/42465795/232779792-557e594c-67a4-4e24-9f53-afa65b4a94ea.png)
![image](https://user-images.githubusercontent.com/42465795/232780084-380cef27-4fcf-4d47-a806-186123b24d16.png)
![image](https://user-images.githubusercontent.com/42465795/232780422-21809957-0b3d-4fc2-a039-48f4615d3be0.png)
