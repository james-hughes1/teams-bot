import os
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext, ActivityHandler

# Adapter settings from environment variables
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# Error handler
async def on_error(context: TurnContext, error: Exception):
    print(f"Error: {error}")
    await context.send_activity("Oops! Something went wrong.")
adapter.on_turn_error = on_error

# Echo bot
class EchoBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        await turn_context.send_activity(f"You said: {turn_context.activity.text}")

bot = EchoBot()

# AIOHTTP web server
async def messages(req):
    body = await req.json()
    response = web.Response()
    await adapter.process_activity(body, req.headers, bot.on_turn)
    return response

app = web.Application()
app.router.add_post("/api/messages", messages)
app.router.add_get("/", lambda req: web.Response(text="Echo bot is running"))

if __name__ == "__main__":
    web.run_app(app, port=int(os.environ.get("PORT", 3978)))
