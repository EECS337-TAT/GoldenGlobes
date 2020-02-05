import nltk

if __name__ == "__main__":
    sentence = "Hello World"
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    print("Hello World")
    print(tagged)

