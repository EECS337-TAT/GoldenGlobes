import urllib2
import gzip
import json
import os
import re
import pickle 
import nltk
import time
from collections import Counter
from collections import defaultdict
from fuzzywuzzy import process, fuzz

OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
# https://en.wikipedia.org/wiki/Most_common_words_in_Englis
stoplist = set(['Netflix','Congrats','Congratulations','Congratulations!','Did','Too','TV','Movie','Golden Globes','The','I','Can','Best','So','That','You','Twitter','Golden','What','Why','Who','Best','She','He','They','Hollywood','This','And','Or','Be','To','Of','A','In','That','Have','I','It','For','Not','On','With','He','As','You','Do','At','What','Their','There','Would','All','One','My','Will','An','Or','She','Her','Say','We','They','From','By','His','But','This','So','Up','Out','If','About','Who','Get','Which','Go','Me','When','Make','Can','Like','Time','No','Just','Him','Know','Take','People','Into','Year','Your','Good','Some','Could','Them','See','Other','Than','Then','Now','Look','Only','Come','Its','Over','Think','Also','Back','After','Use','Two','How','Our','Work','First','Well','Way','Even','New','Want','Because','Any','These','Give','Day','Most','Us'])

def get_tweets_for_year(year):
    tweets = []
    with open("gg%s.json" % year) as tweet_file:
        json_object = json.load(tweet_file)
        for tweet_object in json_object:
            tweets.append((tweet_object["id"], tweet_object["text"]))
    return tweets

def parse_tweets(tweets, regexp, dictionary={}):
    '''Take Tweet and seperate out id and text, search text for regexp, if match then add to dictionary'''
    for tweet in tweets:
        tweetid = tweet[0]
        text = tweet[1]
        ##maybe add stop list before matching
        match =  re.search(regexp, text)
        if(match != None):
            extracted = match.group(0)
            dictionary[tweetid] = extracted
    return dictionary

def filter_tweets(tweets, regexp,related=True):
    '''Take Tweet and seperate out id and text, search text for regexp, if match then add to list, return list'''
    tweet_list =[]
    for tweet in tweets:
        tweetid = tweet[0]
        text = tweet[1]
        ##maybe add stop list before matching
        match =  re.search(regexp, text)
        if(related):
            if(match != None):
                 tweet_list.append(tweet)
        else:
            if(match == None):
                 tweet_list.append(tweet)

    return tweet_list

def get_people_names(tweet,nameset):
    #get ngrams in tweet, compare them to list of actors and actressss 
    # Need to fix 
    names= []
    tweetid = tweet[0]
    text = tweet[1]
    #get rid of possession e.g. Jane Doe's 
    text = re.sub('(\'s)',' ', text)
    # or Nick Jonas'
    text = re.sub('s\'','s', text)
    concurrent_capitalized_words = set(re.findall('([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+)+)',text))
    for string in concurrent_capitalized_words:
            if(string in nameset):
                names.append(string)
    return names

def get_movie_tv_names(tweet):
    #get ngrams in tweet, compare them to list of actors and actressss 
    # Need to fix 
    names= []
    tweetid = tweet[0]
    text = tweet[1]
    ####RegEX
    possible_movie_names = set(re.findall('(?:(?:(?:(?:(?:(?:[A-Z]|[0-9])(?:(?:\w*)?(?:[,:\'.!-/]*)?(?::?\w*)?)?)|A|I)\s?)+)(?:(?:(?:(?:&|(?:i|o)n|of|a(?:s|nd|n|t)?|(?:d|l)e|f?or|vs\.|to|by|la|the|with|du) )){1,2})?)+',text))
    #Not working that great
    for string in possible_movie_names:
        string = string.strip()
        if((string in movies_set) and  string not in stoplist):
                names.append(string)
    return names

