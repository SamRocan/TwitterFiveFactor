import tweepy
import pandas as pd
import re
from django.conf import settings

#Create a Trie Structure
class Node:
    def __init__(self):
        self.key = None
        self.value = None
        self.children = {}

class Trie:
    '''
    A Trie structure to allow for quick and efficient retrieval of matching values

    Attributes
    ----------
    root : Node
        The initial data point at the start of a Trie

    Methods
    -------
    insert(self)
        Inserts a new node into the trie. This node contains a word/regex and its
        corresponding LIWC value

    lookup(self, word)
        Check to see if a word/regex exists in the trie and returns its value if it
        does

    printAllNodes(self, word)
        Iterates through the Trie structure and prints every word/regex and its value

    '''
    def __init__(self):
        self.root = Node()

    def insert(self, word, value):
        '''
        Inserts a new node into the trie. This node contains a word/regex and its
        corresponding LIWC value
        :param word: str
        :param value: int
        :return:
        '''
        currentWord = word
        currentNode = self.root
        while len(currentWord) > 0:
            if currentWord[0] in currentNode.children:
                currentNode = currentNode.children[currentWord[0]]
                currentWord = currentWord[1:]
            else:
                newNode = Node()
                newNode.key = currentWord[0]
                if len(currentWord) == 1:
                    newNode.value = value
                currentNode.children[currentWord[0]] = newNode
                currentNode = newNode
                currentWord = currentWord[1:]

    def lookup(self, word):
        '''
        Check to see if a word/regex exists in the trie and returns its value if it
        does
        :param word: str
        :return nodeValue: int
        '''
        currentWord = word
        currentNode = self.root
        while len(currentWord) > 0:
            if(len(currentNode.children) == 1) and (list(currentNode.children.keys())[0] == '+'):
                currentWord = '+'
            if (currentWord[0] in currentNode.children):
                currentNode = currentNode.children[currentWord[0]]
                currentWord = currentWord[1:]
                #print(currentWord)
            else:
                return "Not in trie"
        if currentNode.value == None:
            return "None"
        return currentNode.value

    def printAllNodes(self):
        '''
        Iterates through the Trie structure and prints every word/regex and its value
        :return:
        '''
        nodes = [self.root]
        while len(nodes) > 0:
            for letter in nodes[0].children:
                nodes.append(nodes[0].children[letter])
            print(nodes.pop(0).key)

def makeTrie(words):
    '''
    Creates the trie structure from given words
    :param words:
    :return: trie: Trie structure (list)
    '''
    trie = Trie()
    for word, value in words.items():
        trie.insert(word, value)
    return trie

def getExcel(filename):
    '''
    Turns excel file into a Pandas Dataframe object
    :param filename:
    :return: exFile: Pandas Dataframe
    '''
    # 0 means sheet zero
    exFile = pd.read_excel(filename,0)
    return exFile

def getUserData(xlx, colName):
    '''
    gets LIWC attributes for a specific user
    :param xlx: Pandas Dataframe
    :param colName: int
    :return: list: list containing the users attributes
    '''
    user = []
    for i in range(0,64):
        user.append(xlx[colName][i])

    return user

def getCategoryData(xlx, catNo):
    '''
    gets all information for a specific liwc category

    :param xlx: Pandas Dataframe
    :param catNo: int
    :return: list: list
    '''
    col = xlx.loc[catNo,:]
    category = []
    plus = 0
    for g in range(1, 241):
        if g not in col:
            pass
        else:
            category.append(col[g])
    return category

def printUserData(xlx, colName):
    '''
    Prints all of a Users data

    :param xlx: Pandas Dataframe
    :param colName: int
    :return:
    '''
    print(colName)
    print("------")
    total = 0
    for i in range(0, 64):
        print(str(xlx['CAT'][i]) + ": " + str(xlx[5][i]))
        total+= xlx[5][i]
    print("Total is: " + str(total))
    avg = total / 64
    print("Average is: " + str(avg))

def printCategoryData(xlx, catNo):
    '''
    Prints all users data from a liwc category

    :param xlx: Pandas Dataframe
    :param catNo: int
    :return:
    '''
    col = xlx.loc[catNo,:]
    head = xlx.columns.values
    print("---")
    total = 0
    plus = 0
    for g in range(1, 241):
        if g not in col:
            print("No " + str(g) + " col")
            plus+=1
        else:
            total += float(col[g])
            print("User " + str(head[g-plus]) + " " + str(col[g]))

    print("Average is: " + str(total/238))

def printEverything(xlx):
    '''
    Prints all data from every  user for every liwc category
    :param xlx: Pandas Dataframe
    :return:
    '''
    #Print everything
    for i in range(0, 64):
        print(i)
        printCategoryData(xlx, i)

def bestMatch(xlx, user):
    '''
    Finds and returns ordered list of users ranked by how close they are to the given
    twitter users score
    :param xlx: Pandas Dataframe
    :param user: list
    :return: users: list
    '''
    mainUserData = user
    users = {}
    # 1) Create dict of all users initialize to 0
    for i in range(1, 241):
        if(i == 17 or i == 66):
            pass
        else:
            users[i] = 0

    # 2) For each category
    for i in range(64):
        # 3) Get all the scores from a category
        scoresForCategory = getCategoryData(xlx, i)
        mainUserData[i]
        scoreDict = {}
        count = 1
        for j in range(238):
            # 4) Calculate the difference between users and each test score
            scoreDict[count] = abs(mainUserData[i]-scoresForCategory[j])
            count+=1
            if(count == 17 or count == 66):
                count+=1
        scoreDict = dict(sorted(scoreDict.items(), key=lambda item: item[1]))
        count = 0
        for x,y in scoreDict.items():
            users[x] += count
            count += 1

    users = dict(sorted(users.items(), key=lambda item: item[1]))
    return users

