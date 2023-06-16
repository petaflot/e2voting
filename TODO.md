There are a bunch of things to improve.

See TODO keyword in code ; note that there is "enough" redundancy there, so grepping and counting the number of TODOs will yield a number higher than the number of features required

* message authentication https://docs.python.org/3/library/hmac.html#module-hmac
* user-friendly GUI App for the Voters and ballot_invites_client
* ballot_invites_client should be able to generate printed labels with the partial hash (ie. QR-code) and the sequence number ; this is the scenario where a voter's identity is verified *in persona* ; in this case the critical duration where a replay a spoofing attack can be effective is very much increased (establishing a secure and authenticated communication chanel is therefore prefered but this may not always be possible).
* if a secured and authenticated communication channel is established between a Voter and BallotMiddleMan, Voter client can do the job of ballot_invites_client
* improve the protocol slightly so the invite client can work (if desired, see inline TODO relative to logging and the identity of the client inside of invites_callback)
* code styling (even though I _hate_ using spaces for indentation)