##Tweet Filtering Functions       
def get_host_tweets(tweets):
    global cohost
    ##find tweets relating to hosts
    regexp = re.compile('(host(ed|ing)\s)')
    host_tweets = filter_tweets(tweets,regexp)
    num_host_tweets = len(host_tweets)
    cohost_tweets = host_tweets
    #get rid of tweets which have "should, should've"
    regexp = re.compile('(should(\'ve| have)\s)')
    host_tweets = filter_tweets(host_tweets,regexp,False)
    #get rid of tweets which have next year 
    regexp = re.compile('next year', re.I)
    host_tweets = filter_tweets(host_tweets,regexp,False)
    ####Additional Basic Logic to Figure out if Cohost or not narrow down to cohost tweets (theoretically should but both test years have cohosts)
    regexp = re.compile('and', re.I)
    cohost_tweets = filter_tweets(cohost_tweets,regexp)
    num_cohost_tweets = len(cohost_tweets)
    num_host_tweets = num_host_tweets-num_cohost_tweets
    if(num_cohost_tweets>num_host_tweets):
        cohost = True
    else:
        cohost = False

    return host_tweets

def get_winner_tweets(tweets):
    ##find tweets relating to winning
    regexp = re.compile('((?:w(i|o)n(ner|ning)?)|((?:t(ook|aking)? home))|(receiv(ed?|ing))|(award(ed)))', re.I)
    winner_tweets = filter_tweets(tweets,regexp)
    #get rid of tweets which have "should, should've"
    regexp = re.compile('(should(\'ve| have)\s)')
    winner_tweets = filter_tweets(winner_tweets,regexp,False)
    #get rid of  tweets with speculation 
    regexp = re.compile('(will|going to)')
    winner_tweets = filter_tweets(winner_tweets,regexp,False)
    return winner_tweets
###############TODO Probably Need Better Regex for nominees and presenters
def get_nominee_tweets(tweets):
    # find tweets relating to nomination
    regexp = re.compile('nomin((?:(?:at(?:ed|ion)))|ee)')
    nominee_tweets = filter_tweets(tweets,regexp)
    ##find tweets relating to winning?
    return nominee_tweets

def get_presenter_tweets(tweets):
    #find of tweets which have to do with presenting
    regexp = re.compile('present(e(d|rs?)|ing)')
    presenter_tweets = filter_tweets(tweets,regexp)
    #narrow down
    ##filter out 
    return presenter_tweets



##Tweet Dictionary Functions dict[tweetid] = names 
def award_names(tweets):
    award_regex = r"(Best(?=\s[A-Z])(?:\s([A-Z]\w+|in|a|by an|\s-\s))+)"
    award_dictionary = parse_tweets(tweets, award_regex)
    return award_dictionary

def make_dictionary(function,tweets):
    # TODO add movies_set and nicknames_set
    dictionary = defaultdict(list)
    list_tweets = function(tweets)
    for tweet in list_tweets:
        tweetid = tweet[0];
        if (get_people_names(tweet,actors_set)!= []):
                dictionary[tweetid].extend(get_people_names(tweet,actors_set))
        if (get_people_names(tweet,actresses_set)!= []):
                dictionary[tweetid].extend(get_people_names(tweet,actresses_set))
        if(get_movie_tv_names(tweet)!=[]):
                dictionary[tweetid].extend(get_movie_tv_names(tweet))
    ##eliminate duplicates in tweets
    for tweetid, name_list in dictionary.iteritems():
        dictionary[tweetid] = list(set(dictionary[tweetid]))
    return dictionary

def get_winners_dictionary(tweets):
    return make_dictionary(get_winner_tweets,tweets)

def get_nominees_dictionary(tweets):
    return make_dictionary(get_nominee_tweets,tweets)

def get_presenters_dictionary(tweets):
    return make_dictionary(get_presenter_tweets,tweets)