def dic_to_dict(filename):
    '''
    converts a .dic file into a python dictionary structure
    :param filename: .dic file
    :return: exportDict; dict
    '''
    exportDict = dict()
    with open(filename) as file:
        lines = file.readlines()
        for line in lines:
            num = ""
            numList = []
            count = 0
            word = ""
            while(line[count].islower() or line[count] == '+'):
                word += line[count]
                #print(str(word))
                count+=1
                if(count == len(line)-1):
                    break
            for i in line:
                if i.isdecimal():
                    num+= i
                if num != "" and i.isdecimal() == False:
                    numList.append(int(num))
                    num = ""
                #print(str(line) + " " + str(count))
            exportDict[word] = numList
    return exportDict

def simpTokenize(text):
    '''
    Breaks a string into individual tokens and returns a list of them
    :param text: String
    :return: retList: list
    '''
    retList = []
    word = ""
    for i in text:
        if i == ' ':
            retList.append(word)
            word = ""
        else:
            word+= i
    retList.append(word)
    return retList

def match_regex_to_text(tokens, dictionary):
    '''
    Matches tokens to the liwc dictionary values, and returns a list of values
    :param tokens: list
    :param dictionary: dictionary
    :return: values: list
    '''
    values = []
    for word in tokens:
        wordMatch = []
        valMatch = []

        matchedWords = []
        for reg,value in dictionary.items():
            if(re.match(reg, word)):
                matchedWords.append(reg)
        sorted_matches = sorted(matchedWords, key=len)
        length = len(sorted_matches)
        if(length>=1):
            wordMatch.append(word)
            valMatch.append(dictionary[sorted_matches[length-1]])

        #Uncomment this to see words as they get added
        #for i in range(0, len(wordMatch)):
        #print(str(wordMatch[i]) + ":")
        #print(valMatch[i])
        for i in valMatch:
            for z in i:
                values.append(z)

    print("------------")
    return values

def removeSpecialCharacters(str):
    '''
    Removes special characters from a string
    :param str: String
    :return: retStr: String
    '''
    retStr = re.sub('[^a-zA-Z0-9]+', '', str)
    return retStr

def getTweets(username):
    '''
    Uses tweepy and twitter API to get a users tweets based on their username.
    returns their tweet content as a string
    :param username: String
    :return: twitterContent: String
    '''
    tweets_list = []
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    twitterContent = ''
    for tweet in tweepy.Cursor(api.user_timeline,id=username).items(10):
        twitterContent += ' ' + tweet._json['text']

    return twitterContent

def tokenize(tweets):
    '''
    A more complicated tokenizer that seperates words, twitter mentions,
    links and prices
    :param tweets: String
    :return: retList: List
    '''
    splitwords = tweets.split(" ")
    mentions = []
    links = []
    words = []
    prices = []
    for i in splitwords:
        print(i)
        if(len(i)>0):
            if(i[0]=='@'):
                mentions.append(i)
            if(i[0]=='$' or i[0]=='£'):
                prices.append(i)
        if(len(i)>7):
            if(i[0:6]=='https:'):
                links.append(i)
        else:
            word = str.lower(removeSpecialCharacters(i))
            if(len(word)>0):
                words.append(word)
    retList = []
    retList.append(words)
    retList.append(mentions)
    retList.append(links)
    retList.append(prices)
    return retList


def getScore(xlx, userNo):
    '''
    An Algorithm to get a users personality score from the supplied database of
    Personality scores
    :param xlx: Pandas Dataframe
    :param userNo: int
    :return: retList: List
    '''
    retList = []
    scores = []
    categories = []
    sub = 2
    if(userNo<=16):
        sub = 1
    if(userNo >=67):
        sub = 3
    user = xlx.loc[userNo-sub,:]
    for i in range(1,11):
        if(i<6):
            scores.append(user[i])
        else:
            categories.append(str(user[i]))

    retList.append(scores)
    retList.append(categories)
    return retList

"""
const: Initializer for the LIWC dictionary
"""
LIWC = {
    1:0,
    2:0,
    3:0,
    4:0,
    5:0,
    6:0,
    7:0,
    8:0,
    9:0,
    10:0,
    11:0,
    12:0,
    13:0,
    14:0,
    15:0,
    16:0,
    17:0,
    18:0,
    19:0,
    20:0,
    21:0,
    22:0,
    121:0,
    122:0,
    123:0,
    124:0,
    125:0,
    126:0,
    127:0,
    128:0,
    129:0,
    130:0,
    131:0,
    132:0,
    133:0,
    134:0,
    135:0,
    136:0,
    137:0,
    138:0,
    139:0,
    140:0,
    141:0,
    142:0,
    143:0,
    146:0,
    147:0,
    148:0,
    149:0,
    150:0,
    250:0,
    251:0,
    252:0,
    253:0,
    354:0,
    355:0,
    356:0,
    357:0,
    358:0,
    359:0,
    360:0,
    462:0,
    463:0,
    464:0,
}
