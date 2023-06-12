#
# a workaround because I can't get quart to run yet
#
AUTHORITY_NAME = b'ballot0'
QUESTION = b'42?'
# wether to publish results before the ballot is closed
POLL_EARLY_RESULTS = True

# all the competitors this ballot server is aware of (same question)
# beware of things like geographic boundaries
BALLOT_COMPETITORS = ()

trustees = [ l.rstrip(b'\n') for l in open('trustees.list','rb').readlines() ]
TRUSTEES = {( *t.split(b'\t',2)[:2], ): {'alias': t.rsplit(b'\t',1)[-1]} for t in trustees}
