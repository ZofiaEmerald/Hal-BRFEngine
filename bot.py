## Importation des packages

import discord
import sys
import json
import traceback
import io
import re
import math
import datetime
import time
import asyncio
import random
# import dateutil.parser
import operator
import sys
sys.path.append("/home/laureta/BRF")
from distribmagik import*
# import pywikibot as pwb
# import pywikibot.site

##Définitions essentielles au bot

client = discord.Client()
TOKEN = "Njc3NzcwNjAxOTA5MzIxNzI4.XkZFmw.J_UvWv3_26NkNcLsHuPWaCSTRbw"
prefix = "&"

## Démarrage

@client.event
async def on_ready():
    print(client.user.name, "is connected to the vibrant door.")
    print(client.user.id, "connection name")
    print("Listening")

## Fonctions


def isrole(member, role): # Fonction qui vérifie si un rôle précis est possédé par un membre
    for r in member.roles:
        if r.name.split(" ")[0].lower() == role.lower():
            return True
    return False

def outoftime(begintime, delay):
    nowtime = time()
    if (nowtime - begintime) > delay:
        return True
    return False

def commands(msgKeywords):
    
    cmd = msgKeywords[0].strip()
    
    if cmd == "carteutilisée":
        sophie = msgKeywords[1:]
        if sophie != []:
            for i in range(len(sophie)):
                sophie[i] = sophie[i].strip()
        print("Cartes reçues.")
        # print(sophie)
        return sophie
    
    if cmd == "clearfile":
        try:
            file = open("cartesvote.txt", "r+")
            file.truncate(0)
            file.close()
            return("done")
        except:
            return("Couldn't delete file")
        return
        
    if cmd == "voteshuffle":
        l = []
        try:
            file = open("cartesvote.txt", "r")
            line = file.readline()
            
            while line:
                # print(line)
                # print(l)
                l.append(line.strip("\n"))
                line = file.readline()
            file.close()
        except:
            return("erreur de recupération de données")
        try:
            r = randint(len(l))
            return("La carte " + str(l[r]) + " à été utilisée cette nuit...\n" + "Sauriez vous trouvez qui est à l'origine de ce maléfice ?")
        except:
            return("erreur choix")
        return
        
async def writetext(liste):
    try:
        file = open("cartesvote.txt", "a")
        for e in liste:
            file.write(str(e) + "\n")
        file.close()
        print("edit done")
    except:
        print("bug fichier edit")
        
        

## commandes

@client.event
async def on_message(message):
    try:
        if not message.guild: # On vérifie que le message ne soit pas un mp
            return
        
        if message.author.bot:  # On vérifie si le message reçu n'est pas originaire du bot
            return
        
        if message.content.find(prefix) != 0: # On vérifie que le préfixe de commande est présent
            return
            
        msgContent = message.content[len(prefix):].strip() # on récupère le contenu du message
        msgKeywords = msgContent.split(" ") # on en fait une liste
        
        if len(msgKeywords) == 0: # On vérifie que le message ne soit pas vide
            return
        
        retourcomm = commands(msgKeywords)
        
        if type(retourcomm) == list:
            await writetext(retourcomm)
            await message.channel.send("Cartes reçues !")
        elif type(retourcomm) == str:
            await message.channel.send(retourcomm)
        return
    except:
        await message.channel.send("Ça marche pas ton truc la")
        return






client.run(TOKEN)