def get_master_award(found_awards, cutoff=25):
    frequent_appearing_awards = [found_award for found_award in found_awards if found_awards.count(found_award) > 5]
    unique_award_names = set(frequent_appearing_awards)
    print unique_award_names
    found_award_counts = Counter(frequent_appearing_awards)
    top_awards = [a[0] for a in found_award_counts.most_common(cutoff)]
    print top_awards
    ordered_by_count = [i[0] for i in found_award_counts.most_common()[::-1]]
    for award in ordered_by_count:
        best_match = process.extractOne(award, ordered_by_count[ordered_by_count.index(award)+1:], scorer=fuzz.token_sort_ratio, score_cutoff=85)
        if best_match:
            if award not in top_awards:
                print award, best_match
                unique_award_names.remove(award)

    return unique_award_names

def convert_awards_to_given_names(found_awards):
    converted_dict = {}
    for tweet_id in found_awards.keys():
        converted_dict[tweet_id] = process.extractOne(found_awards[tweet_id], OFFICIAL_AWARDS)[0]
    return converted_dict




def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    tweets = get_tweets_for_year(year)
    host_tweets = get_host_tweets(tweets)
    names = []
    for tweet in host_tweets:
        if (get_people_names(tweet,actors_set)!= []):
                names.extend(get_people_names(tweet,actors_set))
        if (get_people_names(tweet,actresses_set)!= []):
                names.extend(get_people_names(tweet,actresses_set))
    hosts = Counter(names).most_common(2)
    if(cohost):
        hosts = [hosts[0][0], hosts[1][0]]
    else:
        hosts = [hosts[0][0]]
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    awards_init = []

    if year == 2015:
        for key, value in awards_set_main.iteritems():
            awards_init.append(str(value))

    elif year == 2013:
        for key, value in awards_set_main2013.iteritems():
            awards_init.append(str(value))


    awards = [ite for ite, it in Counter(awards_init).most_common(26)]    
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here'
    
    nominees = {}
    for x in OFFICIAL_AWARDS:
        nominees[x] = []


    if year == 2013:
        for key, value in awards_set_main2013.iteritems():
            for key2, value2 in nominees_2013_main.iteritems():
                if key2 == key:
                    nominees[value].extend(value2)

    if year == 2015:
        for key, value in awards_set_main.iteritems():
            for key2, value2 in nominees_2015_main.iteritems():
                if key2 == key:
                    nominees[value].extend(value2)


    for key, value in nominees.iteritems():
        nominees[key] = [ite for ite, it in Counter(value).most_common(5)]


    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''

    winners = {}
    for x in OFFICIAL_AWARDS:
        winners[x] = []


    if year == 2013:
        for key, value in awards_set_main2013.iteritems():
            for key2, value2 in winners_2013_main.iteritems():
                if key2 == key:
                    winners[value].extend(value2)

    if year == 2015:
        for key, value in awards_set_main.iteritems():
            for key2, value2 in winners_2015_main.iteritems():
                if key2 == key:
                    nominees[value].extend(value2)


    for key, value in winners.iteritems():
        winners[key] = [ite for ite, it in Counter(value).most_common(1)]

    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''

    presenters = {}
    for x in OFFICIAL_AWARDS:
        presenters[x] = []


    if year == 2013:
        for key, value in awards_set_main2013.iteritems():
            for key2, value2 in presenters_2013_main.iteritems():
                if key2 == key:
                    presenters[value].extend(value2)

    if year == 2015:
        for key, value in awards_set_main.iteritems():
            for key2, value2 in presenters_2015_main.iteritems():
                if key2 == key:
                    presenters[value].extend(value2)


    for key, value in presenters.iteritems():
        presenters[key] = [ite for ite, it in Counter(value).most_common(2)]

    # Your code here
    return presenters

def get_most_discussed(year):
    #fun goal to get most popular person
    #these are usually from the list of nominees so we will use it
    #takes in year and returns list of 3 most discussed people

    most_popular = []
    ret_list = []

    if year == 2013:
        for key, value in nominees_2013_main.iteritems():
            most_popular.append(value)

    if year == 2015:
        for key, value in nominees_2015_main.iteritems():
            most_popular.append(value)

    for word in most_popular:
        try:
            ret_list.index(word)[1] += 1
        except:
            ret_list.append([word,0])

    return ret_list


