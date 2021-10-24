import os
import discord
from discord.ext import commands
from discord.commands import Option
import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PREFIX = "py "
SERVER_ID = [896214560816656404]

CODEBLOCK_EX = "https://cdn.discordapp.com/attachments/689908647807156229/901671041041063966/python_codeblock.png"
client = commands.Bot(command_prefix=PREFIX, activity=discord.Game(name=f"/help"))
client.remove_command("help")

async def pyify(code):
    return f"```py\n{code}```"


async def depyify(code):
    return code.replace("```py\n", "").replace("```", "")


async def find_between(s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


@client.event
async def on_ready():
    print("Bot has successfully logged in as: {}".format(client.user))
    print("Bot ID: {}\n".format(client.user.id))
    global help_embed

    help_embed = discord.Embed(
        title="List of commands",
        color=discord.Colour.from_rgb(225, 224, 120)
    )
    help_embed.add_field(
        name="**/ask `question:`**",
        value="Ask any python related question.\n\n" \
              "Ex. `/ask question: How do I use regex?`",
        inline=False
    )
    help_embed.add_field(
        name="**/code `instructions:`**",
        value="*pyBot* will code following your instructions\n\n" \
              "Ex. `/code instructions: \n1. import random\n2. Print a random number between 1 and 100`",
        inline=False
    )
    help_embed.add_field(
        name="**explain**",
        value="*pyBot* will explain the piece of code you prompt\n\n" \
              f"`Use: Right click on a message with a code block PC *support for now* > applications > explain`",
        inline=False
    )
    help_embed.add_field(
        name="**fix**",
        value="*pyBot* will *fix* the piece of code you prompt\n\n" \
              f"`Use: Right click on a message with a code block PC *support for now* > applications > explain`",
        inline=False
    )
    help_embed.set_thumbnail(
        url=CODEBLOCK_EX
    )
    help_embed.set_footer(
        text="Warning: this bot is still being developed and you may encounter errors"
    )


# SlashCommands


@client.slash_command(description="Provides a DM with some info & examples for commands", guild_ids=SERVER_ID)
async def help(ctx):
    emoji = "\u2705"
    await ctx.respond(emoji)
    await ctx.author.send(embed=help_embed)


@client.slash_command(description="Codes for you using the instructions you provide (python)", guild_ids=SERVER_ID)
async def code(ctx, *, instructions):
    print(ctx.author)
    await ctx.defer()
    code = OpenAI.code(instructions)
    code = await pyify(code)
    await ctx.respond(f"**You can do that by following the code below:**\n{code}")


@client.slash_command(description="Ask for any computer science/programming question", guild_ids=SERVER_ID)
async def ask(ctx, *, question):
    print(ctx.author)
    await ctx.defer()
    answer = OpenAI.ask(question)
    await ctx.respond(f"{answer}")

# User commands


@client.message_command(guild_ids=SERVER_ID, name ="explain")
async def explain(ctx, message:discord.Message):
    code = str(message.content)
    code = await find_between(code, "```py", "```")
    if code == "":
        embed = discord.Embed(
            title="There is no code in your message!",
            color=discord.Color.red(),
            description="Remember to format to python codeblock as seen in thumbnail"
        )
        embed.set_thumbnail(url=CODEBLOCK_EX)
        await ctx.respond(embed=embed)
    else:
        await ctx.defer()
        explanation = OpenAI.explain(code)
        await ctx.respond(f"**Here is what the code is doing:**\n`1.{explanation}`")


@client.message_command(guild_ids=SERVER_ID, name ="fix")
async def fix(ctx, message:discord.Message):
    buggy_code = str(message.content)
    buggy_code = await find_between(buggy_code, "```py", "```")
    if buggy_code == "":
        embed = discord.Embed(
            title="There is no code in your message!",
            color=discord.Color.red(),
            description="Remember to format to python codeblock as seen in thumbnail"
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/689908647807156229/901671041041063966/python_codeblock.png")
        await ctx.respond(embed=embed)
    else:
        await ctx.defer()
        fixed_code = OpenAI.fix(buggy_code)
        if fixed_code.replace("\n", "") == buggy_code.replace("\n", ""):
            await ctx.respond(f"**I think your code looks fine**")
        else:
            fixed_code = await pyify(fixed_code)
            await ctx.respond(f"**Maybe try using this code**\n{fixed_code}")

if __name__ == "__main__":
    client.run(BOT_TOKEN)
