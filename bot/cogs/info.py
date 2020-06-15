import discord
from discord.ext import commands

class Info(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.github_link = 'https://github.com/namateeri/markovchain-discord-chatbot'

		prefix = self.bot.command_prefix

		self.help_messages = {
			'shutdown':
				'**Bot owner only**\nTurn the bot off.',

			'settalkchat':
				f'**Need permission: Manage Channels**\nUsage:\n`{prefix}settalkchat <channel mention> <probability>`\n`{prefix}settalkchat remove <channel mention>`\n`{prefix}settalkchat remove all`\nSet or remove channels where the bot will send messages.\nProbability must be a number from 0 to 100, if no probability is given, the value of 10 will be used.\nYou can add or remove more than one channel at once.\nThe bot need at least 50 saved messages to start sending messages.',

			'setlearnchat':
				f'**Need permission: Manage Channels**\nUsage:\n`{prefix}setlearnchat <channel mention>`\n`{prefix}setlearnchat remove <channel mention>`\n`{prefix}setlearnchat remove all`\nSet or remove channels where the bot will log messages, these messages will be used in the generation of random messages.\nYou can add or remove more than one channel at once.',

			'reset':
				'**Need permission: Manage Channels**\nReset the saved messages and the saved channels.',

			'info':
				'Show the number of saved messages, the channels where the bot will send messages and read messages and some info about the bot.',

			'help':
				'Show the help message.'
		}

	@commands.command()
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	async def info(self, ctx):
		embed = discord.Embed(color=0x00FF00)
		embed.set_author(name='Info', icon_url=self.bot.user.avatar_url)
		embed.set_thumbnail(url=ctx.guild.icon_url)

		conn, cur = await self.bot.db.create_connection(ctx.guild.id)

		talk_channels = await self.bot.db.get_talk_channels(cur)
		learn_channels = await self.bot.db.get_learn_channels(cur)
		saved_messages = await self.bot.db.get_guild_saved_messages(cur)

		await self.bot.db.close_connection(conn, cur)

		tc = []
		lc = []

		for channel_id in talk_channels:
			channel = self.bot.get_channel(channel_id)
			tc.append(f'{channel.mention}: {talk_channels[channel_id]}%')
		for channel_id in learn_channels:
			channel = self.bot.get_channel(channel_id)
			lc.append(channel.mention)

		tc = '\n'.join(tc) if len(tc) > 0 else 'None'
		lc = '\n'.join(lc) if len(lc) > 0 else 'None'

		if saved_messages < 50:
			saved_messages = f'{saved_messages}\n*The bot need at least 50 saved messages to start sending messages.*'

		embed.add_field(name='Guild Info', value=f'Saved messages for this guild: {saved_messages}\n\nTalk chats and the respective chance to the bot send message on them:\n{tc}\n\nLearn chats:\n{lc}')
		embed.add_field(name='Bot Info', value=f'Version: {self.bot.version}\nTotal guilds: {len(self.bot.guilds)}\n\nThis bot is an open source project, you can check its source code on [GitHub]({self.github_link})')

		await ctx.send(embed=embed)

	@commands.command()
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	async def help(self, ctx, cmd=None):
		prefix = self.bot.command_prefix

		embed = discord.Embed(color=0x00C8FF)
		embed.set_author(name='Help', icon_url=self.bot.user.avatar_url)

		if cmd in self.help_messages:
			embed.add_field(name=f'{prefix}{cmd}', value=self.help_messages[cmd])
		else:
			embed.add_field(name='Commands:', value=f'`settalkchat`, `setlearnchat`, `reset`, `info`, `help`.\n\nUse `{prefix}help <command>` to get more information on each command.')

		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Info(bot))
