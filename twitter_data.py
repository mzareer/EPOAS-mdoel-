import tweepy
import time
import numpy as np
import nltk
import re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from pandas import ExcelWriter
import os
import xlsxwriter


class search_twitter:

    twitter_keys = {
        'consumerKey':          'GsCb2SISXeHVR7by32eZ9APHg',
        'consumerSecret':       'eoMI0yOSrbjOfQziOL1eaDO9kVZMfM3svyv8OJpgibRLwGWfl2',
        'accessToken':          '779952380-OTg6BByK0TtOBWjVfL2dx4eG7F0c6TX0RgBl7kpq',
        'accessTokenSecret':    'rmQSOO73zH0xgLfWsydhHfkPhhmLlymJkRvqdBiOu1gPE',
    }

    def __init__(self, keys_dict=twitter_keys):
      # Authentication
      auth = tweepy.OAuthHandler(keys_dict['consumerKey'], keys_dict['consumerSecret'])
      auth.set_access_token(keys_dict['accessToken'], keys_dict['accessTokenSecret'])
      self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=5, retry_delay=15)
      print("Twitter API created and authenticated - system ready!")

    def search_tweets(self, searchQuery="marvel", startDate='2020-12-01 00:00:00', endDate='2020-11-01 00:00:00',
     every = 1000, num_tweets=10, list_connections=False, return_data_frame = True, save_excel=True, geo="48.820679,-100.445930,3000km", file_name = 'data1.xlsx', threshold=100):


            def limit_handled(cursor):
                while True:
                  try:
                    yield cursor.next()
                  except tweepy.RateLimitError:
                    time.sleep(15 * 60)
                  except tweepy.TweepError:
                    print("---------------------")
                    print("whats going on?")
                    print(tweepy.TweepError)
                    time.sleep(15 * 60)
                  except StopIteration as s:
                    print("Iteration stopped: ", s)
                    break



            def remove_pattern(input_txt, pattern):
            #cleaning the tweets - this function removes all charachters from tweet text and leaves a clean text
                r = re.findall(pattern, input_txt)
                for i in r:
                    input_txt = re.sub(i, '', input_txt)
                return input_txt

            def clean_tweets(tweets):
                #remove twitter Return handles (RT @xxx:)
                tweets = np.vectorize(remove_pattern)(tweets, "RT @[\w]*:")
                #remove twitter handles (@xxx)
                tweets = np.vectorize(remove_pattern)(tweets, "@[\w]*")
                #remove URL links (httpxxx)
                tweets = np.vectorize(remove_pattern)(tweets, "https?://[A-Za-z0-9./]*")
                #remove special characters, numbers, punctuations (except for #)
                tweets = np.core.defchararray.replace(tweets, "[^a-zA-Z]", " ")
                return tweets

            def get_followers_screen_name(accountvar, limit= None):
            # function that takes a screen name of a user and returns
                every = 1000
                followers_screen_names =[]
                for user in limit_handled(tweepy.Cursor(self.api.followers, screen_name=accountvar,count=5000).items(limit)):
                  followers_screen_names.append(user.screen_name)
                  if len(followers_screen_names) % every == 0:
                    print ("followrs count: ", len(followers_screen_names))
                return followers_screen_names

            def get_friends_screen_name(accountvar):
                every = 1000
                friends_screen_names =[]
                for user in limit_handled(tweepy.Cursor(self.api.friends, screen_name=accountvar,count=5000).items(limit)):
                  friends_screen_names.append(user.screen_name)
                  if len(friends_screen_names) % every == 0:
                    print ("friends count: ", len(friends_screen_names))
                return friends_screen_names




            # function data collection starts here -***************************************************************************
            data = []
            mined = {}
            counter = 0
            rate = every

            tweets = limit_handled(tweepy.Cursor(self.api.search, q = searchQuery,
                                        monitor_rate_limit=True,
                                        wait_on_rate_limit=True,
                                        wait_on_rate_limit_notify = True,
                                        retry_count = 15,
                                        retry_delay = 15,
                                        timeout = 15,
                                        https=True,
                                        geocode=geo,
                                        lang="en", fromDate = startDate, toDate = endDate).items(num_tweets))

            for tweet in tweets:

                if tweet.user.followers_count >= threshold:



                  mined = {
                      'tweet_id':               tweet.id,
                      'tweet created_at':       tweet.created_at,
                      'user name':              tweet.user.name,
                      'user screen_name':       tweet.user.screen_name,
                      'user_id':                tweet.author.id,
                      'user verified':          tweet.user.verified,
                      'followers count':        tweet.user.followers_count,
                      'friends count':          tweet.user.friends_count,
                      '(Tweet)Text':            tweet.text,
                      'location':               tweet.user.location
                   }

                  #cleaning text tweets
                  tweet_Text = clean_tweets(tweet.text)
                  # anlaysing the sentiment of the tweets - --------------------------------- sentiment analysis
                  analyzer = SentimentIntensityAnalyzer() # create an object
                  compound = analyzer.polarity_scores(str(tweet_Text))["compound"]
                  pos = analyzer.polarity_scores(str(tweet_Text))["pos"]
                  neu = analyzer.polarity_scores(str(tweet_Text))["neu"]
                  neg = analyzer.polarity_scores(str(tweet_Text))["neg"]
                  mined['compound'] = compound
                  mined['pos'] = pos
                  mined['neu'] = neu
                  mined['neg'] = neg

                  # checking if the tweet is a replay, retweet or a qoute
                  if hasattr(tweet, 'retweeted_status'):
                    mined['Number of Retweets']  =  tweet.retweeted_status.retweet_count  # get the likes if its a retweet
                    mined['Number of Likes'] =  tweet.retweeted_status.favorite_count  # get the likes if its a retweet
                    mined["Retweet of id"] = tweet.retweeted_status.user.id_str
                    mined["Retweet of screen name"] = tweet.retweeted_status.user.screen_name
                    mined["Type"] = "Retweet"

                  elif hasattr(tweet, 'quoted_status'):
                    mined['Number of Retweets']  =  tweet.quoted_status.retweet_count  # get the likes if its a retweet
                    mined['Number of Likes'] = tweet.quoted_status.favorite_count  # get the likes if its a retweet
                    mined["quoted from id"] = tweet.quoted_status.user.id_str
                    mined["quoted from screen name"] = tweet.quoted_status.user.screen_name
                    mined["Type"] = "Quote"

                  elif tweet.in_reply_to_status_id is not None:
                    # Tweet is a reply
                    mined['Number of Retweets']  =  tweet.retweet_count  # get the likes if its a retweet
                    mined['Number of Likes'] = tweet.favorite_count  # get the likes if its a retweet
                    mined['Reply to screen name'] = tweet.in_reply_to_screen_name
                    mined['Reply to id'] = tweet.in_reply_to_user_id_str
                    mined["Type"] = "Reply"
                  else:
                    try:
                      mined['Number of Retweets']  =  tweet.retweet_count  # get the likes if its a retweet
                      mined['Number of Likes'] =  tweet.favorite_count # gets the likes if its an original tweet
                      mined["Type"] = "Original"
                    except:
                      pass


                  if list_connections is True: # if the user wants to add lists of friends and followers then this will activate otherwise it will be empty
                      mined['followers'] = get_followers_screen_name(mined['user screen_name'])
                      mined['friends'] = get_friends_screen_name(mined['user screen_name'])
                  else:
                      mined['followers'] = None
                      mined['friends'] = None


                  if counter % rate == 0:
                    print("collected tweets :", counter)
                    if save_excel is True: # this checks if we want to save the
                        df = pd.DataFrame(data, columns = ['tweet_id', 'tweet created_at', 'user name', 'user screen_name', 'user_id', 'user verified', 'location',
                                                'friends count', 'followers count', 'followers','friends',
                                                'Number of Retweets', 'Number of Likes',
                                                'compound', 'pos', 'neg', 'neu', '(Tweet)Text',
                                                'Type', 'Reply to id','Reply to screen name',
                                                'Retweet of id', 'Retweet of screen name',
                                                'quoted from id', 'quoted from screen name'])

                        # Create a Pandas Excel writer using XlsxWriter as the engine.
                        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
                        # Convert the dataframe to an XlsxWriter Excel object.
                        df.to_excel(writer, sheet_name='data')
                        # Close the Pandas Excel writer and output the Excel file.
                        writer.save()
                        print("collected tweets saved in:", file_name)

                  counter += 1
                  data.append(mined)






            if save_excel is True: # this checks if we want to save the
                df = pd.DataFrame(data, columns = ['tweet_id', 'tweet created_at', 'user name', 'user screen_name', 'user_id', 'user verified', 'location',
                                        'friends count', 'followers count', 'followers','friends',
                                        'Number of Retweets', 'Number of Likes',
                                        'compound', 'pos', 'neg', 'neu', '(Tweet)Text',
                                        'Type', 'Reply to id','Reply to screen name',
                                        'Retweet of id', 'Retweet of screen name',
                                        'quoted from id', 'quoted from screen name'])

                print("data frame is saved in: ", file_name)
                # Create a Pandas Excel writer using XlsxWriter as the engine.
                writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
                # Convert the dataframe to an XlsxWriter Excel object.
                df.to_excel(writer, sheet_name='data')
                # Close the Pandas Excel writer and output the Excel file.
                writer.save()

                #with ExcelWriter(file_name) as writer:
                #    df.to_excel(writer)


            if return_data_frame is True:
                df = pd.DataFrame(data, columns = ['tweet_id', 'tweet created_at','user name', 'user screen_name', 'user_id', 'user verified', 'location',
                                        'friends count', 'followers count', 'followers','friends',
                                        'Number of Retweets', 'Number of Likes',
                                        'compound', 'pos', 'neg', 'neu', '(Tweet)Text',
                                        'Type', 'Reply to id','Reply to screen name',
                                        'Retweet of id', 'Retweet of screen name',
                                        'quoted from id', 'quoted from screen name'])
                return df
            else:
                return data









    def add_followers_to_dataframe(self, file, limit = None): # methode 2 -----------------------------------------------------------------------------------------------
    # This method takes a dataframe
            # supporting methods methods---------------------------------------------
            def limit_handled(cursor):
            # This function prevents the twitter cursor from terminating once the limit is reached
                while True:
                  try:
                    yield cursor.next()
                  except tweepy.RateLimitError:
                    time.sleep(15 * 60)
                  except tweepy.TweepError:
                    print("---------------------")
                    print("whats going on?")
                    print(tweepy.TweepError)
                    print(tweepy.TweepError.response.status)
                    print(tweepy.TweepError.response.text )
                    time.sleep(15 * 60)
                  except StopIteration as s:
                    break
            
            
                  
            def get_followers(sn): #  function to get a list of follower screen names once you input a screen name 
              names =[]
              list_n = []
              
              for user in tweepy.Cursor(self.api.followers, screen_name=sn, count=200).pages():
                  print(len(user))
                  names.extend(user)
                  time.sleep(60)
              for name in names:
                  list_n.append(name.screen_name)  
              return list_n
            
            

            def get_followers_screen_name(accountvar, limit= None):
            # function that takes a screen name of a user and returns
                every = 1000
                followers_screen_names =[]
                for user in limit_handled(tweepy.Cursor(self.api.followers, screen_name=accountvar,count=200).items(limit)):
                  followers_screen_names.append(user.screen_name)
                  if len(followers_screen_names) % every == 0:
                    print ("followrs count: ", len(followers_screen_names))
                return followers_screen_names


            # checking what type of file was inserted
            def check_file(file):
                if file.endswith('.xlsx'):
                    df=pd.read_excel(
                         os.path.join(file),
                         engine='openpyxl',
                    )
                    df = df[df.filter(regex='^(?!Unnamed)').columns]
                    print("Excel file loaded and converted to a DataFrame: ", file)
                    return df
                elif isinstance(file, pd.DataFrame):
                    print("Dataframe loaded correctly")
                    return df
                else:
                    print("Type of file not supported")

            # start of code for this function 
            # the programming starts from here ----------------------------------------------------------------------------- free code for the followrs addition methode
            df = check_file(file) # this function checks if you have an xcel file or a dataframe - if its an excel file it upoads it and

            index = df.index
            number_of_rows = len(index)
            print("loaded DataFrame has the following nnumber of rows: ",number_of_rows)

            df['followers'] = df['followers'].astype('object')

            for i in range(number_of_rows):
              if pd.isnull(df['followers'][i]) is True:
                print("Program now on index: ", i)
                df.at[i,'followers'] = get_followers(df['user screen_name'][i])
              print("Followers of (", df['user screen_name'][i], ") collected :", len(df.at[i,'followers']))
              with ExcelWriter(file) as writer:
                df.to_excel(writer)


            return df





  #--------------------------------------------------------------- we add the list of friends to a dataframe using the following function
  




    def add_friends_to_dataframe(self, file, limit = None): # method 3 add friend lists -------------------------------------------------------------------------------
            # supporting methods methods---------------------------------------------
            def limit_handled(cursor):
            # This function prevents the twitter cursor from terminating once the limit is reached
                while True:
                  try:
                    yield cursor.next()
                  except tweepy.RateLimitError:
                    time.sleep(15 * 60)
                  except tweepy.TweepError:
                    print("---------------------")
                    print("whats going on?")
                    print(tweepy.TweepError)
                    time.sleep(15 * 60)
                  except StopIteration as s:
                    break


            def get_friends(sn): # new functrion added on 10 may -------------
              
                names =[]
                list_n = []
                
                for user in tweepy.Cursor(self.api.friends, screen_name=sn, count=200).pages():
                    print(len(user))
                    names.extend(user)
                    time.sleep(60)

                for name in names:
                    list_n.append(name.screen_name)
                          
                return list_n


            def get_friends_screen_name(accountvar, limit= None):
                every = 1000
                friends_screen_names =[]  # empty list that will house the names of one idividuals friends (list of connections as friends)
                for user in limit_handled(tweepy.Cursor(self.api.friends, screen_name=accountvar,count=200).items()): # this gets the friends list
                  friends_screen_names.append(user.screen_name)
                  if len(friends_screen_names) % every == 0:
                    print ("friends count: ", len(friends_screen_names))
                return friends_screen_names

            # checking what type of file was inserted
            def check_file(file):
                if file.endswith('.xlsx'):
                    df=pd.read_excel(
                         os.path.join(file),
                         engine='openpyxl',
                    )
                    df = df[df.filter(regex='^(?!Unnamed)').columns]
                    print("Excel file loaded and converted to a DataFrame: ", file)
                    return df
                elif isinstance(file, pd.DataFrame):
                    print("Dataframe loaded correctly")
                    return df
                else:
                    print("Type of file not supported")

            # the programming starts from here ----------------------------------------------------------------------------- free code for the followrs addition methode
            df = check_file(file)

            index = df.index
            number_of_rows = len(index)
            print("loaded DataFrame has the following nnumber of rows: ",number_of_rows)

            df['friends'] = df['friends'].astype('object')
            
            for i in range(number_of_rows):
              if pd.isnull(df['friends'][i]) is True: #check if the name in the list does not have a list of friends added
                print("Collecting the friends of user: ", df['user screen_name'][i])
                df.at[i,'friends'] = get_friends_screen_name(df['user screen_name'][i], limit) # this here calles the function "get_friends_screen_name"

              with ExcelWriter(file) as writer:
                df.to_excel(writer)


            return df
