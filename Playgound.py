import json
import nltk
from nltk.corpus import stopwords

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
    return str.replace('#', '')


def wordIndexInTree(tree, word):
    for i in range(0, len(tree)):
        if tree[i][0] == word:
            return i

def objectSearch(tree, index):
    for i in range(index, len(tree)):
        if "NNP" in tree[i][0]:
            object = ""
            for word_pair in tree[i]:
                object = object + word_pair[0]
            return object

def subjectSearch(tree, index):
    for i in range(index, 0, -1):
        if "NNP" in tree[i][0]:
            subject = ""
            for word_pair in tree[i]:
                subject = subject + word_pair[0]
            return subject


def buildRelation(text, verb):
    text = unhashtag(text)
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    tree = nltk.chunk.ne_chunk(tagged)

    windex = wordIndexInTree(tree, verb)
    obj = objectSearch(tree, windex)
    subj = subjectSearch(tree, windex)
    return Relation(obj, verb, subj)


class Relation():
    def __init__(self, object, verb, subject):
        self.object = object
        self.verb = verb
        self.subject = subject

    def display(self):
        print("Subject: " + self.subject)
        print("Verb: " + self.verb)
        print("Object: " + self.object)


if __name__ == "__main__":

    i = 0
    winTweets = []
    while len(winTweets) < 50:
        if " won " in data[i]['text']:
            winTweets.append(data[i])
        i=i+1

    print(winTweets[26])
    text = winTweets[26]['text']

    relation = buildRelation(text, "won")
    relation.display()