def download(url):
    '''http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
    '''
    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()
    return f

def extract(file_name):
    '''http://stackoverflow.com/questions/20635245/using-gzip-module-with-python
    '''
    inFile = gzip.open(file_name, 'rb')
    outFile = open(file_name[:-3], 'wb')
    outFile.write( inFile.read() )
    inFile.close()
    outFile.close()
    return

def delete(file_name):
    os.remove(file_name)
    return

def save(dObj, sFilename):
  """Given an object and a file name, write the object to the file using pickle."""
  f = open(sFilename, "w")
  p = pickle.Pickler(f)
  p.dump(dObj)
  f.close()

def load(sFilename):
  """Given a file name, load and return the object stored in the file."""
  f = open(sFilename, "r")
  u = pickle.Unpickler(f)
  dObj = u.load()
  f.close()
  return dObj

def Make_IMDB_People_List(f):
    c  = open(f,'rb').read()
    List = re.findall(r'\n{2,}(.*)', c)
    exp = re.compile('([A-z \-\.]*)(?:,(( [A-z\-\.]*){0,3})(?:\(I*\))?)(.*)\s(\(.*\))\s*(\[.*\])?',re.M)
    imdblists =[]
    for index,item in enumerate(List):
        match = re.match(exp, item)
        if(match!= None):
            imdblists.append(match.group(2).strip() +  ' ' +match.group(1).strip())
    return imdblists

def Make_IMDB_Movie_List(f):
    c  = open(f,'rb').read()
    # exp = re.compile('(.*)\s\([0-9?]*\)',re.M)
    # TRY TO LIMIT IT TO MOVIES IN 2000'S
    exp = re.compile('(.*)\s\(20[0-9][0-9?]\)',re.M)
    List = re.findall(exp, c)
    List =set(List)
    return List

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    #get IMDB Actor,Actress,Nicknames, and Movie List
    global actors_set,actresses_set,movies_set,max_tokens,tweets2015,tweets2013,awards_set, winners_2015

    if not((os.path.isfile("actors.set")) and os.path.isfile("actresses.set") and os.path.isfile("movies.set")):
        urls = ['ftp://ftp.fu-berlin.de/pub/misc/movies/database/actors.list.gz','ftp://ftp.fu-berlin.de/pub/misc/movies/database/actresses.list.gz','ftp://ftp.fu-berlin.de/pub/misc/movies/database/aka-names.list.gz','ftp://ftp.fu-berlin.de/pub/misc/movies/database/movies.list.gz']
        for url in urls:
            file_name = url.split('/')[-1]
            download(url)
            extract(file_name)
            delete(file_name)
        lists  = ['actresses.list','actors.list','movies.list']
        actresses = set(Make_IMDB_People_List(lists[0]))
        actors = set(Make_IMDB_People_List(lists[1]))
        movies = Make_IMDB_Movie_List(lists[2])
        delete(lists[0])
        delete(lists[1])
        delete(lists[2])
        #nick nameslist
        save(actors, 'actors.set')
        save(actresses, 'actresses.set')
        save(movies, 'movies.set')



    if not((os.path.isfile("converted_awards.set")) and os.path.isfile("2015tweets.set") and os.path.isfile("2015winners.set") and os.path.isfile("converted_awards2013.set") and os.path.isfile("2013tweets.set") and os.path.isfile("2013winners.set") and os.path.isfile("2013nominees.set") and os.path.isfile("2013presenters.set") and os.path.isfile("presenters.set")):
        tweets = get_tweets_for_year(2015)
        save(tweets, "2015tweets.set")

        movies_set = load('movies.set')
        awards_set = load('converted_awards.set')
        actors_set = load('actors.set')
        actresses_set = load('actresses.set') #needed for get_winners function, only done first time
        winners = get_winners_dictionary(tweets)
        save(winners, "2015winners.set")

        awards = award_names(tweets) #remember to uncomment - roshun self note
        matching_awards_dict = convert_awards_to_given_names(awards)
        save(matching_awards_dict, "converted_awards.set")

        tweets2013 = get_tweets_for_year(2013)
        save(tweets2013, "2013tweets.set")

        awards2013 = award_names(tweets2013)
        converted13 = convert_awards_to_given_names(awards2013)
        save(converted13, "converted_awards2013.set")

        winners13 = get_winners_dictionary(tweets2013)
        save(winners13, "2013winners.set")

        nominees13 = get_nominees_dictionary(tweets2013)
        save(nominees13, "2013nominees.set")

        presenters13 = get_presenters_dictionary(tweets2013)
        save(presenters13, "2013presenters.set")

        presenters15 = get_presenters_dictionary(tweets)
        save(presenters15, "presenters.set")


    ##possibly get dictionary objects for both years json objects
    if not((os.path.isfile('nominees.set'))):
        actors_set = load('actors.set')
        movies_set = load('movies.set')
        actresses_set = load('actresses.set')

        noms = get_nominees_dictionary(load("2015tweets.set"))
        save(noms, "nominees.set")

    print "Pre-ceremony processing complete."
    return

