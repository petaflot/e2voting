#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap

"""
    ballot middleman instance
"""
import asyncio
import logging

from shared_funcs import dec, enc, voter_full_id, send_bytes, recv_bytes, int_as_bytes
from constants import ENCODING, PORT_INVITES, PORT_POLLING, PORT_HTTP, TIMEZONE, LISTEN, INVITE_ERROR_INT
import devel

STATS = None	# global ; will be dict

class BallotMiddleMan:
	"""

		each town/community SHOULD have its own process running for the
		duration of the ballot and a little longer to allow people to verify
		their results and various instances to concatenate the data from each
		source

		a BallotMiddleMan instance opens 3 ports
		- the first is usually 80 (or 443, see PORT_HTTP) and provides an
		  interface for the configuration variables and statistics
		- the second is a socket to accept votes on PORT_POLLING
		- the third is a socket to respond to SecretID requests on PORT_INVITES
		  ; this port MUST be isolated from the internet with proper firewall
		  rules and available only to administrative employees (they MUST
		  verify a voter's identity before providing this information)

	"""
	def __init__( self, authority, question, trustees, voters, host, encoding ):
		self.authority = authority	# just a name/reference, used for data gathering
		self.question = question	# it's good to know what question we're answering
		self.host = host			# the same for all services
		self.encoding = encoding	# encoding everything to ensure consistency of the data
		self.total_possible_votes = len(voters)
		self.result = {}

	@classmethod
	async def init( self, authority, question, trustees, voters, host, encoding = 'utf-8' ):
		self = BallotMiddleMan( authority, question, trustees, voters, host, encoding )

		# preparing trust authorities
		self.trustees = [ ( *t.split(b'\t',2)[:2], ) for t in trustees ]
		STATS = {( *t.split(b'\t',2)[:2], ): {'alias': t.rsplit(b'\t',1)[-1]} for t in trustees}

		print("generating invites...", end=' ')
		# the value id(v) is not used, it's just a redundant placeholder that may be used for verification
		self.invites = { await voter_full_id(v, self.trustees, STATS ): id(v) for v in voters}

		if len(self.invites) != self.total_possible_votes:	# should be unnecessary, just a safety measure
			raise Exception("INIT: Number of invites does not match number of electors ({len(self.invites)}/{len(self.total_possible_votes})")
		else:
			print("done!")

		print("TODO: invites_listener() and http_listen() are not active!")
		for v in voters:
			try:
				print(f'''Ballot 'paper' ID: {hex(self.request_auth( await voter_full_id(v, self.trustees, STATS) ))} for {v}''')
			except KeyError:
				# this is just here for the example
				print(f'''ERROR: cannot get ballot paper for {v}''')

		#await self.invites_listener()	# TODO start server (new thread?) ; uncommenting blocks
		#await self.http_listen()		# TODO fix event loop stuff (new thread?) ; uncommenting crashes
		print("ballot server is ready :-)")
		return self
	
	async def http_listen( self, port = PORT_HTTP ):
		"""
			starts an HTTP server to display running statistics, such as:

			- instance name and description, character set in use
			- trust authorities list and stats, such as
				- availability
				- response time
			- vote params such as start and deadline
			- results (if available/allowed)
			- poll question, obviously
			- list of voters
			- preferably, code validation features (TODO, but how?)

			this is needed so clients can gather initialization data
		"""
		#self.loop = asyncio.get_event_loop()
		self.loop = asyncio.get_running_loop()
		from ballot_quarthttp import http_run
		await http_run( self.loop, self.authority, self.host, port )
	
	async def invites_callback( self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
		voter_id = await recv_bytes( reader )
		try:
			inviteID = self.request_auth( voter_id )
		except KeyError:
			print(f"WARNING: failed fetching invite for {voter_id} (unkown user)")
			await send_bytes( writer, int_as_bytes(INVITE_ERROR_INT) )
		else:
			print(f"fetching invite for {voter_id}: {hex(inviteID)}")
			await send_bytes( writer, int_as_bytes(inviteID) )
		#print("done sending", hex(inviteID))
		writer.close()
		await writer.wait_closed()
		
	async def invites_listener(self, port = PORT_INVITES ):
		"""

			opens a port to listen for invites requests

			TODO: host (listening address) may differ from self.host (public
			address used for PORT_HTTP and PORT_POLLING ; PORT_POLLING may also
			have a distinct value because of a VPN that may exist)

		"""
		server = await asyncio.start_server(self.invites_callback, self.host, port)
		address = ', '.join(str(sock.getsockname()) for sock in server.sockets)
		print(f"{self.authority}: listening for invites requests on {address}")

		async with server:
			await server.serve_forever()

	async def open_poll( self, port = PORT_POLLING ):
		"""

			opens the port to listen for incoming votes

		"""
		print(f'''The question, open to {len(self.invites)} voters, is :\n\t"{dec(self.question)}"''')
		server = await asyncio.start_server(self.ballot_server_callback, self.host, port)
		address = ', '.join(str(sock.getsockname()) for sock in server.sockets)
		print(f"{self.authority}: listening for votes on {address}")
		#logging.info(f'Serving on {address}')

		async with server:
			await server.serve_forever()

	def request_auth( self, voter ):
		"""
			generate personalized ballot paper ("bulletin de vote")

			TODO: make this one-time only? see "generating invites..." in self.init()
		"""
		return id(self.invites[voter])

	def submit_vote( self, voter_full_id, secret, value ):
		"""
			the few CPU cycles (and associated network traffic) it takes this function to execute are the _only_ 
			places where voter/vote can be sniffed (matched)
		"""
		#print("trying to submit vote:", value)
		try:
			if id( self.invites[ voter_full_id ]) == secret:
				self.invites.pop( voter_full_id )	# in some rare cases, may also raise KeyError
				self.result[ secret ] = value
				return id(self.result[secret])
			else:
				raise KeyError
		except KeyError:
			#print(f"submit FAIL for {voter_full_id}")
			logging.debug(f"submit FAIL for {voter_full_id}: {value}")
	
	def verify_vote( self, secret, index ):
		"""
			by feeding 'random' data in this function, counting the number of occurences allows for statistical 
			analysis of the integrity of the ballot (this is the so-called "brute-force" pseudo-attack)
		"""
		if id(self.result[secret]) == index:	return self.result[ secret ]
		else:									raise KeyError	# to make querying cleaner ; not strictly necessary
	
	def ballot_integrity_check( self ):
		"""
			SHOULD return zero
			MAY return a small negative integer for a very short while (borderline case due to concurrency issues)
			MUST NOT return a positive value (this means some votes have been added which shouldn't have)
		"""
		return self.total_possible_votes - ( len(self.invites) + len(self.result) )

	def concatenate_votes( self ):
		"""
			return a summary of the results. this data must be public at the very least when the ballot is closed
		"""
		from collections import Counter
		return Counter( self.result.values() )

	async def ballot_server_callback( self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
		""" Callback function for handling incoming server functions.
	
		:param reader: Reader stream
		:param writer: Writer stream
		"""
		#print("\nserver_request callback executing")
		#logging.debug("server_request callback executing")

		voter_id = await recv_bytes( reader )
		#print(f"{voter_id = }")
		secretID = int.from_bytes(await recv_bytes( reader ))
		#print(f"{hex(secretID) = }")
		answer = await recv_bytes( reader )
		#print(f"{answer = }")
		
		verification_key = self.submit_vote(
				voter_full_id = voter_id,
				secret = secretID,
				value = answer,
			)
		#print(f"{verification_key = }")

		# Send response
		if verification_key is not None:
			#print(f"Send: {r}")
			#logging.debug(f"Send: {r}")
			#print(f"{verification_key = }, {type(verification_key) = }")
			await send_bytes( writer, int_as_bytes(verification_key) )
			print(f"got vote: {answer}")
		#else:
		#	print(f"WARNING: Vote could not be cast! {voter_id}: {answer}")
	
		# Shut down Stream
		writer.close()
		await writer.wait_closed()

async def main( authority, question, trustees, voters, host ):
	BMM = await BallotMiddleMan.init( authority, question, trustees, voters, host, ENCODING )
	await BMM.open_poll()


if __name__ == '__main__':
	from sys import argv
	try:
		# whut? why doesn't this work? TypeError: a bytes-like object is required, not 'str'
		#voters = [v.rstrip('b\n') for v in open(argv[1],'rb').readlines()]
		# this double-nested generator works but is not as pretty and probably not optimal
		voters = [ v.rstrip(b'\n') for v in [v for v in open(argv[1],'rb').readlines()] ]
		trustees = [ l.rstrip(b'\n') for l in open(argv[2],'rb').readlines() ]
	except FileNotFoundError:
		print(f"usage: {argv[0]} <voters.list> <trustees.list>")
		raise SystemExit
	except IndexError:
		print(f"usage: {argv[0]} <voters.list> <trustees.list>")
		raise SystemExit

	authority = enc(input("Authority ID/Name: "))
	authority = devel.AUTHORITY_NAME if authority == b'' else authority
	question = enc(input("Question: "))
	question = devel.QUESTION if question == b'' else question
	host = input(f"Listen on [{LISTEN}]: ")
	host = LISTEN if host == '' else host

	print()
	asyncio.run( main( authority, question, trustees, voters, host ) )
