import json
import nltk
from nltk.corpus import stopwords
from nltk.tree import *

#Githubs I've looked at:
# Brownrout
# LJGladic (PMA alum so his code must be good)

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


if __name__ == "__main__":

    i = 0
    winTweets = []
    winWords = ["won", "wins"]
    while len(winTweets) < 1000:
        temp = data[i]
        for wW in winWords:
            if " " + wW + " " in temp['text']:
                winTweets.append(temp)
                break
        i += 1



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

    voteBoard = VoteBoard("Song")

    for relation in cleanRelation:
        #relation.display()
        if voteBoard.award in relation.object:
            voteBoard.updateVote(relation.subject)

    voteBoard.displayWinner()


    """ 
    for i in range(0, len(winTweets)):
        text = winTweets[i]['text']
        relation = buildRelation(text, "won")

        print(str(i) + ": " + text)

        if relation is None:
            print("NONE")
        else:
            relation.display()
            """

    #relation.display()

    #for i in range(20, 30):
    #    text = data[i]['text']
    #    print(text)
    for tweet in get_awards('2013'):
        print(tweet)

#TODO
# 2. Check if Subject finder can even get movies. IF NOT RETUNE
# 5. Add other verbs

#Alex TODO
#Finding awards:
# 1. At some point convert everything to lowercase
# 2. Write regex award finder because I don't trust relations

#Finding winners:
# 3. Create cleaner of some sort to get award titles out of objects
    #Filter for award words and helper awards starting from word 1
    #Use list of official awards
# 4. Combine subject names (during voting or whatever process we choose)
    #Probably create a dictionary associating full actor names with lists of awards
    #Check for last names, and add them to the dictionary entry of the full name


