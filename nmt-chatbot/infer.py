import inference as inf
import sqlite3
import json
import re

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import secrets



def get_text(data):       
    # Try for extended text of original tweet, if RT'd (streamer)
    try: text = data['retweeted_status']['extended_tweet']['full_text']
    except: 
        # Try for extended text of an original tweet, if RT'd (REST API)
        try: text = data['retweeted_status']['full_text']
        except:
            # Try for extended text of an original tweet (streamer)
            try: text = data['extended_tweet']['full_text']
            except:
                # Try for extended text of an original tweet (REST API)
                try: text = data['full_text']
                except:
                    # Try for basic text of original tweet if RT'd 
                    try: text = data['retweeted_status']['text']
                    except:
                        # Try for basic text of an original tweet
                        try: text = data['text']
                        except: 
                            # Nothing left to check for
                            text = ''
    return text.replace('\n', ' ')


t_dict = {'@AmazonHelp':'AtAmazonHelp', '@amazon':'AtAmazonHelp', '@PrimeVideoIn':'AtAmazonHelp', '@AmazonUK':'AtAmazonHelp', '@AmazonESP':'AtAmazonHelp', '@JeffBezos':'AtAmazonHelp', '@AmazonKindle':'AtAmazonHelp' }


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def process_t(t):
    t = t.replace('AtAmazonHelp', '@AmazonHelp')
    return t

def process_r(r, CustomerName):
    r = r.replace('AtCustomerName', '@'+CustomerName)
    r = r.replace('AmazonHelpURL', 'http://help.amazon.com')
    return r




class AmazonListener(StreamListener):

    def on_data(self, data):

        try:
            
            j = json.loads(data)
            q = process_t(get_text(j))            
            i = inf.inference(q)
            customer_name = j['user']['screen_name']
            print(q)
            print('\t{}'.format(process_r(i['answers'][i['best_index']], customer_name)))
            print('\n\n\n')
            return True
        except Exception as E:
            print(E)
            pass    

    def on_error(self, status):
        print(status)


auth = OAuthHandler(secrets.consumer_key, secrets.consumer_secret)
auth.set_access_token(secrets.access_token_key, secrets.access_token_secret)
api = tweepy.API(auth)

listener = AmazonListener()

stream = Stream(auth, listener)
stream.filter(track=['@AmazonHelp'])