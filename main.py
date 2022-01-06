#2 contributors
#@Ussa-Lle
#@r-lyabastre

# -*- coding:utf-8 -*-
#source du code : https://realpython.com/twitter-bot-python-tweepy/ par Miguel Garcia (https://miguelgarcia.dev/)
import os
import logging
import re
import random

import time
import tweepy 
import requests
import PIL
from PIL import Image

from secrets import *
import main_program as local 

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

def check_if_id_in_file(file_name, id_to_search):
    """ Vérifie que l'ID du tweet n'est pas dans liste_id.txt """
    """ Plus précisément, la fonction fait en sorte que le bot n'essaie pas de répondre à des tweets auquels il a déjà répondu"""
    with open(file_name, 'r', encoding='utf-8') as fichier:
        fichier.seek(0)
        fichier_read = fichier.readlines()
        lis_file = [ re.sub('\D','',f) for f in fichier_read]
        # print(set(lis_file))
        # input('>>')
        if str(id_to_search) in set(lis_file):
            return False
        # print(str(id_to_search))
        # input('>>>')
        return True

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

def disap_emoji():
    """
    IN : _ 
    OUT: "str"
    """  
    return random.choice([ "\U0001f626","\U0001f614","\U0001f613"])

def check_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    #liste d'utilisateurs auquels le bot ne doit pas répondre
    twitter_id_poubelle = ['JunadTME', 'AgenceWyrdink'] #, 'Venitux'
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
                if local.main(tweet.text) is not None:
                    try:
                        ans = local.main(tweet.text)
                        #récupération en local de l'image que l'on souhaite poster : donner en argument l'url de l'image désirée
                        get_image_from_url(ans[0][0])
                        #écriture de l'ID du tweet dans liste_id.txt 
                        #réponse au tweet
                        auteur = ans[0][2].replace(',' , '') 
                        titre = re.sub('[\\\/]+',' ',ans[0][1].strip())
                        titre = re.sub(' +',' ',titre)
                        end_date = ans[0][6]
                        lieu_conservation = ans[0][3]
                        url ="https://www.parismuseescollections.paris.fr/fr/node/"+ans[1]
                        message = "@{} \U0001f449 #{} \U0001f58c\uFE0F {}, \U0001f5bc\uFE0F {}, \U0001f4c6 {}, \U0001f3db\uFE0F {}\n \U0001f517 {}".format(tweet.user.screen_name, ans[0][7].replace(" ", ""),auteur, titre, end_date, lieu_conservation, local.tiny_url(url))
                        try:
                            api.update_with_media('temp.jpg', status=message,in_reply_to_status_id = tweet_id)
                            write_id_in_file('liste_id.txt', tweet_id)
                        except:
                            try:
                                mywidth = 400
                                img = Image.open('temp.jpg')
                                wpercent = (mywidth/float(img.size[0]))
                                hsize = int((float(img.size[1])*float(wpercent)))
                                img = img.resize((mywidth,hsize), PIL.Image.ANTIALIAS)
                                img.save('temp.jpg')
                                api.update_with_media('temp.jpg', status=message,in_reply_to_status_id = tweet_id)
                                write_id_in_file('liste_id.txt', tweet_id)
                            except:
                                message = "@{} \U0001f449 #{} \n \U0001f517 {}".format(tweet.user.screen_name, ans[0][7].replace(" ", ""),local.tiny_url(url))
                                api.update_with_media('temp.jpg', status=message,in_reply_to_status_id = tweet_id)
                                write_id_in_file('liste_id.txt', tweet_id)

                        #suppression de l'image après le post du tweet (gain de place)
                        os.remove('temp.jpg')
                    except:
                        try:
                            message = api.update_status("@{} Navrés ! \U0001f615 Nous n'avons rien trouvé {}".format(tweet.user.screen_name,disap_emoji()))
                            write_id_in_file('liste_id.txt', tweet_id)
                        except:
                            pass                 
                else:
                    if tweet_geolocation_test(tweet) is not False :
                        try:
                            if local.main('',tweet_geolocation_test(tweet)) is not None:
                                ans = local.main('',tweet_geolocation_test(tweet))
                                get_image_from_url(ans[0][0])
                                auteur = ans[0][2].replace(',' , '').strip()
                                titre = re.sub('[\\\/]+',' ',ans[0][1].strip())
                                titre = re.sub(' +',' ',titre)
                                end_date = ans[0][6].strip()
                                lieu_conservation = ans[0][3].strip()
                                url ="https://www.parismuseescollections.paris.fr/fr/node/"+ans[1]
                                message = "@{} \U0001f4cd #{} \U0001f58c\uFE0F {}, \U0001f5bc\uFE0F {}, \U0001f4c6 {}, \U0001f3db\uFE0F {}\n \U0001f517 {}.".format(tweet.user.screen_name, ans[0][7].replace(" ", ""),auteur, titre, end_date, lieu_conservation,local.tiny_url(url))
                                try:
                                    api.update_with_media('temp.jpg', status=message,in_reply_to_status_id = tweet_id)
                                    write_id_in_file('liste_id.txt', tweet_id)
                                except:
                                    try: 
                                        mywidth = 400
                                        img = Image.open('temp.jpg')
                                        wpercent = (mywidth/float(img.size[0]))
                                        hsize = int((float(img.size[1])*float(wpercent)))
                                        img = img.resize((mywidth,hsize), PIL.Image.ANTIALIAS)
                                        img.save('temp.jpg')
                                        api.update_with_media('temp.jpg', status=message,in_reply_to_status_id = tweet_id)
                                        write_id_in_file('liste_id.txt', tweet_id)
                                    except:
                                        message = "@{} \U0001f4cd #{} \n \U0001f517 {}.".format(tweet.user.screen_name,ans[0][7].replace(" ", ""),local.tiny_url(url))
                                        api.update_with_media('temp.jpg', status=message,in_reply_to_status_id = tweet_id)
                                        write_id_in_file('liste_id.txt', tweet_id)
                                os.remove('temp.jpg')
                            else:
                                try:
                                    message = api.update_status("@{} Désolé ! \U0001f615 Nous n'avons rien trouvé {}".format(tweet.user.screen_name,disap_emoji()))
                                    write_id_in_file('liste_id.txt', tweet_id)
                                except:
                                    pass                       

                        except:
                            try:
                                message = api.update_status("@{} Oups ! \U0001f615 Nous n'avons rien détecté {}".format(tweet.user.screen_name,disap_emoji()))
                                write_id_in_file('liste_id.txt', tweet_id)
                            except:
                                pass
                    else:
                        try:
                            message = api.update_status("@{} Mince ! \U0001f615  nous n'avons rien trouvé {}".format(tweet.user.screen_name,disap_emoji()))
                            write_id_in_file('liste_id.txt', tweet_id)
                        except:
                            pass
                                    
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


