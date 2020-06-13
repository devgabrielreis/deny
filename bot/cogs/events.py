import discord
from discord.ext import commands

class Events(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		self.bot.db.remove_guild(guild.id)

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel):
		await self.bot.db.remove_talk_channel(channel.guild.id, channel.id)
		await self.bot.db.remove_learn_channel(channel.guild.id, channel.id)

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return
		if message.is_system():
			return
		if message.guild is None:
			return
		if not self.bot.db.is_guild_in(message.guild.id):
			await self.bot.db.add_guild(message.guild.id)

		if message.clean_content.startswith((self.bot.command_prefix, '>', '!', '$', '=', '?', '@', '-', '.', ';', '/')):
			return

		if await self.bot.db.is_learn_channel(message.guild.id, message.channel.id):
			await self.bot.db.update_chain(message.guild.id, message.clean_content)

		if await self.bot.db.is_talk_channel(message.guild.id, message.channel.id):
			if await self.bot.db.get_guild_saved_messages(message.guild.id) < 50:
				return
			if await self.bot.db.calc_probability(message.guild.id, message.channel.id):
				async with message.channel.typing():
					await message.channel.send(await self.bot.db.generate(message.guild.id))

def setup(bot):
	bot.add_cog(Events(bot))
