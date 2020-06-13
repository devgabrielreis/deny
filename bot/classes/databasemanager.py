import aiosqlite
from sqlite3 import Binary
import json
import os
import random

class DatabaseManager:
	def __init__(self, dirpath, *, max_messages=5000):
		self.dirpath = dirpath
		self.max_messages = max_messages

	async def add_guild(self, guild_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('CREATE TABLE talkchannels (channel INT, probability INT)')
		await cur.execute('CREATE TABLE learnchannels (channel INT)')
		await cur.execute('CREATE TABLE messages (id INTEGER PRIMARY KEY, message TEXT)')
		await cur.execute('CREATE TABLE markovchain (state TEXT, total INTEGER, nodes BLOB)')
		await cur.execute('INSERT INTO markovchain (state, total, nodes) VALUES (?, ?, ?)',
			('__START__', 0, self._dict_to_blob(dict())))

		await conn.commit()
		await self._close_connection(conn, cur)

	def is_guild_in(self, guild_id):
		return os.path.isfile(f'{self.dirpath}/{guild_id}.db')

	async def get_guild_saved_messages(self, guild_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT total FROM markovchain WHERE state = ? LIMIT 1',
			('__START__', ))

		total_saved_messages = await cur.fetchone()
		total_saved_messages = total_saved_messages[0]

		await self._close_connection(conn, cur)

		return total_saved_messages

	async def reset_guild_data(self, guild_id):
		conn, cur = await self._create_connection(guild_id)

		for table in ['talkchannels', 'learnchannels', 'messages', 'markovchain']:
			await cur.execute(f'DROP TABLE {table}')

		await cur.execute('CREATE TABLE talkchannels (channel INT, probability INT)')
		await cur.execute('CREATE TABLE learnchannels (channel INT)')
		await cur.execute('CREATE TABLE messages (id INTEGER PRIMARY KEY, message TEXT)')
		await cur.execute('CREATE TABLE markovchain (state TEXT, total INTEGER, nodes BLOB)')
		await cur.execute('INSERT INTO markovchain (state, total, nodes) VALUES (?, ?, ?)',
			('__START__', 0, self._dict_to_blob(dict())))

		await conn.commit()
		await self._close_connection(conn, cur)

	def remove_guild(self, guild_id):
		os.remove(f'{self.dirpath}/{guild_id}.db')

	async def add_talk_channel(self, guild_id, channel_id, probability):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT channel FROM talkchannels')
		talk_channels = [row[0] async for row in cur]

		if channel_id in talk_channels:
			await cur.execute('UPDATE talkchannels SET probability = ? WHERE channel = ?',
				(probability, channel_id))
			await conn.commit()
			await self._close_connection(conn, cur)
			return 2

		if len(talk_channels) >= 5:
			await self._close_connection(conn, cur)
			return 3

		await cur.execute('INSERT INTO talkchannels (channel, probability) VALUES (?, ?)',
			(channel_id, probability))
		await conn.commit()
		await self._close_connection(conn, cur)
		return 1

	async def add_learn_channel(self, guild_id, channel_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT channel FROM learnchannels')
		talk_channels = [row[0] async for row in cur]

		if channel_id in talk_channels:
			await self._close_connection(conn, cur)
			return 2

		if len(talk_channels) >= 10:
			await self._close_connection(conn, cur)
			return 3

		await cur.execute('INSERT INTO learnchannels (channel) VALUES (?)',
			(channel_id, ))
		await conn.commit()
		await self._close_connection(conn, cur)
		return 1

	async def is_talk_channel(self, guild_id, channel_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT COUNT(channel) FROM talkchannels WHERE channel = ? LIMIT 1',
			(channel_id, ))
		check = await cur.fetchone()
		check = check[0]

		await self._close_connection(conn, cur)

		return check == 1

	async def is_learn_channel(self, guild_id, channel_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT COUNT(channel) FROM learnchannels WHERE channel = ? LIMIT 1',
			(channel_id, ))
		check = await cur.fetchone()
		check = check[0]

		await self._close_connection(conn, cur)

		return check == 1

	async def get_talk_channels(self, guild_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT channel, probability FROM talkchannels')

		talk_channels = {}
		async for row in cur:
			talk_channels[row[0]] = row[1]

		await self._close_connection(conn, cur)

		return talk_channels

	async def get_learn_channels(self, guild_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT channel FROM learnchannels')
		talk_channels = [row[0] async for row in cur]

		await self._close_connection(conn, cur)

		return talk_channels

	async def remove_talk_channel(self, guild_id, channel_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT COUNT(channel) FROM talkchannels WHERE channel = ? LIMIT 1',
			(channel_id, ))
		check = await cur.fetchone()
		check = check[0]

		if check == 0:
			await self._close_connection(conn, cur)
			return 2

		await cur.execute('DELETE FROM talkchannels WHERE channel = ?',
			(channel_id, ))
		await conn.commit()

		await self._close_connection(conn, cur)
		return 1

	async def remove_learn_channel(self, guild_id, channel_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT COUNT(channel) FROM learnchannels WHERE channel = ? LIMIT 1',
			(channel_id, ))
		check = await cur.fetchone()
		check = check[0]

		if check == 0:
			await self._close_connection(conn, cur)
			return 2

		await cur.execute('DELETE FROM learnchannels WHERE channel = ?',
			(channel_id, ))
		await conn.commit()

		await self._close_connection(conn, cur)
		return 1

	async def calc_probability(self, guild_id, channel_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT probability FROM talkchannels WHERE channel = ?',
			(channel_id, ))

		probability = await cur.fetchone()
		probability = probability[0]

		await self._close_connection(conn, cur)

		return random.randint(1, 100) <= probability

	async def remove_all_talk_channels(self, guild_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('DELETE FROM talkchannels')
		await conn.commit()

		await self._close_connection(conn, cur)

	async def remove_all_learn_channels(self, guild_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('DELETE FROM learnchannels')
		await conn.commit()

		await self._close_connection(conn, cur)

	async def update_chain(self, guild_id, content):
		if not self._is_content_clean(content):
			return

		conn, cur = await self._create_connection(guild_id)

		await cur.execute('INSERT INTO messages (message) VALUES (?)',
			(content, ))

		content = content.split()
		content.append('__END__')

		await cur.execute('SELECT total, nodes FROM markovchain WHERE state = ? LIMIT 1',
			('__START__', ))

		row = await cur.fetchone()
		total_saved_messages, nodes = row[0], self._blob_to_dict(row[1])

		total_saved_messages += 1

		if f'{content[0]} {content[1]}' in nodes:
			nodes[f'{content[0]} {content[1]}'] += 1
		else:
			nodes[f'{content[0]} {content[1]}'] = 1

		await cur.execute('UPDATE markovchain SET total = ?, nodes = ? WHERE state = ?',
			(total_saved_messages, self._dict_to_blob(nodes), '__START__'))

		for i in range(2, len(content)):
			await cur.execute('SELECT total, nodes FROM markovchain WHERE state = ? LIMIT 1',
				(f'{content[i-2]} {content[i-1]}', ))
			row = await cur.fetchone()
			if row:
				total, nodes = row[0], self._blob_to_dict(row[1])
				total += 1

				if content[i] in nodes:
					nodes[content[i]] += 1
				else:
					nodes[content[i]] = 1

				await cur.execute('UPDATE markovchain SET total = ?, nodes = ? WHERE state = ?',
					(total, self._dict_to_blob(nodes), f'{content[i-2]} {content[i-1]}'))
			else:
				nodes = {content[i]: 1}
				await cur.execute('INSERT INTO markovchain (state, total, nodes) VALUES (?, ?, ?)',
					(f'{content[i-2]} {content[i-1]}', 1, self._dict_to_blob(nodes)))

		await conn.commit()

		await self._close_connection(conn, cur)

		if total_saved_messages > self.max_messages:
			await self._remove_message(guild_id)

	async def generate(self, guild_id):
		sentence = []

		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT nodes FROM markovchain WHERE state = ? LIMIT 1',
			('__START__', ))

		nodes = await cur.fetchone()
		nodes = self._blob_to_dict(nodes[0])
		state = random.choice(list(nodes))
		sentence += state.split()

		while len(sentence) < 30:
			await cur.execute('SELECT nodes FROM markovchain WHERE state = ? LIMIT 1',
				(state, ))
			nodes = await cur.fetchone()
			nodes = self._blob_to_dict(nodes[0])
			next_node = random.choice(list(nodes))
			if next_node == '__END__':
				break
			sentence += [next_node]
			state = f'{state.split()[1]} {next_node}'

		await self._close_connection(conn, cur)

		return ' '.join(sentence)

	async def _remove_message(self, guild_id):
		conn, cur = await self._create_connection(guild_id)

		await cur.execute('SELECT message, id FROM messages LIMIT 1')

		row = await cur.fetchone()
		message, id = row[0], row[1]
		message = message.split()
		message.append('__END__')

		await cur.execute('DELETE FROM messages WHERE id = ?',
			(id, ))

		await cur.execute('SELECT nodes, total FROM markovchain WHERE state = ? LIMIT 1',
			('__START__', ))

		row = await cur.fetchone()
		nodes, total = self._blob_to_dict(row[0]), row[1]

		total -= 1

		if nodes[f'{message[0]} {message[1]}'] == 1:
			del nodes[f'{message[0]} {message[1]}']
		else:
			nodes[f'{message[0]} {message[1]}'] -= 1

		await cur.execute('UPDATE markovchain SET total = ?, nodes = ? WHERE state = ?',
			(total, self._dict_to_blob(nodes), '__START__'))

		for i in range(2, len(message)):
			await cur.execute('SELECT nodes, total FROM markovchain WHERE state = ? LIMIT 1',
				(f'{message[i-2]} {message[i-1]}', ))

			row = await cur.fetchone()
			nodes, total = self._blob_to_dict(row[0]), row[1]
			if total > 1:
				total -= 1

				if nodes[message[i]] == 1:
					del nodes[message[i]]
				else:
					nodes[message[i]] -= 1

				await cur.execute('UPDATE markovchain SET total = ?, nodes = ? WHERE state = ?',
					(total, self._dict_to_blob(nodes), f'{message[i-2]} {message[i-1]}'))
			else:
				await cur.execute('DELETE FROM markovchain WHERE state = ?',
					(f'{message[i-2]} {message[i-1]}', ))

		await conn.commit()

		await self._close_connection(conn, cur)

	def _is_content_clean(self, content):
		content = content.split()

		if len(content) < 5 or len(content) > 30:
			return False
		for word in content:
			if word.startswith(('https://', 'http://')):
				return False
			elif word == '__START__' or word == '__END__':
				return False

		return True

	def _dict_to_blob(self, dict):
		dict = json.dumps(dict).encode('utf-8')
		return Binary(dict)

	def _blob_to_dict(self, blob):
		return json.loads(blob.decode('utf-8'))

	async def _create_connection(self, guild_id):
		conn = await aiosqlite.connect(f'{self.dirpath}/{guild_id}.db')
		cur = await conn.cursor()
		return conn, cur

	async def _close_connection(self, conn, cur):
		await cur.close()
		await conn.close()
