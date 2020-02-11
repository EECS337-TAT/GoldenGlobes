'''Version 0.35'''
import json
import re
import string

import nltk
from nltk.corpus import stopwords
from fuzzywuzzy import fuzz
from imdb import IMDb

#Githubs I've looked at:
# Brownrout
# LJGladic (PMA alum so his code must be good)

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

# IMDb Helper
ia = IMDb()

with open('gg2013.json') as json_file:
    data = json.load(json_file)

stop_words = set(stopwords.words('english'))

helper_words = ['By','In','For','A','An','-',':','Or','Made','Any']
helper_words_lower = [word.lower() for word in helper_words]
award_words = ['Best','Motion','Picture','Drama','Musical','Comedy','Performance','Actor','Actress','Supporting','Leading','Role',
               'Director','Movie','Film','Feature','Screenplay','Animated','Foreign','Language','Original','Song','Score',
               'Television','TV','Series','Mini','Mini-Series','Miniseries','Limited']
award_words_lower = [word.lower() for word in award_words]
#A comprehensive list of any words that appear in an award but don't indicate that it is an award
helper_words = ['By','In','For','A','An','-',':','Or','Made','Any','Adapted'] # 'Adapted is an oscars term so it appears in helpers
helper_words_lower = [word.lower() for word in helper_words]

# CLASSES START HERE
#
#
class Award:
    def __init__(self, title):
        self.title = title
        self.people = []

    def findWinner(self):
        people_comb = {}
        people_list = sorted(self.people, key=len, reverse=True)

        for tweet in people_list:
            found = False
            for title in people_comb:
                if tweet.lower() in title:
                    people_comb[title] = people_comb[title] + 1
                    found = True
                    break
            if not found:
                people_comb[tweet.lower()] = 1

        max = -1
        winner = ""
        attempt = 0
        while winner == "" and attempt < 5:
            for person in people_comb:
                if people_comb[person] > max:
                    max = people_comb[person]
                    winner = person

            winner_clean = movie_person_cleaner(winner, self.title)
            if winner_clean == "":
                people_comb[winner] = 0
            else:
                winner = winner_clean
            attempt = attempt + 1

        print(winner + " won " + self.title)
        return (self.title, winner)


class Relation:
    def __init__(self, object, verb, subject):
        self.object = object
        self.verb = verb
        self.subject = subject

    def display(self):
        print("Subject: " + self.subject)
        print("Verb: " + self.verb)
        print("Object: " + self.object)
#
#
# CLASSES END HERE


# FUNCTIONS START HERE
#
#
def unstop():
    whatever = data[0]
    data_tokens = nltk.word_tokenize(whatever)
    unstopped_sentence = []

    for t in data_tokens:
        if t not in stop_words:
            unstopped_sentence.append(t)

    print(unstopped_sentence)


def unhashtag(tweet_text):
    if "RT " in tweet_text and ":" in tweet_text:
        tweet_text = tweet_text[tweet_text.index(':'):]

    return tweet_text.replace('#', '')


def wordIndexInTree(tree, words):
    for i in range(0, len(tree)):
        for word in words:
            if tree[i][0] == word:
                return [i, word]


def objectSearch(tree, index):
    searching = True
    compiling = True
    object = ""
    #print(tree)
    while searching and index < len(tree):
        if "Best" == tree[index][0]:
            searching = False
            while index < len(tree):
                if False:
                    compiling = False
                    break
                object = object + tree[index][0] + ' '
                index = index + 1
        index = index+1
    # hard removal of 'golden globes' substrings handled in main function.
    #object = object.replace('golden', '').replace('globes', '').replace('goldenglobes', '')
    return object[:-1].lower()


def subjectSearch(tree, index):

    for i in range(index, 0, -1):
        if "NN" in tree[i][0] or "NNP" in tree[i][0]:
            subject = ""
            for word_pair in tree[i]:
                subject = subject + word_pair[0] + ' '
            # hard removal of 'golden globes' substrings handled in main function.
            # subject = subject.replace('golden', '').replace('globes', '').replace('goldenglobes', '')
            return subject[:-1].lower()


def buildRelation(text, verbs):

    text = unhashtag(text)
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    tree = nltk.chunk.ne_chunk(tagged)
    try:
        [tagIndex, verb] = wordIndexInTree(tagged,verbs)
    except:
        return None
    obj = objectSearch(tagged, tagIndex)
    if obj == "":
        return None
    subj = subjectSearch(tree, wordIndexInTree(tree, verbs)[0])
    if subj is None:
        return None


    return Relation(obj, verb, subj)


def extract_names(text):
    names = []
    for sent in nltk.sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label'): # and chunk.node == "PERSON":
                names.append(chunk)
    return names
