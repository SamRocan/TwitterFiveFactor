import time

from django.test import TestCase
import os
from .LIWCAnalysis import getExcel, getTweets, tokenize, bestMatch, getScore, makeTrie, dic_to_dict


# Create your tests here.

# To test individual methods
# python manage.py test LIWC.tests.LIWCTestCase.test_methodName
class LIWCTestCase(TestCase):

    def setUp(self):
        pass

    def test_getExcel(self):
        self.module_dir = os.path.dirname('media/')
        user_scores = os.path.join(self.module_dir, 'user_scores.xlsx')
        all_users = os.path.join(self.module_dir, 'combined_users.xlsx')
        data = getExcel(all_users)
        self.assertEqual(str(type(data)), '<class \'pandas.core.frame.DataFrame\'>')
        score_data = getExcel(user_scores)
        data = getExcel(all_users)
        self.assertEqual(str(type(score_data)), '<class \'pandas.core.frame.DataFrame\'>')

        #Make sure all data has been imported
        self.assertEqual(len(data), 64)
        self.assertEqual(len(score_data), 238)

    def test_getTweets(self):
        twitterContent = getTweets("BillGates")
        #length should be greater than 10 if all 10 tweets are collected as tweets
        # typically contain more than 1 character each
        self.assertGreater(len(twitterContent), 10)
        twitterContent = getTweets("Jack")
        self.assertGreater(len(twitterContent), 10)
        twitterContent = getTweets("Rihanna")
        self.assertGreater(len(twitterContent), 10)

        try:
            twitterContent = getTweets("DonaldTrump")
        except Exception:
            pass
        self.assertRaises(Exception, twitterContent)

    def test_tokenize(self):
        tweets = tokenize("Hello how are you")
        #everything is changed to lower case
        self.assertEqual(tweets, [['hello', 'how', 'are', 'you'], [], [], []])

        tweets = tokenize("@Sam what are you doing #here")
        #everything is changed to lower case
        self.assertEqual(tweets, [['sam', 'what', 'are', 'you', 'doing', 'here'], ['@Sam'], [], []])

        tweets = tokenize("I made £10 today at the market https://www.market.com . check it out")
        self.assertEqual(tweets, [['i', 'made', '10', 'today', 'at', 'the', 'market', 'check', 'it', 'out'], [], ['https://www.market.com'], ['£10']])

        tweets = tokenize("")
        self.assertEqual(tweets,[[], [], [], []])

    """
    BestMatch() and getScore() are difficult to analyze as the values they produce will
    change depending on the users most recent tweets. As such they have not been officially 
    tested here, but are continually monitored through Acceptance and Functioinal Testing
    """
    def test_bestMatch(self):
        pass
    def test_getScore(self):
        pass


