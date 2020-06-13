import discord
from discord.ext import commands
import os
from datetime import datetime
from classes import DatabaseManager

class ChatBot(commands.Bot):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.remove_command('help')

		self.version = '1.2.3'

		if not os.path.isdir('./data'):
			os.makedirs('./data')
		self.db = DatabaseManager('./data')

		for cog in ['events', 'owner', 'configs', 'info', 'errors']:
			self.load_extension(f'cogs.{cog}')

	async def on_ready(self):
		await self.change_presence(activity=discord.Game(f'use {self.command_prefix}help'))
		print(datetime.now().strftime('%d/%m/%Y %H:%M:%S')+f' - Online as {self.user}!')

	async def on_connect(self):
		print(datetime.now().strftime('%d/%m/%Y %H:%M:%S')+' - Connected!')

	async def on_disconnect(self):
		print(datetime.now().strftime('%d/%m/%Y %H:%M:%S')+' - Disconnected!')

	async def on_message(self, message):
		if message.guild is None:
			return
		if not self.db.is_guild_in(message.guild.id):
			await self.db.add_guild(message.guild.id)
		await self.process_commands(message)

bot_token = #Your token

bot = ChatBot(command_prefix=';', reconnect=True)

bot.run(bot_token)
