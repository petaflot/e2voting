# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap
# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap
import asyncio
import logging

from constants import *

if DEBUG_ENABLED:
	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger("asyncio").setLevel(logging.DEBUG)
else:
	logging.basicConfig(level=logging.INFO)

def increment(dic, key, inc = 1):
	try:
		dic[key] += inc
	except KeyError:
		dic[key] = inc


async def voter_full_id( voter_name, providers, stats_dict, ballotter ):
	"""
		a helper function known by everybody ; simply concatenate hashes IN THE CORRECT ORDER

		the correct order is the one specified in trustees.list

		balloter is a tuple of the form ( str, int )

	"""
	async def get_hash( voter_name, host, port ):
		#print(f"get_hash({voter_name}, {host}, {port})")
		try:
			reader, writer = await asyncio.open_connection(host, port)
		except ConnectionRefusedError:
			# TODO we might want to retry a few times...
			increment( stats_dict[(host,port)], ConnectionRefusedError )
		else:
			try:
				writer.write(voter_name)
				await writer.drain()

				data = await reader.read()
				#print(f'Received from {(host,port)}: {data}')
				#logging.debug(f'Received from {(host,port)}: {data}')
				return data
			finally:
				writer.close()
				await writer.wait_closed()
		
	#print(f"{providers = }")
	# TODO make sure this is good async
	try:
		return b''.join([ await get_hash( voter_name, *provider ) for provider in providers ])
	except TypeError:
		print(f"Warning: some trustee did not respond with hash for voter {voter_name}")
		return None

def enc( string ):
    return string.encode( ENCODING )

def dec( data ):
    return data.decode( ENCODING )

def byte_length(i):
	return (i.bit_length() + 7) // 8

def int_as_bytes(i):
	return i.to_bytes( byte_length(i), 'big' )

async def send_bytes( writer, b ):
	l = len(b)
	#print(f"need to send {l} bytes")
	if l < 128:
		# number of bytes to send fits on 7 bits
		bytelen = l+128
		writer.write(bytelen.to_bytes(1,'big'))
	else:
		# number of bytes to send requires more than 7 bits
		bytelen = byte_length(l)
		if l < 128:
			writer.write(bytelen.to_bytes(1,'big'))
			# the other end of the link now knows it must fetch a large integer of bytelen that is the size of the integer to read
		else:
			raise Exception("TODO make this recursive")
	writer.write(b)
	await writer.drain()
	#print(f"wrote {b}")
	logging.debug(f"wrote {b}")

async def recv_bytes( reader ):
	# TODO make this recursive for very large bytestrings ; the MSB should be 1 to stop recursion
	bytelen = int.from_bytes(await reader.read(1),'big')
	if bytelen > 128:
		bytelen -= 128
		#print(f"reading {bytelen} bytes")
		data = await reader.read(bytelen)
	else:
		#print(f"integer size is {bytelen} bytes")
		bytelen = int.from_bytes(await reader.read(bytelen),'big')
		#print(f"reading {bytelen} bytes")
		data = await reader.read(bytelen)

	#print(f"received {data}")
	logging.debug(f"Data received: {data}")

	return data
