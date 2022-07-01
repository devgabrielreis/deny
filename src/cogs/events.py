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
		conn, cur = await self.bot.db.create_connection(channel.guild.id)

		await self.bot.db.remove_talk_channel(conn, cur, channel.id)
		await self.bot.db.remove_learn_channel(conn, cur, channel.id)

		await self.bot.db.close_connection(conn, cur)

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return
		if message.is_system():
			return
		if message.guild is None:
			return
		if message.clean_content.startswith((self.bot.command_prefix, '>', '!', '$', '=', '?', '@', '-', '.', ';', '/')):
			return

		conn, cur = await self.bot.db.create_connection(message.guild.id)

		if await self.bot.db.is_learn_channel(cur, message.channel.id):
			await self.bot.db.update_chain(conn, cur, message.clean_content)

		if await self.bot.db.is_talk_channel(cur, message.channel.id):
			if await self.bot.db.get_guild_saved_messages(cur) >= 50:
				if await self.bot.db.calc_probability(cur, message.channel.id):
					async with message.channel.typing():
						await message.channel.send(await self.bot.db.generate(cur))

		await self.bot.db.close_connection(conn, cur)

def setup(bot):
	bot.add_cog(Events(bot))