"""
def get_nominees(year):
    official_awards = OFFICIAL_AWARDS_1315.copy()




def get_awards(year):

    potential_award_tweets = [] # Look for tweets with award words in them
    for tweet in data:
        # Punctuation and extra spaces r bad so purge it aggressively unless it is a hyphen
        tweet = tweet['text'].replace('  ',' ')
        for punct in [',',':','!','.','?']:
            tweet = tweet.replace(punct,'')
        #Find the award words
        award_words_count = 0
        for token in tweet.lower().split(' '):
            if token in award_words_lower:
                award_words_count += 1
        if award_words_count >= 3:
            potential_award_tweets.append(tweet)

    awards = []
    award_freq_dict = dict()
    for pta in potential_award_tweets:
        pta = pta.lower().replace('movie','motion picture') # The globes only use 'motion picture' or 'film' to refer to movies, but tweets are not so consistent
        award_tokens = pta.split(' ')
        if "best" not in award_tokens:
            continue
        award_start = award_tokens.index("best") #90% of awards start with best; these are the ones we will find
        at_end_award = False
        award_end = award_start
        award_ind = award_start
        award_name = ""
        while (not at_end_award):
            word = award_tokens[award_ind]
            if word == 'tv':
                word = 'television'
            if word.lower() in award_words_lower or word in helper_words_lower:
                award_name += word + " "
            else:
                award_end = award_ind
                at_end_award = True
            award_ind += 1
            if (award_ind >= len(award_tokens)):
                at_end_award = True
        award_name = award_name[0:len(award_name)-1]
        if len(award_name.split(' ')) < 3:
            continue
        if len(award_name) >= 3 and award_name[len(award_name)-3:len(award_name)] == "for": # In the sentence "(award name) for (movie or actor), the final 'for' is unwittingly tacked on as a helper word
            award_name = award_name[0:len(award_name)-3]
        if len(award_name) >= 2 and (award_name[len(award_name)-2] == " -" or award_name[len(award_name)-2] == "by"):
            award_name = award_name[0:len(award_name)-2]
        awards.append(award_name)

    # Frequency voting and process partial awards

    #awards = [award.replace(" -","") for award in awards]
    awards_comb = {}
    awards_list = sorted(awards, key=len, reverse=True)
    print('Combining similar award names and calculating frequency...')
    for award in awards_list:
        award_word_list = [w for w in award.split(' ') if w in award_words_lower]
        award_word_count = len(award_word_list)
        found = False
        for title in awards_comb:

            found_word_count = 0
            for word in award.split(' '):
                if word not in award_words_lower:
                    continue
                if word in title:
                    found_word_count += 1

            if found_word_count == award_word_count: #If every award word in award is in title, they could be the same award
            #if fuzz.token_sort_ratio(title,award) > 85:
                #if title == award:
                found = True
                awards_comb[title] = awards_comb[title] + 1

        if not found:
            awards_comb[award] = 1

    # Start using those frequencies, with some fuzzy matching as well
    removal_list = []
    for key1 in awards_comb:
        '''
        for key2 in awards_comb:
            if not ('actor' in key1 and 'actor' not in key2) and not ('actress' in key1 and 'actress' not in key2):
                if not ('actor' in key1 and 'actress' in key2) and not ('actor' in key2 and 'actress' in key1):
                    if not ('drama' in key1 and 'musical' in key2 and 'comedy' in key2) and not ('drama' in key2 and 'musical' in key1 and 'comedy' in key1):
                        if key1 != key2 and fuzz.token_set_ratio(key1,key2) >= 90: # The keys are too similar, one of them has gotta go
                            if awards_comb[key1] > awards_comb[key2]:
                                removal_list.append(key2)
                            else:
                                removal_list.append(key1)
        '''
        if ( ('actor' in key1 or 'actress' in key1) and awards_comb[key1] <= 600) or awards_comb[key1] <= 250: # Awards without actors or actresses tend to be mentioned less
            removal_list.append(key1)

    for award in set(removal_list):
        del awards_comb[award]
    print(len(awards_comb.keys()))
    return awards_comb

"""

