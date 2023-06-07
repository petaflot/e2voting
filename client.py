#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap

import asyncio
import logging

from shared_funcs import enc, dec, recv_bytes, send_bytes, voter_full_id
import devel

STATS = {}

class Voter:
	"""

		This class represents an individual voter and defines the necessary
		fuctions to interact with the system.

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
				ballot_server_port = devel.PORT_POLLING
		else:
			ballot_server_addr, ballot_server_port = host_port
		d = {}
		# TODO: retrieve parameters from http (json/XML)
		d['authority'] = devel.AUTHORITY_NAME
		d['poll_open'] = devel.POLL_OPEN
		d['poll_port'] = devel.PORT_POLLING
		d['poll_early_results'] = devel.POLL_EARLY_RESULTS
		d['ballot_competitors'] = devel.BALLOT_COMPETITORS
		d['trustees'] = devel.TRUSTEES

		# TODO not so great when using a GUI, better not to store it (or even prompt for it) until right before the vote is submitted ; sqlite storage if required
		d['secret_id'] = int(input(f"SecretID for {devel.AUTHORITY_NAME} (0x????????????) "),0).to_bytes(6,'big')

		try:
			self.ballots[devel.QUESTION][(ballot_server_addr, ballot_server_port)] = d
		except KeyError:
			self.ballots[devel.QUESTION] = {(ballot_server_addr, ballot_server_port): d}

		print(f"Added ballot @{ballot_server_addr}:{ballot_server_port} for question:\n\t{dec(devel.QUESTION)}")	# TODO persistent storage with sqlite
	
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
			trustees = self.ballots[question][ballotter]['trustees']
			for t in trustees.keys():
				try:				STATS[t]
				except KeyError:	STATS[t] = trustees[t]

			#print(f"{list(trustees.keys()) = }")
			voter_id = await voter_full_id( self.voter_id, list(trustees.keys()), STATS )
			answer = get_answer( question ) if answer is None else answer
			secretID = self.ballots[question][ballotter]['secret_id']
			port = self.ballots[question][ballotter]['poll_port']
			print(f"will submit {answer} to {ballotter[0]}:{port} as {voter_id} with SecretID {hex(int.from_bytes(secretID,'big'))}")
			try:
				reader, writer = await asyncio.open_connection(ballotter[0], port)
				try:
					for value in (voter_id, secretID, answer):
						await send_bytes( writer, value )
					#print("all values sent, waiting for confirmation ID")

					verification_key = int.from_bytes(await recv_bytes(reader),'big')	# verification ID as per poc.py
					if not verification_key:
						print("""ERROR: vote could could not be cast ; possible causes include :
	- your vote was already recorded
	- there was a TrustAuthority problem""")
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
	await V.register_ballot( (devel.BALLOT_SERVER, devel.PORT_HTTP) )
	await V.submit_vote()

if __name__ == '__main__':
	from sys import argv
	try:
		voter_id = enc(argv[1])
	except IndexError:
		voter_id = enc(input("Voter ID: "))
	asyncio.run( main( voter_id ) )
