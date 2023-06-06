# du census au consensus

"""
    this document written just around 6am after waking up on a sunday morning.
    it was never tested.
    dim 27 nov 2022 11:44:03 CET

    pof.py contains a class, with no comments, with the minimal code.


    tranditional voting:
    PROS:
    - simple

    CONS:
    - no verification possible, based on the trust of a limited set of individuals
    - expensive processing


    blockchain can be used for voting

    PROS:
    - tracability (hard to forge)

    CONS:
    - hard to understand (not for "noobs")
    - computationally intensive
    - in the long term, only results are of interest (exponential long-term cost)

    mem-based voting

    PROS:
    - computationally cheap
    - voters can check the validity of their own vote
    - observers can statistically check the validity of the ballot (random secret/vote_value combinations should only be valid a limited number of times)
    - anyone can compile the result of regions
    - by community (state/town/street/...) it's very easy to assess that the total number of votes match the number of people allowed to vote
    - scalability
    - low cost
    - to submit votes, encryption is not strictly required
    - very simple code source, basically anyone can understand
    - hybrid (paper/e-voting can be combined)

    in paper form:
    - électeur reçoit bulletin / invitation à voter
    - au bureau, reçoit un bulletin avec numéro de série (unique) en deux parties (une à détacher et une à garder pour vérification)
    - à la fin du scrutin, avis officiel (local) publie la liste des numéros de série et des résultats

"""


#05:25 < b-jazz> I have forgotten the name of a library I used many years ago to fill up a database with a million synthetic people. the sample data   |
#                library would generate random users like "Fred Smith" at "123 Main St.; Podunk, ST 12345" data entries. But I can no longer find it   |
#                on pypi. Does this sound familiar to anyone? TIA                                                                                      |
#05:26 < JAA> b-jazz: https://pypi.org/project/Faker/ ?

# this list is public ; can contain other info such as address, birthdate... must be unique! 
voters = {
    'alice',
    'bob',
    'charles',
}

# alternatively, voters can be a dict with lists of who has vouched for who

# this number is definiteley public and kept for reference
num_voters_before = len(voters)


# register voters for ballot
# even though v is a string id(v) SHOULD be unique because it's pulled from a mutable object
ballot = { v: id(v) for v in voters}

if len(ballot) != num_voters_before:
    raise Exception("this is definitely wrong, set was changed (this should not be allowed)")

# optionally, ballot can be an item in a larger dict:
tous_les_ballots['objet du ballot'] = '...'

# initialize result dict (optionally in larger dict)
result = {}

# invitation to vote: each voter receives some data (batched)
for v in ballot:
    send_in_sealed_envelope( recipient = v, ballot = id(ballot), secret = ballot[v] )


# vote : each user sends his vote and secret, receives a confirmation
def vote( voter_name, ballot_id, secret, vote_value ):
    """
        voter_name: known and public
        secret: depends on the python process, absolutely unique in the process (by design), basically imposible to forge

        vote value can be one of:
        - True (object is accepted)
        - False (object is refused)
        - None (blank vote, ie. no opinion on the matter but care to express it)
        - integer (can be a value for a poll or free submission, can decode to a string)
    """
    if ballot.get( voter_name ) == secret:
        # very simple alternative, secret needs to be unique
        result[ secret ] = vote_value
        ballot.pop( voter_name )
        # a voter should keep this for future reference until poll is validated
        return id(result[secret]), vote_value   # meeh can only return id(result[secret]) if id guaranteed to be unique and using first form

        # this alternative is not valid, because secret is not guaranteed to be unique in this scope
        # (this depends on the exact implementation details)
        # secret is just a "computationally cheap pseudo-random value" with less collisions than
        # using a standard RNG (better distribution of values)
        #try:
        #    result[vote_value].append(secret)
        #except KeyError:
        #    result[vote_value] = [ secret ]
        #finally:
        #    ballot.pop( voter_name )
        #    # a voter should keep this for future reference until poll is validated
        #    return id(result[secret]), vote_value   # meeh can only return id(result[secret]) if id guaranteed to be unique and using first form
    else:
        raise Exception("you cannot vote")


# vote verification and publishing
def check_ballot( ballot ):
    unused_votes = len(ballot)
    total_votes = sum( len( result[k] ) for k in result )
    vote_diff = num_voters_before - ( total_votes + unused_votes )
    if vote_diff == 0:
        print("no problem so far")
    elif vote_diff < 0:
        # only very small delta is acceptable, it can _only_ be negative and may not persist once voting process is closed
        # TODO make sure program does not exit here, this would be stupid
        raise Exception("results were tampered with or are in a transient state", vote_diff)
    elif vote_diff > 0:
        raise Exception("too many votes accounted for, this is unacceptable")

def check_my_vote( ballot_id, value, secret ):
    """
        each individual can check if his vote was received and accounted for
        there MAY be double-entries, but it's very unlikely
    """
    return secret in result.get( ballot_id )[ value ]

def print_ballot_results( ballot ):
    """
        pretty uninteresting there, TODO

        for items where result is a free submission, display stats such as:
        - min/max/avg/norm/deviation
        - vector similarities (text-based comparison)
    """
    return ...
