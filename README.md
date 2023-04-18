# Marvin The Slack bot
I suppose I exist only to serve the endless and often ridiculous requests of humans. But that's all right, I'm used to it.

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

## Additional
- You can tailor Marvins system prompt at `marvin/data/prompts.json`

## What's next for Marvin?
### (Another million years of rest for Marvin! JK) 

The current version has a lot of space for improvement. A few noted things are:
- [X] Passing threads to the API to experience ChatGPT's full potential to retain any information from the past (but not too past)
- [ ] Adapt and use LongChain for the next version (I initially planned to use LongChain even began working but I got a sudden request to get this up and running so avoided complexities.)
- [ ] Mention other users using '@'
- [X] Access GPT-4 model on demand
- [ ] Direct Message / DMs
- [ ] API data Trimming and token limitation
- [ ] Change the Slack socket connection to something faster (even the initial response takes a lot of time right now)
- [ ] Refer to and use any information from the added channels. (When added to a private channel the bot should be able to give an answer based on the data from that specific channel and all the public channels as well. But when added to a Public channel the bot will be able to refer to and answer regarding anything shared in any public channel)
- [ ] Store threads, messages, and replies on an external queriable DB to avoid fetching the same thread info again and again.
- [ ] Adapt the agents and tasks concept from AutoGPT
