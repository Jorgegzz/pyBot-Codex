import os
import discord
from discord.ext import commands
import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PREFIX = "py "
client = commands.Bot(command_prefix=PREFIX, activity=discord.Game(name=f"/help"))
client.remove_command("help")
serverID = [896214560816656404]


async def pyify(code):
    return f"```py\n{code}```"


async def depyify(code):
    return code.replace("```py\n", "").replace("```", "")


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
        name="**/ ask**",
        value="Ask any python related question.\n" \
              "Ex. `/ask question: How do I use regex?`",
        inline=False
    )
    help_embed.add_field(
        name="**/ code**",
        value="pyBot will code following your instructions\n" \
              "Ex. `/code instructions: \n1. import random\n2. Print a random number between 1 and 100`",
        inline=False
    )
    explain_example_code = \
        r"""word = input()
    output = ""
    first_vowel = True
    for char in word:
    if char in "aeiou" and first_vowel:
        char *= 10
        first_vowel = False
    output += char
    
    print(output)
    """
    explain_example_code = await pyify(explain_example_code)
    help_embed.add_field(
        name="**py explain**",
        value="pyBot will explain the piece of code you ask\n" \
              f"Ex.`py explain code:` {explain_example_code}",
        inline=False
    )
    help_embed.set_footer(
        text="Warning: this bot is still being developed and you may encounter errors"
    )


# NormalCommands


@client.command()
async def explain(ctx, *, code):
    print(ctx.author)
    with ctx.typing():
        code_dp = await depyify(code)
        explanation = OpenAI.explain(code_dp)
        await ctx.send(f"**Here is what the code above is doing:**\n1.`{explanation}`")


# SlashCommands


@client.slash_command(description="Provides a DM with some info & examples for commands", guild_ids=serverID)
async def help(ctx):
    emoji = "\u2705"
    await ctx.respond(emoji)
    await ctx.author.send(embed=help_embed)


@client.slash_command(description="Codes for you using the instructions you provide (python)", guild_ids=serverID)
async def code(ctx, *, instructions):
    print(ctx.author)
    await ctx.defer()
    code = OpenAI.code(instructions)
    code = await pyify(code)
    await ctx.respond(f"**You can do that by following the code below:**\n{code}")


@client.slash_command(description="Ask for any computer science/programming question", guild_ids=serverID)
async def ask(ctx, *, question):
    print(ctx.author)
    await ctx.defer()
    answer = OpenAI.ask(question)
    await ctx.respond(f"{answer}")


if __name__ == "__main__":
    client.run(BOT_TOKEN)
