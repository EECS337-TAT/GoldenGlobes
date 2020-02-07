import json
import nltk
from nltk.corpus import stopwords
from nltk.tree import *

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


def wordIndexInTree(tree, word):
    for i in range(0, len(tree)):
        if tree[i][0] == word:
            return i


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


def buildRelation(text, verb):

    text = unhashtag(text)
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    tree = nltk.chunk.ne_chunk(tagged)

    obj = objectSearch(tagged, wordIndexInTree(tagged, verb))
    subj = subjectSearch(tree, wordIndexInTree(tree, verb))
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

        print(winner + " won " + self.award)


if __name__ == "__main__":

    i = 0
    winTweets = []
    while len(winTweets) < 1000:
        if " won " in data[i]['text']:
            winTweets.append(data[i])
        i = i+1



    cleanRelation = []

    for i in range(0, len(winTweets)):
        text = winTweets[i]['text']
        relation = buildRelation(text, "won")

        #print(str(i) + ": " + text)

        if relation is not None:
            cleanRelation.append(relation)

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



#TODO
# 2. Check if Subject finder can even get movies. IF NOT RETUNE
# 5. Add other verbs

#Alex TODO
# 1. At some point convert everything to lowercase
# 3. Create cleaner of some sort to get award titles out of objects
    #Filter for award words and helper awards starting from word 1
    #Use list of official awards
# 4. Combine subject names (during voting or whatever process we choose)
    #Probably create a dictionary associating full actor names with lists of awards
    #Check for last names, and add them to the dictionary entry of the full name

