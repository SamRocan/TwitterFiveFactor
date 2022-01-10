from django.shortcuts import render
import os
import time
import tweepy as tw
import pandas as pd

from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings

from .LIWCAnalysis import getExcel, getTweets, tokenize,\
                          dic_to_dict, match_regex_to_text, \
                          bestMatch, getScore, Node, Trie, makeTrie
# Create your views here.
def analysis(request):
    if(request.method == 'GET'):
        prodQuery = request.GET['analysisSearch']

    userName = prodQuery
    if(userName == "None"):
        return render(request, 'Main/noTwitter.html')
    if(userName[0]=='@'):
        userName = userName[1:]
    module_dir = os.path.dirname('media/')
    all_users = os.path.join(module_dir, 'combined_users.xlsx')
    user_scores = os.path.join(module_dir, 'user_scores.xlsx')
    liwc_dic = os.path.join(module_dir, 'LIWC2007_Ammended.dic')
    start_time = time.time()

    data = getExcel(all_users)
    score_data = getExcel(user_scores)
    print(userName)
    print("Getting Tweets for " + str(userName))
    try:
        twitterContent = getTweets(userName)
    except:
        message = "No Twitter account found for that username, please try another account or check your spelling."
        return render(request, 'Main/noTwitter.html', {'message':message})
    print("Getting Tweets took ", time.time() - start_time, " to run")


    print("Tokenizing Tweets")
    tokenizedTweets = tokenize(twitterContent)
    print(tokenizedTweets)
    print("Tokenizing Tweets took ", time.time() - start_time, " to run")

    print("turning to dictionary")
    dictionary = dic_to_dict(liwc_dic)
    print("Dictionary took ", time.time() - start_time, " to run")
    trie = makeTrie(dictionary)

    print("Categorizing tokens")
    trie = makeTrie(dictionary)

    values = []
    for i in tokenizedTweets[0]:
        value = trie.lookup(i)
        for i in value:
            if(isinstance(i, int)):
                values.append(i)
    print("Categorizing tokens took ", time.time() - start_time, " to run")

    print("Getting Best Match")
    try:
        match = bestMatch(data, values)
    except:
        message = "Analysis cannot be preformed on this account. This is usually due to the account " \
                  "primarily being in a language other than English, or the Twitter API rate limit being reached." \
                  "Please try another account, or wait and try again later. "
        return render(request, 'Main/noTwitter.html', {'message':message})
    print("Best Match took ", time.time() - start_time, " to run")

    profile = list(match.keys())[0]
    print("Getting Scores")
    scores = getScore(score_data, profile)
    print("Scores took ", time.time() - start_time, " to run")

    scoresVar = scores[0]
    catVar = scores[1]
    fiveFactors = ["Extraversion", "Neuroticism", "Agreableness", "Concientiousness", "Openness"]

    print("My program took ", time.time() - start_time, " to run")
    extScore = scoresVar[0]
    neuScore = scoresVar[1]
    agrScore = scoresVar[2]
    conScore = scoresVar[3]
    opnScore = scoresVar[4]
    ext = "Extraversion (" + str(catVar[0]) + ")"
    neu = "Neuroticism (" + str(catVar[1]) + ")"
    agr = "Agreableness (" + str(catVar[2]) + ")"
    con = "Concientiousness (" + str(catVar[3]) + ")"
    opn = "Openness (" + str(catVar[4]) + ")"

    #Get Twitter Image
    auth = tw.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
    api = tw.API(auth, wait_on_rate_limit=True)

    user = api.get_user(screen_name=userName)
    url = str(user.profile_image_url)
    userImage = url.replace("_normal", "")
    print(userImage)
    print("My program took ", time.time() - start_time, " to run")

    fiveFactorData = {
        'fiveFactors': fiveFactors,
        'scores': scoresVar,
        'cats': catVar,
        'userName':userName,
    }
    request.session['5Factor'] = fiveFactorData
    #jsonData = dumps(fiveFactorData)

    context = {
        #'scoresVar':scoresVar,
        #'catVar':catVar,
        #'data':jsonData,
        'extScore':extScore,
        'neuScore':neuScore,
        'agrScore':agrScore,
        'conScore':conScore,
        'opnScore':opnScore,
        'ext':ext,
        'neu':neu,
        'agr':agr,
        'con':con,
        'opn':opn,
        'founderName':userName,
        'userImage':userImage
    }

    return render(request, 'LIWC/analysis.html', context)

class ChartData(APIView):

    def get(self, request, format = None):
        data = request.session['5Factor']

        return Response(data)