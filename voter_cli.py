#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap

import asyncio
import logging
import urllib.request
import base64
import json
from datetime import datetime

from shared_funcs import enc, dec, recv_bytes, send_bytes, voter_full_id
from constants import PORT_HTTP, LISTEN

STATS = {}

class Voter:
	"""

		This class represents an individual voter and defines the necessary
		functions to interact with the system.

	"""
	def __init__(self, voter_id):
		self.voter_id = voter_id
		self.ballots = {}

	async def register_ballot( self, host_port = None ):
		"""

			add a ballot to the local list

		"""
		if host_port is None:
			host_port = input("Ballot server address[:port] = ")
			try:
				ballot_server_addr, ballot_server_port = host_port.split(':')
				ballot_server_addr, ballot_server_port = enc(ballot_server_addr), int(ballot_server_port)
			except ValueError:
				ballot_server_addr = enc(ballot_server_addr)
				ballot_server_port = PORT_POLLING
		else:
			ballot_server_addr, ballot_server_port = host_port

		# TODO allow connection over SSL
		#print('http://'+':'.join([ballot_server_addr, str(ballot_server_port)])+'/config.json')
		data = urllib.request.urlopen('http://'+':'.join([ballot_server_addr, str(ballot_server_port)])+'/config.json').read()
		ballot_config = {}

		# TODO write a function that does this a bit more automatically and re-usable for other projects
		for key in json.loads(data):
			key, val = base64.b64decode(enc(key)), base64.b64decode(enc(json.loads(data)[key]))
			match key:
				case b'poll_port':
					val = int.from_bytes( val, 'big' )
				case b'datetime':
					import pendulum
					print("msg1",enc(pendulum.now().strftime(DATETIME_FMT)))
					ts = ''.join(str(val).rsplit(':',1))
					print("msg2",ts)
					val = datetime.strptime(ts, DATETIME_FMT)
				case b'anticipated_results':
					val = bool(val)
				case b'trustees':
					val = [(HP[0], int(HP[1])) for HP in [hp.split(':',1) for hp in dec(val).split('\n')]]
			ballot_config[key] = val

		data = urllib.request.urlopen('http://'+':'.join([ballot_server_addr, str(ballot_server_port)])+'/trustees.json').read()
		#print(f"{data = }")
		for key in json.loads(data):
			key, val = base64.b64decode(enc(key)), base64.b64decode(enc(json.loads(data)[key]))
			match key:
				case b'trustees':
					val = [(HP[0], int(HP[1])) for HP in [hp.split(':',1) for hp in dec(val).split('\n')]]
					#print(f"{val = }")
				case _:
					print(f"WARNING: trustees data contains unknown key {key}")
			ballot_config[key] = val


		# TODO not so great when using a GUI, better not to store it (or even prompt for it) until right before the vote is submitted ; sqlite storage if required
		ballot_config[b'secret_id'] = int(input(f"SecretID for {ballot_config[b'authority']} (0x????????????) "),0).to_bytes(6,'big')

		try:
			self.ballots[ballot_config[b'question']][(ballot_server_addr, ballot_server_port)] = ballot_config
		except KeyError:
			self.ballots[ballot_config[b'question']] = {(ballot_server_addr, ballot_server_port): ballot_config}

		print(f"Added ballot @{ballot_server_addr}:{ballot_server_port} for question:\n\t{dec(ballot_config[b'question'])}")	# TODO persistent storage with sqlite
		#print(f"{ballot_config[b'secret_id'] = }")
		#print(self.ballots[ballot_config[b'question']][(ballot_server_addr, ballot_server_port)][b'trustees'])
	
	def ballots_list(self):
		# TODO make a prettier output
		print(self.ballots)
	
	async def submit_vote( self, question = None, ballotter = None, answer = None ):
		"""

			send a vote to a ballot instance

		"""
		prefered_answers = {}

		def get_answer( question ):
			try:
				return prefered_answers[question]
			except KeyError:
				prefered_answers[question] = b''
				while prefered_answers[question] == b'':
					print(f"The question is:\n\t{dec(question)}")
					prefered_answers[question] = enc(input("Your answer: "))
					print(f"Your answer: {prefered_answers[question]}")
					if input("Confirm? [yes/No]: ") != 'yes':
						prefered_answers[question] = b''
				return prefered_answers[question]


		if question is None and ballotter is None:
			for question in self.ballots:
				#print(f"{question = }")
				answer = get_answer( question ) if answer is None else answer
				for ballotter in self.ballots[question]:
					await self.submit_vote(question=question, ballotter=ballotter, answer=answer)
		elif ballotter is None:
			answer = get_answer( question ) if answer is None else answer
			for ballotter in self.ballots[question]:
				await self.submit_vote(question=question, ballotter=ballotter, answer=answer)
		elif question is None:
			raise Exception("Won't do that, makes little sense")
		else:
			trustees = self.ballots[question][ballotter][b'trustees']
			for t in trustees:
				# TODO reset the stats from time to time
				try:				STATS[t]
				except KeyError:	STATS[t] = {}

			#print(f"{list(trustees.keys()) = }")
			port = self.ballots[question][ballotter][b'poll_port']
			voter_id = await voter_full_id( self.voter_id, trustees, STATS, (ballotter,port) )
			answer = get_answer( question ) if answer is None else answer
			#print(self.ballots[question][ballotter].keys())
			secretID = self.ballots[question][ballotter][b'secret_id']
			print(f"will submit {answer} to {ballotter[0]}:{port} as {voter_id} with SecretID {hex(int.from_bytes(secretID,'big'))}")
			try:
				reader, writer = await asyncio.open_connection(ballotter[0], port)
				try:
					for value in (voter_id, secretID, answer):
						await send_bytes( writer, value )
					print("all values sent, waiting for confirmation ID")

					verification_key = int.from_bytes(await recv_bytes(reader),'big')	# verification ID as per poc.py
					if not verification_key:
						print("""ERROR: vote could could not be cast ; possible causes include :
	- your vote was already recorded
	- there was a TrustAuthority problem ; try again later (and report the issue if this persists)""")
						return False
					else:
						print(f'Verification key received from {(ballotter[0],port)}: {hex(verification_key)}')
						logging.debug(f'Verification key received from {(ballotter[0],port)}: {hex(verification_key)}')
						self.ballots[question][ballotter]['verification_key'] = verification_key
						return verification_key
				except:
					raise
				finally:
					writer.close()
					await writer.wait_closed()
			
			except ConnectionRefusedError:
				print("ConnectionRefusedError, try again later")	# TODO automatic retries

async def main( voter_id ):
	V = Voter( voter_id )
	# TODO prompt for or read from args/ncofig/whatever
	await V.register_ballot( (LISTEN, PORT_HTTP) )
	await V.submit_vote()

if __name__ == '__main__':
	from sys import argv
	try:
		voter_id = enc(argv[1])
	except IndexError:
		voter_id = enc(input("Voter ID: "))
	asyncio.run( main( voter_id ) )
