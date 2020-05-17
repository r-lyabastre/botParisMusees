#!/usr/bin/env python
# -*- coding:utf-8 -*-
#source du code du bot: https://realpython.com/twitter-bot-python-tweepy/ par Miguel Garcia (https://miguelgarcia.dev/)
import os
import re
import logging
import time
import tweepy #pip install tweepy
import requests
import json
from secrets import *

###############################################
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

###############################################
#Fonctions de traitement pour le bot

def check_if_id_in_file(file_name, id_to_search):
    """ Vérifie que l'ID du tweet n'est pas dans liste_id.txt """
    """ Plus précisément, la fonction fait en sorte que le bot n'essaie pas de répondre à des tweets auquels il a déjà répondu"""
    with open(file_name, 'a+', encoding='utf-8') as fichier:
        fichier.seek(0) #pour être sûr de lire le fichier depuis le début
        fichier_read = fichier.read()
        if str(id_to_search) not in fichier_read:
            return True
        else:
            return False

def write_id_in_file(file_name, id_to_write):
    """ Ecrit l'ID du tweet dans liste_id.txt"""
    with open(file_name, 'a+', encoding='utf-8') as fichier:
        fichier.write('{}\n'.format(str(id_to_write)))

def get_image_from_url(url_image):
    """ Récupère une image depuis son url et l'enregistre dans un fichier JPG"""
    with open("temp.jpg", "wb") as fichier_image:
        url = url_image
        r = requests.get(url = url)
        fichier_image.write(r.content)

def tweet_geolocation_test(tweet):
    """ Test si le tweet a des informations de geolocalisation ou si l'utilisateur a un lieu enregistré dans son profil"""
    tweet_json = tweet._json
    if tweet_json['place'] != None:
        #récupération du nom du lieu géolocalisé
        tweet_coord_name = tweet_json['place']['name']
        #si l'on souhaite, récupération de la latitude et longitude
        #tweet_coord_longlat = tweet_json['place']['bounding_box']['coordinates']
        #le format obtenu est une liste de liste de liste, on ne souhaite récupérer qu'une liste avec la latitude et la longitude
        #tweet_coord_longlat = tweet_coord_longlat[0]
        #tweet_coord_longlat = tweet_coord_longlat[0]
        return str(tweet_coord_name)

    #récupération du lieu enregistré par l'utilisateur dans son profil  
    elif tweet.user.location != "":
        location_user = tweet.user.location
        print(location_user)
        return str(location_user)
    else:
        return False

###############################################
#Ecriture du bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def check_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    #liste d'utilisateurs auquels le bot ne doit pas répondre
    twitter_id_poubelle = ['JunadTME', 'AgenceWyrdink']
    #pour chaque tweet mentionnant le bot
    for tweet in tweepy.Cursor(api.mentions_timeline,since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue
        tweet_id = str(tweet.id)
        #si l'utilisateur n'est pas dans la liste poubelle
        if tweet.user.screen_name not in twitter_id_poubelle:
            if check_if_id_in_file('liste_id.txt', tweet_id) == True:
                logger.info(f"Answering to {tweet.user.name}")
                #on récupère le contenu du tweet dans la variable contenu_tweet
                contenu_tweet = tweet.text.lower()
                #récupération des éventuelles infos de géolocalisation
                tweet_geolocation_test(tweet)
                #Traitement du contenu du tweet



                

                #récupération en local de l'image que l'on souhaite poster : donner en argument l'url de l'image désirée
                get_image_from_url('https://www.parismuseescollections.paris.fr/sites/default/files/atoms/images/CAR/lpdp_27126-5.jpg')
                #écriture de l'ID du tweet dans liste_id.txt
                write_id_in_file('liste_id.txt', tweet_id) 
                #réponse au tweet
                message = "@{} Bonjour {}".format(tweet.user.screen_name, tweet.user.name)
                api.update_with_media('temp.jpg', status=message)
                #suppression de l'image après le post du tweet (gain de place)
                os.remove('temp.jpg')
                
                
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


