#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap
import asyncio

from shared_funcs import send_bytes, recv_bytes, enc
from constants import INVITE_ERROR_INT
"""
	simple client to get invites (ballot papers) for a given voter
"""

def print_invite( userID, inviteID ):
	"""

		pretty prints an invite token

		TODO: generate qrcode, print label... whatever

	"""
	if inviteID == INVITE_ERROR_INT:
		print(f"ERROR: no invite available for {userID} ; did you use the full, concatenated ID?")
	else:
		print(f"{hex(inviteID) = }")

class BallotInvitesClient:
	def __init__(self, host, port):
		self.host = (host, port)

	async def get_invite( self, userid ):
		reader, writer = await asyncio.open_connection(self.host[0], self.host[1])
		await send_bytes( writer, userid )
		#print("sent", userid)
		inviteID = await recv_bytes( reader )
		#print("received", inviteID)
		return inviteID

	async def answer_requests(self):
		while True:
			userID = enc(input("Request invite for: "))
			print_invite( userID, int.from_bytes( await self.get_invite( userID ), 'big') )

async def main( host, port ):
	BIC = BallotInvitesClient( host, port )
	await BIC.answer_requests()

if __name__ == '__main__':
	from sys import argv
	try:
		host, port = argv[1].split(':',1)
		port = int(port)
	except ValueError:
		print(f"usage: {argv[0]} <host>:<port>")
	except IndexError:
		from constants import LISTEN as host,  PORT_INVITES as port
		print(f"Connecting to {host}:{port}")


	asyncio.run( main( host, port ) )
