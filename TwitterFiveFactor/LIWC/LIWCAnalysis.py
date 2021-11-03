import snscrape.modules.twitter as sntwitter
import pandas as pd
import re

class LIWCAnalysis:

    #reads excel data into DataFrame Object
    def getExcel(self, filename):
        # 0 means sheet zero
        exFile = pd.read_excel(filename,0)
        return exFile

    #Gets specific users data from excellspreadsheat
    def getUserData(self, xlx, colName):
        user = []
        for i in range(0,64):
            user.append(xlx[colName][i])

        return user

    #Gets specific category data from excel spreadsheat
    def getCategoryData(self, xlx, catNo):
        col = xlx.loc[catNo,:]
        category = []
        plus = 0
        for g in range(1, 241):
            if g not in col:
                pass
            else:
                category.append(col[g])
        return category

    #Prints all of a  Users data
    def printUserData(self, xlx, colName):
        print(colName)
        print("------")
        total = 0
        for i in range(0, 64):
            print(str(xlx['CAT'][i]) + ": " + str(xlx[5][i]))
            total+= xlx[5][i]
        print("Total is: " + str(total))
        avg = total / 64
        print("Average is: " + str(avg))

    #Prints Categorys data
    def printCategoryData(self, xlx, catNo):
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

    #Prints all data from every user
    def printEverything(self, xlx):
        #Print everything
        for i in range(0, 64):
            print(i)
            self.printCategoryData(xlx, i)

    #Finds closes match to specified users LIWC Scores
    def bestMatch(self, xlx, user):
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
            scoresForCategory = LIWCAnalysis.getCategoryData(self, xlx, i)
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

    # Converts a .dic file to a python dictionary
    def dic_to_dict(self, filename):
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

    # A very simple tokeninzer method
    def simpTokenize(self, text):
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

    # matches tokens to their corresponding value in the LIWC dictionry
    def match_regex_to_text(self, tokens, dictionary):
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

    #Removes all special characters
    def removeSpecialCharacters(self, str):
        retStr = re.sub('[^a-zA-Z0-9]+', '', str)
        return retStr

    #Uses SNSScrape to get a users recent tweets depending on their twitter username
    def getTweets(self, username):
        tweets_list = []
        twitterContent = ""
        #Puts tweets into list
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper('from:'+username).get_items()): #declare a username
            if i>10: #number of tweets you want to scrape
                break
            tweets_list.append([tweet.date, tweet.id, tweet.content]) #declare the attributes to be returned

        for i in tweets_list:
            twitterContent += str(i[2])

        return twitterContent

    #A more complicated tokenizer that seperates words, twitter mentions, links and prices
    def tokenize(self, tweets):
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
                word = str.lower(LIWCAnalysis.removeSpecialCharacters(self, i))
                if(len(word)>0):
                    words.append(word)
        retList = []
        retList.append(words)
        retList.append(mentions)
        retList.append(links)
        retList.append(prices)
        return retList

    #An Algorithm to get a users personality score from the supplied database of
    #Personality scores
    def getScore(self, xlx, userNo):
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

    #Initiaizer for the LIWC dictionary
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