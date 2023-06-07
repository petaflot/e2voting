# e2voting
An attempt to make a clear, concise (and therefore cheap) e-voting system


*e-voting* is usually seen as something that seems straightforward but yet quite tricky when one looks into the details. 

Besides security (where e-voting is often lamer than traditional voting), cost is often argued to be a major setback. This approach aims to fix these problems, and more. Security, trust and cost are so closely related that we will not even try to categorize each issue.

It is interesting to note that the core of the code (the part that really matters) basically amounts to some 15-20 lines. So it's **very** short. Security doesn't only depend on the code though, there's a substantial part of *reverse social engineering* that I believe makes this entire concept really strong. I would really appreciate comments, especially if I'm wrong.

# Problems with voting mechanisms (traditional and electronic)

* **complexity and missing transparency**: these are probably the most important problems, especially with electronic voting ; this will not be discussed as a whole, but rather broken down into sub-parts, just keep on reading.
* **compiler trust**: compiling the software is one thing, compiling results is another. The former is a part of *installation validation*, while for the latter it boggles down to counting the votes and compiling the results in a way that is easy to read (number of *'Yes'* and *'No'* votes, number of abstentees, and so on) ; the current mechanisms allows individual voters to verify their vote is kept untampered with until the ballot is closed and deemed valid. It is also made possible for observers to make a statistical[^distribution] analysis of the votes (number of votes, choices) with a brute-force approach[^bruteforce] ; the list of electors is public (this is fact is not very different than a phone book, or checking the names on the mailboxes along a street ; this allows for a form of peer verification).
* **blank votes** are usually unaccounted for : this makes a lot of people unhappy ; furthermore, it is generally not possible to request answers beyond the scope of *yes* or *no*. The current paradigm fixes both of these issues, while encouraging people to submit their vote even if they have no opinion or disagree entirely with the object because it helps preventing their vote from being stolen.
* **software validation**: computer software is usually not understood by the majority of voters, making it close to impossible for them to review the code : code has to be well segmented and as simple as possible when it comes to the critical parts.
* **installation validation**: the computer systems and delivery chain must be trusted ; the infrastructure must be simple to set up, cheap, and the results must be verifiable. Here, a mechanism allows individual voters to verify their votes have been accounted for, all while preserving confidentiality ; this opens a door to a form of brute-force approach that allows harvesting more accurate results than publicised numbers yet this still doesn't break the confidentiality clause (see *compiler trust* above).
* **delivery validation**: it is bad if someone can steal someone else's vote ; if the victim is then unable to vote (and can be aware of it and therefore make it publicly known) it's not dramatic[^spoofing]. The same applies if a voter never receives its credentials and is therefore unable to cast his vote.
* **data security**: using databases and shifting data from one system to another is prone to data loss, data corruption and data injection by various attack vectors. The present system avoids this problem by keeping all sensitive data in a single process that runs from the beginning of the ballot to its very end ; only a very restricted family of attack vectors requiring direct memory access are able to compromise the data and those capable of "surgically" data alteration without compromising anything else are almost non-existent. In case the process dies, the data is considered to be corrupted[^distribution].

[^bruteforce]: In the current paradigm, vote confidentiality can be attacked mainly with a brute-force approach ; however, due to the architecture of the system, the data gathered can only be used to gather data for statistical analysis. The current paradigm uses this *as a feature*, thus rendering other types of attacks less stealth and therefore less effective.

[^spoofing]: It's not dramatic in the sense that is basically impossible to prevent it : however, keeping track of spoofing occurrences is important as it may indicate a flaw in the delivery process ; such statistics also allows communities to determine whether spoofing has a significant influence on the ballot.

[^distribution]: Using distributive computing makes for cheaper systems, lessens the influence of corrupted systems or officials, all while leveraging the power of statistical analysis for software validation, installation validation, compiler trust, delivery validation. This also makes attacks on the data in systems memory very expensive and unpractical.

