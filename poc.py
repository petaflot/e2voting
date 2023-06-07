#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap

def voter_full_id( voter_name, providers ):
	"""
		a helper function known by everybody ; simply concatenate hashes
	"""
	return b''.join([ provider.hash( voter_name ) for provider in providers ])


class LocalBallot:
	"""
		each town/community SHOULD have its own process running for the duration of the ballot and a little longer 
		to allow people to verify their results and various instances to concatenate the data from each source

		this is less than 30 lines (comments and blank lines stripped) of very straightforward code, and basically
		just 10 lines of actual code
	"""
	def __init__( self, authority, question, voters, secret_providers = None, encoding = 'utf-8' ):
		self.authority = authority	# just a name/reference, used for data gathering
		self.question = question	# it's good to know what question we're answering
		self.encoding = encoding	# encoding everything to ensure consistency of the data

		self.total_possible_votes = len(voters)
		self.invites = { voter_full_id(v, secret_providers): id(v) for v in voters}	# id(v) is not used, it's just a placeholder that may be used for verification

		if len(self.invites) != self.total_possible_votes:	# should be unnecessary, just a safety measure
			raise Exception("INIT: Number of invites does not match number of electors ({len(self.invites)}/{len(self.total_possible_votes})")
		print(f'''Vote is open to {len(voters)} ; the question is : "{self.question}"''')	# cosmetic

		self.result = {}


	def request_auth( self, voter ):
		"""
			generate personalized ballot paper ("bulletin de vote")
		"""
		return hex(id(self.invites[voter]))

	def submit_vote( self, voter, secret, value ):
		"""
			the few CPU cycles (and associated network traffic) it takes this function to execute are the _only_ 
			places where voter/vote can be sniffed (matched)
		"""
		if id( self.invites[ voter ]) == secret:
			self.invites.pop( voter )	# in some rare cases, may also raise KeyError
			self.result[ secret ] = value
			return id(self.result[secret])
	
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


"""
this is basically all for the functional code ; the rest is just interface stuff and is not critical
"""


class SecretInstance:
	"""
		really, that is just a fancy way to say "there is a function that will make a pseudo-secret 'hash' of some sort when given publicly known data"

		it is suggested to use regular cryptography with keys and certificates or another trust and validation mechanism to authenticate the parties ; 
		however there are a large variety of methods available and we will not discuss them here.

		SecretInstance objects have a hash() method, called three times, in order:
		- once by the ballot process when it is instantiated and it build the voters list
		- a second time when generating the balot "papers" (by the process generating these, either by print or through a web service or equivalent)
		- a third time by each voter upon ballot/vote submission

		this ensure a high level of anonymity and high security
	"""
	def hash( self, name ):
		try:				return self.table[name]
		except KeyError:	return b''



if __name__ == '__main__':
	"""
		very basic zero-privacy example interface
	"""
	# elements of this list must be unique, and are publicly known
	voters = {
		b'alice',
		b'bob',
		b'charles',
	}

	class NameProvider(SecretInstance):
		"""
			sort of a dummy thing.. not strictly necessary (we need at least _one_ provider and no collisions)

			adding the name provider as a SecretInstance makes code cleaner and easier to understand but in fact there's
			even more privacy if that's not included
		"""
		def hash( self, name ):
			return name

	class SecretProvider0(SecretInstance):
		from hashlib import md5	# this is intentionally insecure ;-)
		def hash( self, name ):
			return self.md5( name ).digest()

	class SecretProvider1(SecretInstance):
		table = {
				b'alice': b'InWonderland',
				b'bob': b'IsASponge',
			}

	class SecretProvider2(SecretInstance):
		table = {
				b'charles': b'Paranoid, has own auth service',
				b'alice': b"she's charle's friend, too",
			}
	
	# this list is public, known by the ballot instance/server and every voter
	# in real life, these will be accessible through TCP/IP or something equivalent
	secret_providers = (
			NameProvider(),
			SecretProvider0(),
			SecretProvider1(),
			SecretProvider2(),
			# etc.., as many as required
		)

	b = LocalBallot(
			authority = "Cryptoville",
			question = "What is the answer to Life, the Universe and Everything?",
			voters = voters,
			secret_providers = secret_providers,
		)
	

	print("Hint: press ctrl+d to exit loops")


	print("--- Generation of credentials (sent in batches per voter preference or on-demand) ---")
	for v in voters:
		try:
			print(f'''Ballot 'paper' ID: {b.request_auth( voter_full_id(v, secret_providers) )} for {v}''')
		except KeyError:
			# this is just here for the example
			print(f'''ERROR: cannot get ballot paper for {v}''')


	print("--- Loop: votes submission ---")
	while True:
		try:
			v = bytes( input("Voter name: "), b.encoding )
			r = b.submit_vote(
					voter = voter_full_id( v, secret_providers ),
					secret = int( input( "Ballot ID (hex): " ), base=0 ),
					value = bytes( input("Your answer: " ), b.encoding ),
				)
		except KeyError:
			print(f'''ERROR: could not process vote for "{v}" (already voted or not in list)''')
		except EOFError:
			print("\nBallot was ended!")
			break
		else:
			print(f'''Verification ID: {hex(r)} (voter: "{v}")''')

	print("--- Vote verification ---")
	while True:
		print( "Is ballot valid?", b.ballot_integrity_check(), "(should be zero)" )
		try:
			print( "You voted: ", b.verify_vote(
					secret = int(input("Ballot ID: "), base=0),
					index = int(input("Verification ID: "), base=0) ),
				"; if this is not correct, please shout out loud to complain."
				)
		except KeyError:
			print("ERROR: not in votes list")
		except EOFError:
			break
	
	print("--- Vote results ---")
	print(b.concatenate_votes())
