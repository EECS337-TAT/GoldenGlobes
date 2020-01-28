import json
import nltk
from nltk.corpus import stopwords

with open('gg2020.json', 'rb') as f:
    data = f.readlines()


if __name__ == "__main__":
    sentence = "Hello World"
    tokens = nltk.word_tokenize(sentence)
    print("Hello World")
    print(tokens)


