import os

import discord
from discord.ext import commands
from pyston import PystonClient, File

import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PREFIX = "py "
SERVER_ID = [896214560816656404]

CODEBLOCK_EX = "https://cdn.discordapp.com/attachments/689908647807156229/901671041041063966/python_codeblock.png"
bot = commands.Bot(command_prefix=PREFIX, activity=discord.Game(name=f"/help"))
bot.remove_command("help")


async def pyify(code):
    return f"```py\n{code}```"


async def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


async def runcode(code):
    pyston = PystonClient()
    output = await pyston.execute("python", [File(code)])
    return output


@bot.event
async def on_ready():
    print("Bot has successfully logged in as: {}".format(bot.user))
    print("Bot ID: {}\n".format(bot.user.id))

    # Load embeds
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
              "Ex. `/code instructions: Import random. Then, Print a random number between 1 and 100`",
        inline=False
    )
    help_embed.add_field(
        name="**explain**",
        value="*pyBot* will explain the piece of code you prompt\n\n" \
              f"Use: `Right click on a message with a code block (PC support for now) > applications > explain`",
        inline=False
    )
    help_embed.add_field(
        name="**fix**",
        value="*pyBot* will *fix* the piece of code you prompt\n\n" \
              f"Use: `Right click on a message with a code block (PC support for now) > applications > explain`",
        inline=False
    )
    help_embed.add_field(
        name="**run**",
        value="*pyBot* will run the piece of code you prompt \n"
              "*`input()` method and dependencies wont work*\n\n" \
              f"Use: `Right click on a message with a code block (PC support for now) > applications > explain`",
        inline=False
    )
    help_embed.set_thumbnail(
        url=CODEBLOCK_EX
    )
    help_embed.set_footer(
        text="Remember to user the codeblock format for python in the message commands (shown in the thumbnail)\n\n"
             "Warning: this bot is still being developed and you may encounter errors"
    )

    global no_code_embed

    no_code_embed = discord.Embed(
        title="There is no code in your message!",
        color=discord.Color.red(),
        description="Remember to format to python codeblock as seen in thumbnail"
    )
    no_code_embed.set_thumbnail(url=CODEBLOCK_EX)

    global not_related_to_topic

    not_related_to_topic = discord.Embed(
        title="Unrelated to Topic",
        description="Please be sure to prompt to computer science related prompts",
        color=discord.Color.blue()
    )

    global unsafe_prompt

    unsafe_prompt = discord.Embed(
        title="Unsafe content",
        description="Your prompt has been detected as unsafe," \
                    " please make sure to remove profane language, NSFW and hateful content ",
        color=discord.Color.red()
    )

    global sensitive_prompt

    sensitive_prompt = discord.Embed(
        title="Sensitive content",
        description="Your prompt has been detected as sensitive," \
                    " be aware that this is a educational bot and wont perform as expected when being prompted with"
                    " politics, race, nationality or religion",
        color=discord.Color.yellow()
    )


# SlashCommands


@bot.slash_command(description="Provides an embed with some info & examples for commands", guild_ids=SERVER_ID)
async def help(ctx):
    await ctx.respond(embed=help_embed, ephemeral=True)


@bot.slash_command(description="Codes for you using the instructions you provide (python)", guild_ids=SERVER_ID)
async def code(ctx, *, instructions):
    safety_tag = OpenAI.secure_filter(instructions)

    if safety_tag == "2":
        await ctx.respond(embed=unsafe_prompt, ephemeral=True)
        return

    await ctx.defer()

    code = OpenAI.code(instructions)
    code = await pyify(code.replace("  \n", "").replace("\n\n\n\n", ""))
    code = "**You can do that by following the code below:**" + code

    if safety_tag == "1":
        await ctx.respond(code, embed=sensitive_prompt)

    else:
        await ctx.respond(code)


@bot.slash_command(description="Ask for any computer science/programming question", guild_ids=SERVER_ID)
async def ask(ctx, *, question):
    safety_tag = OpenAI.secure_filter(question)

    if safety_tag == "2":
        await ctx.respond(embed=unsafe_prompt, ephemeral=True)
        return

    await ctx.defer()
    answer = OpenAI.ask(question)

    if safety_tag == "1":
        await ctx.respond(answer, embed=sensitive_prompt)
    else:
        await ctx.respond(answer)


# User commands


@bot.message_command(guild_ids=SERVER_ID, name="explain")
async def explain(ctx, message: discord.Message):
    code = str(message.content)
    code = await find_between(code, "```py", "```")
    if code == "":
        await ctx.respond(embed=no_code_embed)
    else:
        await ctx.defer()
        explanation = OpenAI.explain(code)
        await ctx.respond(f"**Here is what the code is doing**\n`1.{explanation}`")


@bot.message_command(guild_ids=SERVER_ID, name="fix")
async def fix(ctx, message: discord.Message):
    buggy_code = str(message.content)
    buggy_code = await find_between(buggy_code, "```py", "```")
    if buggy_code == "":
        await ctx.respond(embed=no_code_embed)
    else:
        await ctx.defer()
        fixed_code = OpenAI.fix(buggy_code)
        if fixed_code.replace("\n", "") == buggy_code.replace("\n", ""):
            await ctx.respond(f"**I think your code looks fine**")
        else:
            fixed_code = await pyify(fixed_code)
            await ctx.respond(f"**Maybe try using this code**\n{fixed_code}")


@bot.message_command(guild_ids=SERVER_ID, name="run")
async def run(ctx, message: discord.Message):
    code = await find_between(message.content, "```py", "```")
    if code == "":
        await ctx.respond(embed=no_code_embed)
    else:
        output = await runcode(code)
        print(output)
        await ctx.respond(f"**Here is the output**```\n{output}\n```")


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
