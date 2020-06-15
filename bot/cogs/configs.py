import asyncio
import discord
from discord.ext import commands

class Configs(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True)
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	@commands.has_permissions(manage_channels=True)
	async def settalkchat(self, ctx):
		if len(ctx.message.channel_mentions) == 0:
			await ctx.send(f'Use `{self.bot.command_prefix}help settalkchat` to get help on how to use this command.')
			return

		result = []

		msg = ctx.message.content.split()

		conn, cur = await self.bot.db.create_connection(ctx.guild.id)

		for channel in ctx.message.channel_mentions:
			if not isinstance(channel, discord.channel.TextChannel):
				result.append(f'- {channel.mention} isn\'t a text channel.')
				continue

			bot_permissions = channel.permissions_for(ctx.guild.get_member(self.bot.user.id))
			if not bot_permissions.read_messages:
				result.append(f'- I do not have permission to read messages on {channel.mention}.')
				continue
			elif not bot_permissions.send_messages:
				result.append(f'- I do not have permission to send messages on {channel.mention}.')
				continue

			try:
				probability = int(msg[msg.index(channel.mention)+1])
				probability = 100 if probability > 100 else probability
				probability = 1 if probability < 1 else probability
			except:
				probability = 10

			r = await self.bot.db.add_talk_channel(conn, cur, channel.id, probability)
			if r == 1:
				result.append(f'- {channel.mention} was added to the talking channels list with a {probability}% probability.')
			elif r == 2:
				#The channel was already saved, just its probability was changed.
				result.append(f'- {channel.mention} probability was set to {probability}%.')
			else: #r == 3
				result.append(f'- {channel.mention} was not added, you can only add up to 5 talking channels.')

		await self.bot.db.close_connection(conn, cur)

		await ctx.send(embed=discord.Embed(title='Action completed with the following results:', description='\n'.join(result), color=0x00FF00))

	@settalkchat.command(name='remove')
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	@commands.has_permissions(manage_channels=True)
	async def _settalkchat_remove(self, ctx, all=None):
		if all == 'all':
			conn, cur = await self.bot.db.create_connection(ctx.guild.id)
			await self.bot.db.remove_all_talk_channels(conn, cur)
			await self.bot.db.close_connection(conn, cur)

			await ctx.send('All channels have been removed from the talking channels list!')
			return

		if len(ctx.message.channel_mentions) == 0:
			await ctx.send(f'Use `{self.bot.command_prefix}help settalkchat` to get help on how to use this command.')
			return

		result = []

		conn, cur = await self.bot.db.create_connection(ctx.guild.id)

		for channel in ctx.message.channel_mentions:
			r = await self.bot.db.remove_talk_channel(conn, cur, channel.id)
			if r == 1:
				result.append(f'- {channel.mention} was removed from the talking channels list.')
			else: #r == 2
				result.append(f'- {channel.mention} is not in the talk channels list.')

		await self.bot.db.close_connection(conn, cur)

		await ctx.send(embed=discord.Embed(title='Action completed with the following results:', description='\n'.join(result), color=0x00FF00))

	@commands.group(invoke_without_command=True)
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	@commands.has_permissions(manage_channels=True)
	async def setlearnchat(self, ctx):
		if len(ctx.message.channel_mentions) == 0:
			await ctx.send(f'Use `{self.bot.command_prefix}help setlearnchat` to get help on how to use this command.')
			return

		result = []

		conn, cur = await self.bot.db.create_connection(ctx.guild.id)

		for channel in ctx.message.channel_mentions:
			if not isinstance(channel, discord.channel.TextChannel):
				result.append(f'- {channel.mention} isn\'t a text channel.')
				continue

			bot_permissions = channel.permissions_for(ctx.guild.get_member(self.bot.user.id))
			if not bot_permissions.read_messages:
				result.append(f'- I do not have permission to read messages on {channel.mention}.')
				continue

			r = await self.bot.db.add_learn_channel(conn, cur, channel.id)
			if r == 1:
				result.append(f'- {channel.mention} was added to the learning channels list.')
			elif r == 2:
				result.append(f'- {channel.mention} was already in the learning channels list.')
			else: #r == 3
				result.append(f'- {channel.mention} was not added, you can only add up to 10 talking channels.')

		await self.bot.db.close_connection(conn, cur)

		await ctx.send(embed=discord.Embed(title='Action completed with the following results:', description='\n'.join(result), color=0x00FF00))

	@setlearnchat.command(name='remove')
	@commands.bot_has_permissions(send_messages=True, embed_links=True)
	@commands.has_permissions(manage_channels=True)
	async def _setlearnchat_remove(self, ctx, all=None):
		if all == 'all':
			conn, cur = await self.bot.db.create_connection(ctx.guild.id)
			await self.bot.db.remove_all_learn_channels(conn, cur)
			await self.bot.db.close_connection(conn, cur)

			await ctx.send('All channels have been removed from the learning channels list!')
			return

		if len(ctx.message.channel_mentions) == 0:
			await ctx.send(f'Use `{self.bot.command_prefix}help setlearnchat` to get help on how to use this command.')
			return

		result = []

		conn, cur = await self.bot.db.create_connection(ctx.guild.id)

		for channel in ctx.message.channel_mentions:
			r = await self.bot.db.remove_learn_channel(conn, cur, channel.id)
			if r == 1:
				result.append(f'- {channel.mention} was removed from the learning channels list.')
			else: #r == 2
				result.append(f'- {channel.mention} was not in the learn channels list.')

		await self.bot.db.close_connection(conn, cur)

		await ctx.send(embed=discord.Embed(title='Action completed with the following results:', description='\n'.join(result), color=0x00FF00))

	@commands.command()
	@commands.bot_has_permissions(send_messages=True)
	@commands.has_permissions(manage_channels=True)
	async def reset(self, ctx):
		def check(message):
			return ctx.author == message.author and ctx.channel == message.channel

		prefix = self.bot.command_prefix

		await ctx.send(f'This action will reset all the data for this guild! Send `{prefix}yes` to confirm.')

		try:
			msg = await self.bot.wait_for('message', check=check, timeout=10.0)
		except asyncio.TimeoutError:
			await ctx.send('Time is over!')
		else:
			if not msg.content.lower() == f'{prefix}yes':
				await ctx.send('Action canceled!')
			else:
				conn, cur = await self.bot.db.create_connection(ctx.guild.id)
				await self.bot.db.reset_guild_data(conn, cur)
				await self.bot.db.close_connection(conn, cur)

				await ctx.send('Done!')

def setup(bot):
	bot.add_cog(Configs(bot))