# Main principle of operation, the paper analogy

To make an e-voting system acceptable by the public, it must be simple enough to be understood by the majority. A working paper analogy is needed:

* electors receive an invitation to vote, which may or may not include a paper ballot. This invitation is generated by each community (village, town or district) and the elector list is public.
* each elector goes to the polling office, shows his credentials (invitation), receives (if that was not done before) a paper ballot. The paper ballot is comprised of two parts, each with the serial number of the paper ballot. The elector may write his answer on one part (preferably on both), and put it in the box.
* at any time, official result statistics are available (this is optional).
* at any time, a voter can use the serial number on his receipt to verify his vote was not altered.
* at the end of the ballot (or as soon as results are made available), voters and observers can:
	* relate to their surroundings : in a small village or part of town, people usually have an idea what the general tendency will be
	* "attack" the database to gather statistically data, enabling them to validate (or not) the *local* official results (they can try to randomly"pick" votes from the ballot box, gathering results and sharing them to increase the size of the data pool. It can also be decided that this part of the data is open to anyone : statistics require less resources (computational and at a networking level) ; at this stage the data that allows tracing a vote to a particular individual has anyways been deleted and cannot be recovered.
	* gather result data from each community to verify the global (state-, country- and world-wide) results match the real data ; this may also be done with a statistical approach, results may be compiled with a bottom-to-top approach (city data compiled from district data, state data compiled with data from cities and villages, national data compiled from state data, etc.) : this is recommended and allows building a trusted network of data compilers.
* voters and observers hang a flag at their window, for example green when that person is happy with the way his or her vote was processed, red for cases of fraud ; now anyone walking in the street can see at once not the result of the vote, but if the process went smoothly.

## How it would really work

Few people like to copy and go through pages of printed material. Printed material is also very prone to error, mostly when it comes to making hand copies.

The current approaches works with both methods : the main recommendation is that the serial numbers of paper ballots are computer-generated and the results made available through a machine-readable process (in fact, this strengthens the system by making statistical analysis easier, as well as making it easier for voters to very their votes have not been tampered with.

## Cost

The code does not yet deal with the full chain of events required to have a practical voting process. However, it can be expected that a single RaspberryPi-type computer could serve as a master host for a few thousand people at a time (a rough estimate tells me I wouldn't expect anything in the 100k users range to have decent performance). With a fairly conservative figure of 10k users, hardware, network and associated costs being at most some 500$, the cost of the infrastructure is around 5¢/voter for the base service[^othercosts], which seems totally acceptable.

[^othercosts]: Other costs have to be taken into account, such as the statistical analysis of the results and other *"democratic"* costs (writing laws etc.) but all this is distributed, sometimes made by benevolent benefactors, sometimes by highly-rewarded lobbyists, so overall it's really hard to give a figure without accurately defining first what these cost should be include.

Compared to an estimate for Switzerland[^zurichvoting] of around CHF 100.-/voter (hopefully for more than a single ballot) there is definitely a margin for error here.

[^zurichvoting]: *"Appraisals assume that the implementation of e-voting in the whole country would cost 400 to 600 million CHF."* [Wikipedia](https://en.wikipedia.org/wiki/Electronic_voting_in_Switzerland#Disadvantages)


## Additional security

Since the name of a person is basically not a secret and no communication channel is 100% secure, the ballot instance (the one running the core process) may rely on a variety of sources to verify the identity of a voter when delivering the ballot "paper". Using such a mechanism implies that a ballot paper can be delivered and used when and only when **all** available sources are compliant and no communication channel is compromised in a significant way. The same applies for the instance (aka. authority) that generates the ballot "paper" and of course to the voter (it makes no sense if authorities make use of mechanisms a voter cannot trust and verify). It is not required for a voter to be known by all *Secret Providers* ; if the voter is unknown, the provider should respond with an empty string.

At this point, reading the source code makes sense : it may be best to start with the simple proof-of-concept `poc.py` that includes the basic workflow in a single file in an interractive-demo sort of way.

# Other attack vectors

Some attack vectors have not been mentioned above ; this is a good place to talk about them now.

## Man-in-the-middle attacks (MITM), phishing, spoofing

To work, such attacks would require to be done successfully **at least twice** : first in the distribution phase, giving voters a dummy address for the polling office or its numerical equivalent (possibly altering or generating dummy ballot papers IDs), then again in the verification phase. Chances to succeed continuously - even for a limited number of voters - while avoiding detection during the entire duration of the ballot is highly unlikely.

Subtypes and related attacks such as *whale-phishing* or *spear-phishing* are just as unlikely.

## DDoS attacks

The system would be very slow, people just couldn't vote, so it would be very obvious. See also [^distribution].

## Ransomware

You'd really need to pay a lot of people, for a voting process this is not very realistic. Giving jobs to people is likely to be more efficient.

## Password attack, URL interpretation

Just like MITM and phishing, but harder: while it is technically possible to brute-force ballot paper IDs and user credentials, it is basically impossible to successfully take-over a significant number of votes without being unnoticed.

## SQL injection

Can only be done at the voters list level, in case it relies on such a database. See also the note about distribution[^distribution], as it would require to break in a variety of different, independent systems.

## Session hi-jacking

There are basically no sessions to hi-jack : a voter sends his credentials and ballot ID along with his vote, receives a verification key, and the Session is closed. Any subsequent session is "send verification key, receive vote value" and ends there.

## Trojan horses, malware attacks, XSS attacks, eavesdropping, drive-by and other web attacks

I mean, you get to compromise a very large number of systems of an entire community for a continuous duration ; although it doesn't have to last for weeks on end it is very unlikely to avoid detection.


## Birthday attack, brute-force attacks

At his stage, probably the most interesting one to mention : the main *hashing* algorithm is memory addresses (which people can share or collect "randomly"[^bruteforce] in order to ensure the validity of the data) that - by design - can only yield unique values. Furthermore, as many safety elements (in addition to the voters' name which isn't really safety anyway) can be added as desired and these can be gathered from a number of sources each with limited trust (or whose communication channels are potentially untrusted)

## I'm-not-who-I-pretend-I-am

This one is tricky : a troll sets up a dummy ballot server and uses it to query each TrustAuthority for each voter, then uses this data to submit votes on other (legit) ballot servers (providing it has the required SecretID for each voter : this is a decent failsafe, but is it enough?)

It is not sure how to fully get around that issue : 
* should a TrustAuthority response depend on the poll question? probably yes
* should a TrustAuthority response depend on the host:port values for a ballot server? definitely yes : this way, generic searches are done **in reverse** and pushed to the ballot server

At this point, it makes sense to consider dropping TrustAuthorities altogether.


# Notes
## In general...

An algorithm can be expressed (or defined) in a variety of languages, but an algorithm does not express (or define) a specific language. Therefore, a language a language can express (or define) a multitude of algorithms so a language is a higher-level structure than an algorithm.

## Security
It is recommended to setup a *somewhat secure and authenticated* (ie. ssh/VPN) transmission channel between every instance ; this MAY be included in the future.

## Polling options
It has been debated wether a limited set of options should be made available to a voter ; reasons are both technical and "ethical" to **not** limit the user in valid choices. Voters are responsible to cast their vote for the correct entity. In some cases, ballot instances may decide to use a vector-based approach to concatenate values such as "Yes", "yes", "YES" into one.

## Did you know?
Early Sunday November 27, 2022, the author woke up suddenly : while doing some permutations in a dream, he had realized he may have put his finger on something actually useful. It was just short of 4am. He immediately got up to take a few notes for the following 2 hours or so, took some more rest and then spent the rest of the day making a proof-of-concept code that would actually execute (the morning notes were little more than pseudo-code).


