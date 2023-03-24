from discord.ext import commands
import discord
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

async def send_message(message):
    try:

        await message.channel.send()
    except Exception as error:
        print(error)

def run_discord_bot():
    client = discord.Client(intents=discord.Intents.default())

    @client.event
    async def on_ready():
        print(f'{client.user} is now running.')

    @client.event
    async def on_message(message):
        await send_message 


    # @client.command(name="embed")
    # async def embed(ctx):
    #     embed = discord.Embed(title='Title', description='Desc', color=discord.Color.random())
    #     embed.add_field(name="Name", value="Value", inline=False)
    #     await ctx.send(embed=embed)

    client.run(TOKEN)