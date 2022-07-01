import asyncio
import discord
from discord.ext import commands
from datetime import datetime

class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.is_owner()
	@commands.bot_has_permissions(send_messages=True)
	async def shutdown(self, ctx):
		def check(message):
			return message.author == ctx.author and message.channel == ctx.channel

		prefix = self.bot.command_prefix

		await ctx.send(f'Are you sure? Send `{prefix}yes` to confirm.')

		try:
			msg = await self.bot.wait_for('message', check=check, timeout=10.0)
		except asyncio.TimeoutError:
			await ctx.send('Time is over!')
		else:
			if not msg.content.lower() == f'{prefix}yes':
				await ctx.send('Action canceled!')
			else:
				await ctx.send('Shutting down...')
				print(datetime.now().strftime('%d/%m/%Y %H:%M:%S')+' - Shutting down...')
				await self.bot.logout()

def setup(bot):
	bot.add_cog(Owner(bot))
