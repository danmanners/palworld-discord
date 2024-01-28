# Native Python Imports
import os
import subprocess

# Handle ctrl+c as well as SIGTERM
import signal
import sys

# Third Party Imports
import discord
from discord.ext import commands
from dotenv import load_dotenv


# Handle ctrl+c as well as SIGTERM
def signal_handler(sig, frame):
    print("Exiting...")
    sys.exit(0)


# Handle ctrl+c as well as SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# Get the `TOKEN` from the `.env` file
load_dotenv()

# Get the `TOKEN` from the `.env` file
TOKEN: str = os.environ.get("DISCORD_TOKEN")
RCON_HOST: str = os.environ.get("RCON_HOST")
RCON_PORT: int = os.environ.get("RCON_PORT")
RCON_PASSWORD: str = os.environ.get("RCON_PASSWORD")
RESTART_TIMEOUT = os.environ.get("RESTART_TIMEOUT") or 60.0
RESTART_TIMEOUT = float(RESTART_TIMEOUT)

# Check if any of the environment variables are not set
for var in [TOKEN, RCON_HOST, RCON_PORT, RCON_PASSWORD]:
    if var is None:
        # Print the actual variable name and tell the user to set it
        print(f"Please set all environment variables!")
        # Output to the user which variables must be set
        print(f"Required variables: DISCORD_TOKEN, RCON_HOST, RCON_PORT, RCON_PASSWORD")
        sys.exit(1)

# Set up the intents of the bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Define the bot commands
bot = commands.Bot(command_prefix="!", intents=intents)


# If a user sends the message "!memory" in the #palworld-bot-test channel,
# the bot will react with a thinking emoji, run a command, then react with a checkmark emoji
@bot.command(name="memory")
async def memory(ctx):
    await ctx.message.add_reaction("🤔")
    await ctx.send("Checking memory usage...")
    await ctx.send(
        "```\n"
        + subprocess.check_output("free -ht", shell=True).decode("utf-8")
        + "\n```"
    )
    await ctx.message.add_reaction("✅")
    await ctx.message.remove_reaction("🤔", bot.user)


# If a user sends the message "!save" in the #palworld-bot-test channel,
# the bot will react with a thinking emoji, run a command, then react with a checkmark emoji
@bot.command(name="save")
async def save(ctx):
    await ctx.message.add_reaction("🤔")
    await ctx.send("Saving world...")
    await ctx.send(
        "```\n"
        + subprocess.check_output(
            f"rcon -a {RCON_HOST}:{RCON_PORT} -p {RCON_PASSWORD} Save", shell=True
        ).decode("utf-8")
        + "\n```"
    )
    await ctx.message.add_reaction("✅")
    await ctx.message.remove_reaction("🤔", bot.user)


# If a user sends the message "!upgrade" in the #palworld-bot-test channel,
# the bot will react with a thinking emoji, run a command, then react with a checkmark emoji
@bot.command(name="upgrade")
async def upgrade(ctx):
    await ctx.message.add_reaction("🤔")
    await ctx.send("Upgrading server...")
    await ctx.send(
        "```\n"
        + subprocess.check_output(
            "steamcmd +login anonymous +app_update 2394010 validate +quit", shell=True
        ).decode("utf-8")
        + "\n```"
    )
    await ctx.message.add_reaction("✅")
    await ctx.message.remove_reaction("🤔", bot.user)


# If a user sends the message "!restart" in the #palworld-bot-test channel,
# the bot will react with a thinking emoji, run a command, then react with a checkmark emoji
@bot.command(name="restart")
async def restart(ctx):
    def restart_message(ctx):
        return f"Are you sure you want to restart the server, {ctx.message.author.mention}? Please react with ✅ to confirm in the next {RESTART_TIMEOUT} seconds."

    await ctx.message.add_reaction("🤔")
    # Confirm that the user wants to restart the server
    # Send a confirmation message, wait for a checkmark reaction on the message the bot sent, then continue
    restart_check = await ctx.send(restart_message(ctx))
    await restart_check.add_reaction("✅")
    # Start a timer for the value of RESTART_TIMEOUT; if the user reacts with a checkmark, continue
    try:
        reaction, user = await bot.wait_for(
            "reaction_add",
            timeout=RESTART_TIMEOUT,
            check=lambda reaction, user: user == ctx.author
            and str(reaction.emoji) == "✅",
        )
        # If the user reacts with a checkmark, continue
        await ctx.send("Restarting server...")
        await ctx.send(
            "```\n"
            + subprocess.check_output(
                f"rcon -a {RCON_HOST}:{RCON_PORT} -p {RCON_PASSWORD} Save && sudo systemctl restart palworld",
                shell=True,
            ).decode("utf-8")
            + "\n```"
        )
        await ctx.message.add_reaction("✅")
    # If the user does not react with a checkmark, cancel the restart
    except Exception as e:
        if type(e).__name__ == "CalledProcessError":
            error = str(e).replace(RCON_PASSWORD, "****")
            await restart_check.edit(
                content=f"{restart_message(ctx)}\n**SOMETHING WENT HORRIBLY WRONG!!**\n```bash\n{error}\n```"
            )
        else:
            await restart_check.edit(
                content=f"{restart_message(ctx)}\n**Restart Timed Out and Cancelled!**"
            )
        await restart_check.remove_reaction("✅", bot.user)
        await ctx.message.add_reaction("🚫")

    await ctx.message.remove_reaction("🤔", bot.user)


# If the user sends a command that is not recognized, the bot should do nothing and not error out
@bot.event
async def on_command_error(ctx, error):
    pass


# Run the bot
bot.run(TOKEN)