def onLoad():
    '''if we get a gui stuff to do before it shows'''
    global actors_set,actresses_set,movies_set,max_tokens,tweets2015,tweets2013,awards_set, winners_2015
    # load sets 
    max_tokens = 4; #Max number of tokens in a name i.e. Robert De Niro has 3 
    actors_set = load('actors.set')
    actresses_set = load('actresses.set')
    movies_set = load('movies.set')

    global awards_set_main, awards_set_main2013, winners_2015_main, presenters_2015_main, tweets2015_main, nominees_2015_main, nominees_2013_main, winners_2013_main, presenters_2013_main
    awards_set_main = load('converted_awards.set')
    awards_set_main2013 = load('converted_awards2013.set')

    nominees_2015_main = load('nominees.set')
    nominees_2013_main = load('2013nominees.set')

    presenters_2015_main = load('presenters.set')
    presenters_2013_main = load('2013presenters.set')

    winners_2015_main  = load('2015winners.set')
    winners_2013_main = load('2013winners.set')

    #######Optionally create dictionaries on load
    #tweets2015_main = load('2015tweets.set')
    #presenters_2015 = get_presenters_dictionary(tweets2015_main)
    #tweets2013 = load('2013tweets.set')

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    print 'Loading Lists'
    onLoad()
    print 'Lists Loaded'
    #x = get_hosts(2015)

    #matching_main()

    inputflag = 1

    while(inputflag == 1):

        print "Type 'gethosts' to display hosts"
        print "Type 'awards' to display award names"
        print "Type 'nominees' to display nominees mapped to awards"
        print "Type 'winners' to display winners mapped to awards"
        print "Type 'presenters' to display presenters mapped to awards"
        print "Type 'popular' to display frequency of people / movies discussed"

        var = raw_input("Please enter something from the above: ")

        if var == 'gethosts':
            year = raw_input("Please enter either 2013 or 2015: ")
            print get_hosts(int(year))

        if var == 'awards':
            year = raw_input("Please enter either 2013 or 2015: ")
            print get_awards(int(year))

        if var == 'nominees':
            year = raw_input("Please enter either 2013 or 2015: ")
            print get_nominees(int(year))

        if var == 'winners':
            year = raw_input("Please enter either 2013 or 2015: ")
            print get_winner(int(year))

        if var == 'presenters':
            year = raw_input("Please enter either 2013 or 2015: ")
            print get_presenters(int(year))

        if var == 'popular':
            year = raw_input("Please enter either 2013 or 2015: ")
            print get_most_discussed(int(year))

        cont = raw_input("Do you want to continue y/n(Enter y or n lowercase): ")

        if cont == 'y':
            continue
        if cont == 'n':
            print "Terminated"
            inputflag -= 1
            break


if __name__ == '__main__':
    pre_ceremony()
    main()

