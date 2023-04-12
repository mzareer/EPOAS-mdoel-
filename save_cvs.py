import tweepy
import pandas as pd
from pandas import ExcelWriter
import os
import tweepy
import time
import sys
import numpy as np
import os
import xlsxwriter
from ast import literal_eval



#****************************************************************************************************************************************
#***********************************************************************************************************************************
#*****************************************************************************************************************************
# class for friends and followers collection

class friends_and_followers:

    def __init__(self):
        self.get_list_ids = self.get_list_ids()
        self.get_list_screen_names = self.get_list_screen_names()



    # this method will give back a list of ids - either friends ids or followers ids
    class get_list_ids:#-------------------------------------------------------------------------------------------  inner class


        def __init__(self):
            twitter_keys = {
                  'consumerKey':          'drr3nRWjq8HiK8jEtbyDAhtQW',
                  'consumerSecret':       'zaZMOqrsyhlQrZzPG26Kxjftd8bsenCXShM2kl6YCLHKMKRWzg',
                  'accessToken':          '1412478170679349248-xxnbAMqJ5Ykwk3QGaAUT1Pln0xEylR',
                  'accessTokenSecret':    'PEQYPsviBlHjJfDiGOYzQU67I9onsUbmv9604QsdTMt3h' ,
              }

            auth = tweepy.OAuthHandler(twitter_keys['consumerKey'], twitter_keys['consumerSecret'])
            auth.set_access_token(twitter_keys['accessToken'], twitter_keys['accessTokenSecret'])
            self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=5, retry_delay=15)
            print("Twitter API created and authenticated - system ready!")


        def updt(self, total, progress):
            """
            Displays or updates a console progress bar.
            Original source: https://stackoverflow.com/a/15860757/1391441
            """
            barLength, status = 20, ""
            progress = float(progress) / float(total)
            if progress >= 1.:
                progress, status = 1, "\r\n"
            block = int(round(barLength * progress))
            text = "\r[{}] {:.0f}% {}".format(
                "#" * block + "-" * (barLength - block), round(progress * 100, 0),
                status)
            sys.stdout.write(text)
            sys.stdout.flush()

        def limit_handled(self, cursor): # to handle if any errors come with the cursor
            while True:
              try:
                yield cursor.next()
              except tweepy.RateLimitError:
                time.sleep(15 * 60)
              except tweepy.TweepError as e:
                print("---------------------")
                print("whats going on?")
                print(e ) # prints 34
                time.sleep(15 * 60)
              except StopIteration as s:
                print("Iteration stopped: ", s)
                break




        # This method gives a function that takes an agent id or a user name and returns a list of followers id  ---------------------------------------------------------------------------------------------
        def get_followers_list(self, agent_id):

            print(" ")
            print("-----------------------------------------------------------------")
            print("Agent ( ", agent_id , " ) - begin mapping.")
            start = time.time()
            print("Begin followers collection for agent : ", agent_id)

            user = self.api.get_user(agent_id)       # fetching the user
            followers_count = user.followers_count   # fetching the followers_count
            print("The number of followers of the user are : " + str(followers_count))

            # This starts getting the list of follower ids
            list_of_ids = []
            for page in self.limit_handled(tweepy.Cursor(self.api.followers_ids, agent_id).pages()):
              list_of_ids.extend(page)
              collected_agents = len(list_of_ids) # number of agent follower ids collected at this iteration
              # progress report
              self.updt(followers_count, collected_agents) # update function    - - def updt(total, progress) ---> progress bar

            print("Number of collected followers ids : ", len(list_of_ids))
            end = time.time()
            print("The time it took to collect the data is : ", end - start)

            print("-----------------------------------------------------------------")
            print(" ")
            return list_of_ids




        # This method gives a function that takes an agent id and returns a list of friends id  ---------------------------------------------------------------------------------------------
        def get_friends_list(self, agent_id):

            print(" ")
            print("-----------------------------------------------------------------")
            print("Agent ( ", agent_id , " ) - begin mapping.")
            start = time.time()
            print(" Begin friends collection for agent : ", agent_id)


            user = self.api.get_user(agent_id) # fetching the user
            friends_count = user.friends_count # fetching the followers_count
            print("The number of friends of the user are : " + str(friends_count))


            list_of_ids = []
            for page in self.limit_handled(tweepy.Cursor(self.api.friends_ids, agent_id).pages()):
              list_of_ids.extend(page)
              collected_agents = len(list_of_ids) # number of agent follower ids collected at this iteration
              # progress report
              self.updt(friends_count, collected_agents) # update function    - - def updt(total, progress)   ---> progress bar

            print("Number of collected friends ids : ", len(list_of_ids)) # prints the number of collected id of friends
            end = time.time()
            print("The time it took to collect the data is : ", end - start)

            print("-----------------------------------------------------------------")
            print(" ")
            return list_of_ids


    """ <<<<<<<<<< Second inner class >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"""
    # this method will give back a list of ids - either friends ids or followers ids
    class get_list_screen_names:#-------------------------------------------------------------------------------------------  inner class

        def __init__(self):
            twitter_keys = {
                  'consumerKey':          'drr3nRWjq8HiK8jEtbyDAhtQW',
                  'consumerSecret':       'zaZMOqrsyhlQrZzPG26Kxjftd8bsenCXShM2kl6YCLHKMKRWzg',
                  'accessToken':          '1412478170679349248-xxnbAMqJ5Ykwk3QGaAUT1Pln0xEylR',
                  'accessTokenSecret':    'PEQYPsviBlHjJfDiGOYzQU67I9onsUbmv9604QsdTMt3h' ,
              }

            auth = tweepy.OAuthHandler(twitter_keys['consumerKey'], twitter_keys['consumerSecret'])
            auth.set_access_token(twitter_keys['accessToken'], twitter_keys['accessTokenSecret'])
            self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=5, retry_delay=15)
            print("Twitter API created and authenticated - system ready!")

        def updt(self, total, progress):
            """
            Displays or updates a console progress bar.
            Original source: https://stackoverflow.com/a/15860757/1391441
            """
            barLength, status = 20, ""
            progress = float(progress) / float(total)
            if progress >= 1.:
                progress, status = 1, "\r\n"
            block = int(round(barLength * progress))
            text = "\r[{}] {:.0f}% {}".format(
                "#" * block + "-" * (barLength - block), round(progress * 100, 0),
                status)
            sys.stdout.write(text)
            sys.stdout.flush()



        # This method gives a function that takes an agent id and returns a list of friends screen names  ---------------------------------------------------------------------------------------------

        def get_followers_list_screen_names(self, screen_name):


            print(" ")
            print("-----------------------------------------------------------------")
            start = time.time()
            print("Agent ( ", screen_name, " ) --->  begin mapping.")
            print("Begin followers collection for agent : ", screen_name )

            # This starts getting the list of follower ids
            list_of_screen_names = []
            list_of_pages = []

            user = self.api.get_user(screen_name)       # fetching the user
            followers_count = user.followers_count   # fetching the followers_count
            print("The number of followers of the user are : " + str(followers_count))

            print("Collecting pages")
            for page in self.limit_handled(tweepy.Cursor(self.api.followers, screen_name, count=200).pages()):
              list_of_pages.extend(page)
              collected_agents = len(list_of_pages) # number of agent follower ids collected at this iteration
              updt(followers_count, collected_agents) # update function    - - def updt(total, progress) ---> progress bar


            print("Collecting names")
            for name in list_of_pages:
                list_of_screen_names.append(name.screen_name)

            print("Number of collected  -- followers -- ids : ", len(list_of_screen_names))
            end = time.time()
            print("The time it took to collect the data is : ", end - start)

            print("-----------------------------------------------------------------")
            print(" ")
            return list_of_screen_names



        def get_friends_list_screen_names(self, screen_name):

            print(" ")
            print("-----------------------------------------------------------------")
            start = time.time()
            print("Agent ( ", screen_name, " ) --->  begin mapping.")
            print("Begin friends collection for agent : ", screen_name )

            # This starts getting the list of follower ids
            list_of_screen_names = []
            list_of_pages = []

            user = self.api.get_user(screen_name)       # fetching the user
            followers_count = user.friends_count   # fetching the followers_count
            print("The number of friends of the user are : " + str(followers_count))

            print("Collecting pages")
            for page in self.limit_handled(tweepy.Cursor(self.api.friends, screen_name, count=200).pages()):
              list_of_pages.extend(page)
              collected_agents = len(list_of_pages) # number of agent follower ids collected at this iteration

              updt(followers_count, collected_agents) # update function    - - def updt(total, progress) ---> progress bar


            print("Collecting names")
            for name in list_of_pages:
                list_of_screen_names.append(name.screen_name)

            print("Number of collected  -- friends -- ids : ", len(list_of_screen_names))
            end = time.time()
            print("The time it took to collect the data is : ", end - start)

            print("-----------------------------------------------------------------")
            print(" ")
            return list_of_screen_names



