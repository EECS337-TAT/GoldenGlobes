import json
import nltk
from nltk.corpus import stopwords

with open('gg2020.json', 'r') as f:
    data = f.readlines()

stop_words = set(stopwords.words('english'))

if __name__ == "__main__":
    sentence = "Hello World"
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    print("Hello World")
    print(tagged)
    print(tokens)
    print(data[0])
    whatever = data[0]
    data_tokens = nltk.word_tokenize(whatever)

    unstopped_sentence = []

    for t in data_tokens:
        if t not in stop_words:
            unstopped_sentence.append(t)

    print(unstopped_sentence)


