#!/usr/bin/env python
# -*- coding:utf-8 -*-
#source du code : https://realpython.com/twitter-bot-python-tweepy/ par Miguel Garcia (https://miguelgarcia.dev/)
import os
import sys
import tweepy #pip install tweepy
import logging
import time
from secrets import *

##########################
#Test de l'accès à Twitter et création de l'API
def create_api():
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)  
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
        print("Authentication OK")
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api
###########################
#test tweet
#api.update_status("Test tweet from Tweepy Python")
###########################

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def check_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    #cette liste contient des noms d'utilisateur qui avait mentionné mon compte il y a longtemps, elle n'a pas de rapport avec le projet
    twitter_id_poubelle = ['JunadTME', 'AgenceWyrdink'] 
    for tweet in tweepy.Cursor(api.mentions_timeline,since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue
        #si l'utilisateur n'est pas dans la liste poubelle 
        if tweet.user.screen_name not in twitter_id_poubelle:
            logger.info(f"Answering to {tweet.user.name}")
            #on récupère le contenu du tweet dans la variable contenu_tweet
            contenu_tweet = tweet.text.lower()
            print(contenu_tweet)
            #la NER doit se faire à ce niveau là, une fois après avoir récupérer le contenu du tweet
            api.update_status(
                status="@{} Bonjour {} :) je suis un test de réponse".format(tweet.user.screen_name, tweet.user.name), in_reply_to_status_id=tweet.id,
            )

    return new_since_id

def main():
    api = create_api()
    since_id = 1
    while True:
        since_id = check_mentions(api, since_id)
        logger.info("Waiting...")
        time.sleep(60)

if __name__ == "__main__":
    main()