#____



class add_data:

    def __init__(self, name_of_file):
        self.file_name = name_of_file
        print(self.file_name)

    def fill(self):
        #df = pd.read_excel(os.path.join(self.file_name), engine='openpyxl') this is for reading excel files
        df = pd.read_csv(self.file_name) # this is for reading cvs files

        LOG_EVERY_N = 10
        index = df.index
        num_rows = len(index)
        print("Number of agents :", num_rows)

        start = 1380

        for i in range(start, num_rows):
            print("________________________________________________________________________________________________________________")
            print("________________________________________________________________________________________________________________")

            print("Now Agent number (index) ", i, " with --Screen name : ", df['user screen_name'][i] , " ,and --ID:", df['user_id'][i])

            match_found = False
            if pd.isnull(df['followers_ids'][i]) is True: #if the followers are empty
                for j in range(0,i):
                    if df['user name'][i] == df['user name'][j]:
                        print("This is a repeated user. --- collecting previous information.")
                        df.at[i, 'followers_ids'] = df['followers_ids'][j]
                        df.at[i, 'friends_ids'] = df['friends_ids'][j]
                        match_found = True
                        #with ExcelWriter(self.file_name) as writer:
                        #    df.to_excel(writer)
                        break

                if match_found is False:
                        print("Begin the capturing phase for agent : ", df['user_id'][i])
                        #print(list)
                        ff = friends_and_followers.get_list_ids()
                        list_followers = ff.get_followers_list(df['user_id'][i])
                        list_frinds = ff.get_friends_list(df['user_id'][i])


                        df['followers_ids'] = df['followers_ids'].astype('object')
                        df['friends_ids'] = df['friends_ids'].astype('object')

                        df.at[i, 'followers_ids'] = list_followers
                        df.at[i, 'friends_ids'] = list_frinds





            if (i % LOG_EVERY_N) == 0 or i == num_rows-1:
                print("data frame is saved in: ", self.file_name)
                df.to_csv(self.file_name, index=False)




"""
# this to open and parse a cvs file
df = pd.read_csv('file.csv')
print(df)
index = df.index
num_rows = len(index)

for i in range(num_rows):
  print("user name: ( ", df['user screen_name'][i] , " ) user id : ( ", df['user_id'][i], " ) ")
  lst1 = df['followers_ids'][i]
  list1 = literal_eval(lst1)
  lst2 = df['friends_ids'][i]
  list2 = literal_eval(lst2)
  print("Followers : ", len(list1))
  print("Friends :", len(list2))
  print("last Followers : ", list1[-1])
  print(type(df['followers_ids'][i]))
  print("followers : ", type(list1))
  print("friends : " , type(list2))
  print("_________________________________________________________________________________________")
"""

a = add_data('feb_cvs.csv')
a.fill()
"""
# copy an excel file to a cvs file
df = pd.read_excel(os.path.join('april_filtered.xlsx'), engine='openpyxl')
df.to_csv('april_cvs.csv', index=False)
df1 = pd.read_csv('april_cvs.csv')
print(df1)
"""
