#
# a workaround because I can't get quart to run yet
#
import pendulum
AUTHORITY_NAME = b'ballot0'
QUESTION = b'42?'
POLL_OPEN_FOR = {'days': 1}
POLL_OPEN = ( pendulum.now('Europe/Paris'), pendulum.now('Europe/Paris').add(**POLL_OPEN_FOR) )
# wether to publish results before the ballot is closed
POLL_EARLY_RESULTS = True

import constants
PORT_POLLING = constants.PORT_POLLING
PORT_HTTP = constants.PORT_HTTP
BALLOT_SERVER = constants.LISTEN

# all the competitors this ballot server is aware of (same question)
# beware of things like geographic boundaries
BALLOT_COMPETITORS = ()

trustees = [ l.rstrip(b'\n') for l in open('trustees.list','rb').readlines() ]
TRUSTEES = {( *t.split(b'\t',2)[:2], ): {'alias': t.rsplit(b'\t',1)[-1]} for t in trustees}
