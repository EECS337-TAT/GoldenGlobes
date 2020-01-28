# gg-project-master-2016
Golden Globe Project Master 2016
This is Team 9's Golden Globe Project for EECS 337 at Northwestern University

Currently the PreProcessing of Tweets takes **about 1 hour** on our computers.

Requirements:
The project requires the [fuzzywuzzy](https://pypi.python.org/pypi/fuzzywuzzy) external library for Approximate String Matching

This Project also makes use of the [IMDB Alternative Interface Plaintext Files](http://www.imdb.com/interfaces)
These files are downloaded automatically and parsed with regular expressions to get a set of Actor, Actress, and Movies/TV Names

Our goal was to find the Names of Awards, the winners, nominees, and presenters of those awards and the Hosts of the show.

Our Approach was to take the tweet and find those related to Awards by using a regular expression:
We take these tweets and filter them down further into tweets related to Nominees,Winners, and Presenters
After this we took  the tweets and extracted names of People,TV shows and Movies
We then perform frequency analysis to decide which names are associated with each section of tweets for a particular award
We take the most common name as the winner and the next 4 as nominees
We take the most common 2 names associated with both Presentation and an Award as the Presenters
For host we take the 2 most common names or just most common name based on how many tweets relating to host contain the word 'and'
Additionally we incorporated a 'Most Discussed' function which returns the names of the most discussed people at that years Golden Globes
