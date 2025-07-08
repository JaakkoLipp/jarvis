# bot.py
"""
DISCORD ↔ OLLAMA  —  context-aware assistant

Quick start
───────────
1.  pip install -U discord.py aiohttp python-dotenv
2.  Put secrets in .env  (same folder):
        DISCORD_TOKEN=YOUR_BOT_TOKEN
        OLLAMA_MODEL=llama3
        OLLAMA_URL=http://localhost:11434
3.  Run:  python bot.py
"""

import os, textwrap, asyncio, aiohttp
from dotenv import load_dotenv
import discord
from discord.ext import commands

# ─── environment ───────────────────────────────────────────────────────────
load_dotenv()
TOKEN        = os.environ["DISCORD_TOKEN"]
OLLAMA_MODEL  = os.getenv("OLLAMA_MODEL", "phi4-mini")
OLLAMA_URL    = os.getenv("OLLAMA_URL",  "http://65.21.183.21:2556")

# ─── global HTTP session ───────────────────────────────────────────────────
session: aiohttp.ClientSession | None = None

async def ask_ollama(user_prompt: str,
                     context: str | None = None,
                     model: str = OLLAMA_MODEL) -> str:
    """Send user_prompt (+ optional context) to Ollama and return the reply."""
    assert session and not session.closed, "HTTP session not ready"

    # Embed context above the actual prompt if we have any
    prompt = (f"Previous message:\n{context}\n\nUser:\n{user_prompt}"
              if context else user_prompt)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    async with session.post(f"{OLLAMA_URL}/api/generate",
                            json=payload, timeout=120) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return data.get("response", "").strip()

# ─── discord setup ─────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True       # enable in Dev Portal too

bot = commands.Bot(
    command_prefix=commands.when_mentioned,  # “@BotName …” is the prefix
    case_insensitive=True,
    intents=intents,
    help_command=None,
)

# ─── lifecycle events ──────────────────────────────────────────────────────
@bot.event
async def on_ready():
    global session
    if session is None or session.closed:          # start connection pool once
        session = aiohttp.ClientSession()
    print(f"✅ Logged in as {bot.user} (ID {bot.user.id})")

@bot.event
async def on_disconnect():
    if session and not session.closed:
        await session.close()

# ─── main listener ─────────────────────────────────────────────────────────
@bot.event
async def on_message(message: discord.Message):
    """Catch mention, optionally gather reply context, ask Ollama, respond."""
    if message.author.bot:
        return

    # 1  Is the bot pinged?
    ping_forms = (bot.user.mention, f"<@!{bot.user.id}>")
    if not any(message.content.startswith(p) for p in ping_forms):
        return await bot.process_commands(message)

    # 2  Extract text after the mention
    for p in ping_forms:
        if message.content.startswith(p):
            user_text = message.content[len(p):].lstrip()
            print(f"👤 User text: {user_text[:50]}…")
            break
    if not user_text:            # nothing but the mention → ignore
        return

    # 3  If this message replies to another, fetch that message’s content
    context_txt = None
    if message.reference and message.reference.message_id:
        ref = message.reference
        print("", f"🔗 Replying to message ID {ref.message_id} in channel {ref.channel_id}")
        ref_msg = ref.resolved                       # cached?
        if ref_msg is None:
            try:
                ref_msg = await message.channel.fetch_message(ref.message_id)
            except (discord.NotFound, discord.Forbidden):
                ref_msg = None
        if ref_msg and ref_msg.content:
            context_txt = "User replying to another message: "+ref_msg.content.strip()+". With the following: "
            print(f"🔗 Context: {context_txt[:50]}…")

    # 4  Ask Ollama
    async with message.channel.typing():
        try:
            if context_txt is None:
                context_txt = ""
            user_prompt = "System: You are Jarvis, a helpful assistant Discord bot. " \
            "Your response should be as short as possible (!if user asks to summarize the answer should be very short, MAXIMUM 10 words!). " \
            "The user's request: "+context_txt+user_text
            print(f"🤖 Asking Ollama: {user_prompt[:200]}…")
            answer = await ask_ollama(user_prompt)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            return await message.reply(f"⚠️ LLM error: {e}")

    # 5  Discord’s hard limit is 2 000 characters
    for chunk in textwrap.wrap(answer, width=2000, replace_whitespace=False):
        await message.reply(chunk)

# ─── sample command (still works) ───────────────────────────────────────────
@bot.command()
async def ping(ctx: commands.Context):
    """@BotName ping → Pong!"""
    await ctx.reply("🏓 Pong!")

# ─── go ─────────────────────────────────────────────────────────────────────
bot.run(TOKEN)