def combine_people(people_list):
    people_comb = {}
    people_list = sorted(people_list, key=len, reverse=True)
    total = len(people_list)

    for tweet in people_list:
        found = False
    # 1. The following for loop combines people according to whichever one is the superstring.
    # This may potentially be an issue if a longer phrase is mis-identified as a person.
    # Note, this is partially due to sorting by length above.
    #    for title in people_comb:
    #        if tweet in title:
    #            people_comb[title] = people_comb[title] + 1
    #            found = True
    #            break
    #    if not found:
    #        people_comb[tweet] = 1

    # 2. UPDATE THIS DESC TO BE ACCURATE
    # The following for loop combines people according to frequency.
    # This may potentially be an issue if a nickname or similar is commonly used to reference a person.
        if " " in tweet and tweet not in people_comb:
                people_comb[tweet] = 1
        for title in people_comb:
            if title in tweet:
                people_comb[tweet] += 1
        #    elif tweet in title:
        #        people_comb[title] = people_comb[title] + 1

    #            found = True



    host_list = []
    cutoff = total*.15  # 1/4 of mentions
    for host in people_comb:
        #print(host + " :: " + str(people_comb[host]))
        if people_comb[host] > cutoff:
            host_list.append(host + " :: " + str(people_comb[host]))

    return host_list


def find_people(tweets):
    people = []

    for i in range(0, len(tweets)):
        text = tweets[i]['text']
        text = unhashtag(text)
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        tree = nltk.chunk.ne_chunk(tagged)
        people_extracted = people_in_tweet(tree)
        for person in people_extracted:
            people.append(person)

    hosts = combine_people(people)

    return hosts


def people_in_tweet(tree):
    peopleArr = []
    for i in range(0, len(tree)):
        if "PERSON" in str(tree[i]):
            subject = ""
            for word_pair in tree[i]:
                subject = subject + word_pair[0] + ' '
            peopleArr.append(subject[:-1])

    return peopleArr


def movie_person_cleaner(name, award):
    """
    if "performance" in award or "director" in award or "score" in award:
        person_results = ia.search_person(name)
        if len(person_results) > 0:
            people_accuracy = fuzz.partial_token_set_ratio(str(person_results[0]).lower(), name)
        else:
            people_accuracy = 0

        if people_accuracy < 50:
            return ""
        return str(person_results[0]).lower()

    movie_results = ia.search_movie_advanced(name)

    if len(movie_results) > 0:
        movie_accuracy = fuzz.ratio(str(movie_results[0]).lower(), name)
    else:
        movie_accuracy = 0

    if movie_accuracy < 50:
        return ""
    return str(movie_results[0]).lower()
    """
    movie_results = ia.search_movie(name)
    person_results = ia.search_person(name)

    if len(movie_results) > 0:
        movie_accuracy = fuzz.partial_ratio(str(movie_results[0]).lower(), name)
    else:
        movie_accuracy = 0
    if len(person_results) > 0:
        people_accuracy = fuzz.partial_ratio(str(person_results[0]).lower(), name)
    else:
        people_accuracy = 0

    if movie_accuracy == 0 and people_accuracy == 0:
        final_name = ""
    elif movie_accuracy > people_accuracy:
        final_name = movie_results[0]
    else:
        final_name = person_results[0]

    return str(final_name).lower()



