import os
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext, ActivityHandler

# 👇 Pulling credentials from environment variables
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

# 👇 Bot Framework adapter needs these to authenticate
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# Error handler
async def on_error(context: TurnContext, error: Exception):
    print(f"Error: {error}")
    await context.send_activity("Oops! Something went wrong.")
adapter.on_turn_error = on_error

# Echo bot logic
class EchoBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        await turn_context.send_activity(f"You said: {turn_context.activity.text}")

bot = EchoBot()

# Messages endpoint
async def messages(req):
    body = await req.json()
    response = web.Response()
    await adapter.process_activity(body, req.headers, bot.on_turn)  # 👈 Uses App ID / Password for auth
    return response

app = web.Application()
app.router.add_post("/api/messages", messages)
