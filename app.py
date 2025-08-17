import os
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
    ActivityHandler,
)
from botbuilder.schema import Activity
import traceback

# -----------------------------
# Adapter settings from env vars
# -----------------------------
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
print(f"DEBUG: MicrosoftAppId={APP_ID}")
print(f"DEBUG: MicrosoftAppPassword={'SET' if APP_PASSWORD else 'NOT SET'}")

adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# -----------------------------
# Error handler
# -----------------------------
async def on_error(context: TurnContext, error: Exception):
    print(f"ERROR in turn: {error}")
    traceback.print_exc()
    await context.send_activity("Oops! Something went wrong.")

adapter.on_turn_error = on_error

# -----------------------------
# Echo bot
# -----------------------------
class EchoBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        print(f"DEBUG: Received message: {turn_context.activity.text}")
        await turn_context.send_activity(f"You said: {turn_context.activity.text}")

bot = EchoBot()

# -----------------------------
# AIOHTTP web server
# -----------------------------
async def messages(req):
    try:
        body = await req.json()
        print(f"DEBUG: Raw request body: {body}")
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        print(f"DEBUG: Authorization header: {auth_header}")
        # Process activity
        await adapter.process_activity(activity, auth_header, bot.on_turn)
        return web.Response(status=200)
    except Exception as e:
        print(f"Exception in /api/messages: {e}")
        traceback.print_exc()
        return web.Response(status=500, text=str(e))

app = web.Application()
app.router.add_post("/api/messages", messages)
app.router.add_get("/", lambda req: web.Response(text="Echo bot is running"))

# Handle favicon requests to avoid 500 errors in browser
async def favicon(req):
    return web.Response(status=204)  # 204 = No Content

app.router.add_get("/favicon.ico", favicon)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    print(f"DEBUG: Starting web server on port {port}")
    web.run_app(app, port=port)