#OG API Functions
#
#
def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    hostTweets = []
    for temp in data:
        if " host " in temp['text'] and " next " not in temp['text']:
            hostTweets.append(temp)

    hosts = find_people(hostTweets)

    hostStr = ""
    for h in hosts:
        hostStr += h + ", "
    print("Host(s): " + hostStr[:-2])

    hosts = json.dumps(hosts)
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    awards = []

    awarded = OFFICIAL_AWARDS_1315.copy()

    for aw in awarded:
        awards.append(aw)

    awards = json.dumps(awards)
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    nominees = {}

    awards = OFFICIAL_AWARDS_1315.copy()
    for aw in awards:
        nominees[aw] = "r"

    nominees = json.dumps(nominees)
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    winners = {}

    print('Finding people...')
    winTweets = []
    winWords = ["won", "wins"]
    for temp in data:
        # temp = data[i]
        for wW in winWords:
            if " " + wW + " " in temp['text']:
                winTweets.append(temp)
                break

    cleanRelation = []


    print('Building relations... (This may take a while)')
    for i in range(0, len(winTweets)):
        text = winTweets[i]['text']
        relation = buildRelation(text, winWords)

        if relation is not None:
            cleanRelation.append(relation)

    print('Finding Awards...')
    awards = get_awards('2013')
    print(awards)

    award_array = []
    for award in OFFICIAL_AWARDS_1315:
        award_array.append(Award(award))
    # voteBoard = VoteBoard(award)

    # fuzzywuzzy info https://www.datacamp.com/community/tutorials/fuzzy-string-python
    for relation in cleanRelation:
        max = -1
        most_likely = "garbage"
        for award in award_array:
            # TODO :: TEST WHICH FUZZ METHOD IS MOST ACCURATE
            fuzz_val = fuzz.partial_token_sort_ratio(award.title.lower(), relation.object.lower())
            if max < fuzz_val:
                max = fuzz_val
                most_likely = award

        ungolden = relation.subject.replace('golden', '').replace('globes', '').replace('goldenglobes', '')

        most_likely.people.append(ungolden)

    for award in award_array:
        tempArr = award.findWinner()
        winners[tempArr[0]] = tempArr[1]
    print(winners)
    winners = json.dumps(winners)
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here

    """ presenters = {}
    awards = OFFICIAL_AWARDS_1315.copy()
    for aw in awards:
        presenters[aw] = "r"
    """

    official_awards = []
    official_award_punct_dict = dict()
    if (year == 2013):
        official_awards = OFFICIAL_AWARDS_1315.copy()
    # elif (year == 2018):
    #    official_awards = OFFICIAL_AWARDS_1819.copy()
    # elif (year == 2018):
    #    official_awards = OFFICIAL_AWARDS_1920.copy()
    for i in range(0, len(official_awards)):
        for punct in string.punctuation:
            official_awards[i] = official_awards[i].lower().replace(punct, "")
            official_award_punct_dict[official_awards[i]] = OFFICIAL_AWARDS_1315[i]
    potential_presenter_tweets = []
    presenter_regex = re.compile('.+(are )?present(er|ed|ing|s|\s).+')
    for tweet in data:
        tweet = tweet['text'].lower()
        for punct in string.punctuation:
            tweet = tweet.replace(punct, "")
        if re.match(presenter_regex, tweet) and any([word in tweet for word in award_words_lower]):
            potential_presenter_tweets.append(tweet)

    shortened_award_names = dict()
    short_award_name_words = ['best', 'actor', 'actress', 'supporting', 'drama', 'musical', 'comedy', 'television',
                              'miniseries', 'animated', 'foreign', 'song',
                              'score', 'screenplay', 'director']
    for award in official_awards:
        short_string = ""
        for word in short_award_name_words:
            if word in award and word in short_award_name_words:
                short_string += word + " "
        shortened_award_names[short_string] = award

    presenters = dict()

    award_tweet_mappings = dict()
    pre_present_trees = []
    for ppt in potential_presenter_tweets:
        ppt = ppt.replace('the nominees for', '').replace('for best', 'best')
        if 'best ' not in ppt or ' present' not in ppt or ppt.index('best ') < ppt.index(' present'):
            continue
        # Find the award name
        ppt_tokens = ppt.split(' ')
        best_ind = ppt_tokens.index('best')
        # present_index = ppt_tokens.index('present')
        award_name = ""
        for i in range(best_ind, len(ppt_tokens)):
            if ppt_tokens[i] in award_words_lower and ppt_tokens[i] != "motion" and ppt_tokens[i] != "picture":
                award_name += ppt_tokens[i] + " "
            elif ppt_tokens[i] not in helper_words_lower:
                break
        max_similarity = 0
        max_len = 0
        best_key = ""
        for s in shortened_award_names.keys():
            similarity = fuzz.token_set_ratio(s, award_name)
            if best_key == "" or (similarity >= max_similarity and len(s) >= max_len):
                max_similarity = similarity
                max_len = len(s)
                best_key = s
        award_tweet_mappings[shortened_award_names[best_key]] = award_name
        presenter_1_regex = re.compile('([A-Z][a-z]+)\s([A-Z][a-z]+)')
        presenter_2_regex = re.compile('([A-Z][a-z]+)\s([A-Z][a-z]+)\s(And)\s([A-Z][a-z]+)\s([A-Z][a-z]+)')
        ppt_pre_present = ppt[0:ppt.index(' present')]
        ppt_names = ""
        ppt_pre_present = ' '.join([token.capitalize() for token in ppt_pre_present.split(' ')])
        if re.match(presenter_2_regex, ppt_pre_present):
            ppt_search = re.search(presenter_2_regex, ppt_pre_present)
            ppt_names = [ppt_search.group(1) + " " + ppt_search.group(2),
                         ppt_search.group(4) + " " + ppt_search.group(5)]
            pre_present_trees.append(ppt_names)
            presenters[official_award_punct_dict[shortened_award_names[best_key]]] = ppt_names
        elif re.match(presenter_1_regex, ppt_pre_present):
            ppt_search = re.search(presenter_1_regex, ppt_pre_present)
            name = ppt_search.group(1) + " " + ppt_search.group(2)
            if 'rt' in name[0:3].lower():
                continue
            pre_present_trees.append(name)
            presenters[official_award_punct_dict[shortened_award_names[best_key]]] = name

    presenters = json.dumps(presenters)
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return



def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    year = 2013
    theHosts = get_hosts(year)



    get_awards(2013)

    get_nominees(2013)

    winner = get_winner(2013)


    get_presenters(2013)


    return

if __name__ == '__main__':
    main()
