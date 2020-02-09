import json
import nltk
from nltk.corpus import stopwords
from fuzzywuzzy import fuzz

#Githubs I've looked at:
# Brownrout
# LJGladic (PMA alum so his code must be good)
OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

with open('gg2013.json') as json_file:
    data = json.load(json_file)

stop_words = set(stopwords.words('english'))

def unstop():
    whatever = data[0]
    data_tokens = nltk.word_tokenize(whatever)
    unstopped_sentence = []

    for t in data_tokens:
        if t not in stop_words:
            unstopped_sentence.append(t)

    print(unstopped_sentence)


def unhashtag(str):
    #if "RT " in str:
    #    str = str[str.index(':'):]
    return str.replace('#', '')


def wordIndexInTree(tree, words):
    for i in range(0, len(tree)):
        for word in words:
            if tree[i][0] == word:
                return [i, word]


def objectSearch(tree, index):
    searching = True
    compiling = True
    object = ""

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

    return object


def subjectSearch(tree, index):
    for i in range(index, 0, -1):
        if "NNP" in tree[i][0]:
            subject = ""
            for word_pair in tree[i]:
                subject = subject + word_pair[0] + ' '
            return subject


def buildRelation(text, verbs):

    text = unhashtag(text)
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    tree = nltk.chunk.ne_chunk(tagged)

    [tagIndex, verb] = wordIndexInTree(tagged,verbs)
    obj = objectSearch(tagged, tagIndex)
    subj = subjectSearch(tree, wordIndexInTree(tree, verbs)[0])
    if obj is "" or subj is None:
        return None

    return Relation(obj, verb, subj)


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
        for person in people_comb:
            if people_comb[person] > max:
                max = people_comb[person]
                winner = person

        print(winner + "won " + self.title)



class Relation:
    def __init__(self, object, verb, subject):
        self.object = object
        self.verb = verb
        self.subject = subject

    def display(self):
        print("Subject: " + self.subject)
        print("Verb: " + self.verb)
        print("Object: " + self.object)


class VoteBoard:
    def __init__(self, award):
        self.award = award
        self.candidates = {}

    def updateVote(self, curCandidate):
        if self.candidates.get(curCandidate) is None:
            self.candidates[curCandidate] = 1
        else:
            self.candidates[curCandidate] = self.candidates[curCandidate] + 1

    def displayWinner(self):
        winner = ""
        max = -1
        for candidate in self.candidates:
            if self.candidates[candidate] > max:
                max = self.candidates[candidate]
                winner = candidate

        print(winner + "won " + self.award)


def get_awards(year):
    award_words = ['Best','Motion','Picture','Drama','Musical','Comedy','Performance','Actor','Actress','Supporting','Director','Film','Feature','Screenplay','Animated','Foreign','Language','Original','Song','Television','Series','Mini'] # Mini is for 'mini-series'
    award_words_lower = [word.lower() for word in award_words]
    helper_words = ['By','In','For','A','An','-',':','Or','Made'] #TODO: remove 'for' if it's the last word in the award
    helper_words_lower = [word.lower() for word in helper_words]

    potential_award_tweets = [] # Look for tweets with award words in them
    for tweet in data:
        tweet = tweet['text'].strip(',').strip(':').strip('!').strip('.').strip('?')
        award_words_count = 0
        for token in tweet.split(' '):
            if token.lower() in award_words_lower:
                award_words_count += 1
        if award_words_count >= 3:
            potential_award_tweets.append(tweet)

    awards = []
    award_freq_dict = dict()
    for pta in potential_award_tweets:
        award_tokens = pta.lower().split(' ')
        try:
            award_start = award_tokens.index('best') #90% of awards start with best; these are the ones we will find
        except ValueError:
            continue
        at_end_award = False
        award_end = award_start
        award_ind = award_start
        award_name = ""
        while (not at_end_award):
            word = award_tokens[award_ind]
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
        awards.append(award_name)

    # Frequency voting and process partial awards

    awards = [award.replace(" -","") for award in awards]

    return set(awards)


def combine_awards(awards_list):
    awards_comb = {}
    awards_list = sorted(awards_list, key=len, reverse=True)

    for tweet in awards_list:
        found = False
        for title in awards_comb:
            if tweet in title:
                awards_comb[title] = awards_comb[title] + 1
                found = True
                break
        if not found:
            awards_comb[tweet] = 1

    return awards_comb


def combine_people(people_list):
    people_comb = {}
    people_list = sorted(people_list, key=len, reverse=True)
    total = len(people_list)

    for tweet in people_list:
        found = False
        for title in people_comb:
            if tweet in title:
                people_comb[title] = people_comb[title] + 1
                found = True
                break
        if not found:
            people_comb[tweet] = 1

    host_list = []
    cutoff = total*.10  # 1/4 of mentions
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
            peopleArr.append(subject)

    return peopleArr


if __name__ == "__main__":

    i = 0
    hostTweets = []
    winTweets = []
    winWords = ["won", "wins"]
    for temp in data:
        #temp = data[i]
        for wW in winWords:
            if " " + wW + " " in temp['text']:
                winTweets.append(temp)
                break
        if " host " in temp['text']:
            hostTweets.append(temp)
        #i += 1

    peopleList = find_people(hostTweets)
    print(peopleList)

    cleanRelation = []

    for i in range(0, len(winTweets)):
        text = winTweets[i]['text']
        relation = buildRelation(text, winWords)

        #print(str(i) + ": " + text)

        if relation is not None:
            cleanRelation.append(relation)

    # awardList = []
    # for award in awardList:
    #     voteBoard = VoteBoard(award)
    #
    #     for relation in cleanRelation:
    #         # relation.display()
    #         if voteBoard.award in relation.object:
    #             voteBoard.updateVote(relation.subject)
    #
    #     voteBoard.displayWinner()





    awards = get_awards('2013')
    compiled_awards = combine_awards(awards)
    print(compiled_awards)

    award_array = []
    for award in OFFICIAL_AWARDS_1315:
        award_array.append(Award(award))
    #voteBoard = VoteBoard(award)

    # fuzzywuzzy info https://www.datacamp.com/community/tutorials/fuzzy-string-python
    for relation in cleanRelation:
        max = -1
        most_likely = "garbage"
        for award in award_array:
            # TODO :: TEST WHICH FUZZ METHOD IS MOST ACCURATE
            fuzz_val = fuzz.token_set_ratio(award.title.lower(), relation.object.lower())
            if max < fuzz_val:
                max = fuzz_val
                most_likely = award
        most_likely.people.append(relation.subject)

    for award in award_array:
        award.findWinner()

    # voteBoard.displayWinner()

#TODO
# 2. Subject finder defintely is not getting movies correctly
# 4. Kristen Wiig and Will Ferrell are creating a weird host error due to their presentation speech
# 5. Add other verbs
# 6. Mess with fuzz logic

#Alex TODO
#Finding awards:
# 1. At some point convert everything to lowercase
# 2. Write regex award finder because I don't trust relations
# 3. Replace combiner to use closest fuzz logic and not in

#Finding winners:
# 3. Create cleaner of some sort to get award titles out of objects
    #Filter for award words and helper awards starting from word 1
    #Use list of official awards
# 4. Combine subject names (during voting or whatever process we choose)
    #Probably create a dictionary associating full actor names with lists of awards
    #Check for last names, and add them to the dictionary entry of the full name

    #Currently using a sort by length as a cheeky way to place full names before first or last names

#Finding Hosts:
# 1. Clean host names by removing extra space and lowercasing


