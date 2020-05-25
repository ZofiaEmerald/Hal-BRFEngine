print("V 3.53")


## Importation des paquets

import discord
import math
import numpy as np
import random
import time
import os
from dotenv import load_dotenv
from discord.ext import commands

## Setup des variables nécéssaires

load_dotenv()
bank = list()
with open("brfenginebank.txt", "r") as file:
    line = file.readline()
    while line:
        bank.append(line.strip())
        line = file.readline()
TOKEN = bank[0]
GUILD = bank[1]
SECRET_NUMBER = random.randint(0,100)

bot = commands.Bot(command_prefix='&')

## Fonctions complémentaires

async def appendfile(filepath, text):
    with open(filepath, "a") as file:
        file.write(text + "\n")
    return

async def recupfile(filepath):
    IDlist = list()
    with open(filepath, "r") as file:
        line = file.readline()
        while line:
            IDlist.append(line.strip())
            line = file.readline()
    return IDlist

async def delfile(filepath):
    with open(filepath, "w") as file:
        file.truncate(0)
    return

def findinliste(text, list):

    text = text.lower()
    text = text.split()
    i = 0
    sujet = ""

    for j in range(len(list)):
        mot = list[j]
        mot = mot.lower()

        if mot != text[i]:
            i = 0

        if mot == text[i]:
            i +=1

            if i == (len(text)) and (j+1 < len(list)-1):
                Jsujet = j+1

                if (list[Jsujet] in ["un", "le", "la", "une"]) and (Jsujet < len(list)-1):
                    print(Jsujet, len(list))
                    sujet = (list[Jsujet] + " " + list[Jsujet+1])

                else:
                    sujet = list[Jsujet]
                break

    return sujet

## Gestion des évents

@bot.event
async def on_ready():

    guild = discord.utils.get(bot.guilds, name=GUILD)

    print(
    f"\n{bot.user.name} is connected to Discord.\n"
    f"Connection ID : {bot.user.id}\n"
    f"Connected to guild : {guild.name}\n"
    f"Guild ID : {guild.id}\n"
    f"Secret number for raising exception is {SECRET_NUMBER}\n"
    )

    members = "\n - ".join([member.name for member in guild.members])
    print(f"Guild Members :\n - {members}", "\n")


@bot.event
async def on_member_join(member):

    await member.create_dm()
    await member.dm_channel.send(
    f"Bienvenue à toi, {member.name} ! Prêt à commencer une partie endiablée de Bad Red Fox ?"
    )


@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("Commande inconnue :confused:")
    elif isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send("Echec d'éxécution de la commande... :sad:")
        raise error
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f"Erreur de syntaxe : un argument est manquant !")
    else:
        raise error

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    text = str(message.content).lower()
    splitext = text.split()
    listesuis = ["je suis"]

    for suis in listesuis:
        sujet = findinliste(suis, splitext)

        if sujet:
            r = np.random.rand()

            if r < 0.9:
                await message.channel.send(f"Salut {sujet} ! Moi c'est {bot.user.name} !")
            break
    await bot.process_commands(message)



## Commandes normales

@bot.command(name = "stop", help = "Déconnecte le bot")
async def stop_bot(ctx, number):
    if int(number) == SECRET_NUMBER:
        await ctx.send("Ok bye !")
        await bot.logout()
    else:
        await ctx.send("C'est pas ça le mot magique...")


@bot.command(name = "addplayer", help = "Permet de vous ajouter à la liste des joueurs.")
async def add_player(ctx):
    id = str(ctx.author.id)
    await appendfile("Listejoueurs.txt", id)
    await ctx.send(f"Joueur {ctx.author.name} enregistré.")


@bot.command(name = "resetplayers", help = "Permet de supprimer la liste des joueurs participants.")
async def reset_players(ctx):

    await delfile("Listejoueurs.txt")

    await ctx.send("Liste des joueurs effacée.")


@bot.command(name = "shout", help = "Permet d'envoyer un message anonyme à tous les joueurs.")
async def dm_all(ctx):
    await delfile("answerme.txt")
    await appendfile("answerme.txt", str(ctx.author.id))
    IDlist = await recupfile("Listejoueurs.txt")
    transmission = ctx.message.content[7:]
    if not IDlist:
        await ctx.send("Aucun joueur ne participe !")

    guild = discord.utils.get(bot.guilds, name=GUILD)

    for ID in IDlist:
        user = guild.get_member(int(ID))
        if user:
            if not user.dm_channel:
                await user.create_dm()

            await user.dm_channel.send(transmission)

    await ctx.send("Message envoyé.")


@bot.command(name = "whisper", help = "Permet d'envoyer un message anonyme à un ou plusieurs joueur.")
async def dm_one(ctx):

    await delfile("answerme.txt")
    await appendfile("answerme.txt", str(ctx.author.id))

    transmission = ctx.message.content[9:]
    mention_list = ctx.message.mentions
    transmission = transmission[23*len(mention_list):]
    IDlist = await recupfile("Listejoueurs.txt")
    fail = list()
    success = list()

    for mention in mention_list:

        id = mention.id

        if str(id) in IDlist:

            guild = discord.utils.get(bot.guilds, name=GUILD)
            user = guild.get_member(int(id))


            if user:
                if not user.dm_channel:
                    await user.create_dm()

                await user.dm_channel.send(transmission)
                success.append(mention)
        else:
            fail.append(mention)
    if not fail:
        await ctx.send("Message envoyé.")
    elif not success:
        await ctx.send("Echec de l'envoi : aucune de ces personnes ne se sont inscrites !")
    else:
        failed = "\n - ".join([mention.name for mention in fail])
        prompt = f"Le message n'a pas pu être envoyé aux joueurs suivants car ils ne sont pas inscrits:\n - {failed}\n"
        await ctx.send(prompt)


@bot.command(name = "answer", help = "permet de répondre à la dernière personne ayant envoyé un message anonyme.")
async def answer_me(ctx):

    [id] = await recupfile("answerme.txt")
    id = int(id)
    transmission = ctx.message.content[8:]
    guild = discord.utils.get(bot.guilds, name=GUILD)
    user = guild.get_member(int(id))

    if user:
        if not user.dm_channel:
            await user.create_dm()

        await user.dm_channel.send(transmission)
        await ctx.send("Message envoyé.")

    else:
        await ctx.send("Echec de l'envoi, destinataire introuvable.")


@bot.command(name = "nextplayer", help = "Permet de désigner la personne qui doit jouer ensuite")
async def next_player(ctx):

    ID_list = await recupfile("Listejoueurs.txt")
    played_list = await recupfile("playedlist.txt")

    if len(ID_list) == len(played_list):

        await delfile("playedlist.txt")
        idjoueur = random.choice(ID_list)


    else:
        if len(ID_list) == len(played_list)-1:
            await ctx.send("Tu es le dernier joueur, n'oublie pas de signaler que la nuit se termine avec un &shout")

        idjoueur = random.choice(ID_list)

        while idjoueur in played_list:
            idjoueur = random.choice(ID_list)

    await appendfile("playedlist.txt", idjoueur)
    guild = discord.utils.get(bot.guilds, name=GUILD)
    joueur = guild.get_member(int(idjoueur))

    if joueur:
        if not joueur.dm_channel:
            await joueur.create_dm()

        await joueur.dm_channel.send("A toi de jouer !! (yu-gi-oh oh oh oh)")
        await ctx.send("Commande exécutée.")

    else:
        await ctx.send("Echec de l'envoi, destinataire introuvable.")


@bot.command(name = "resetplayed", help = "Réinitialise la liste des joueurs ayant déjà joué")
async def rest_played(ctx):

    await delfile("playedlist.txt")
    await ctx.send("Fichier effacé.")

@bot.command(name = "dice", help = "Permet de faire rouler autant de dés que nécéssaire en indiquant le nombre de faces.\nSyntaxe : &rolldice nombre_de_faces nombre_de_faces etc...")
async def roll_dice(ctx, *args: int):

    liste = list()
    for dice in args:
        r = random.randint(1,dice)
        liste.append(str(r))

    resultats = "\n - ".join(liste)
    await ctx.send(f"Voici les résultats de vos lancers :\n - {resultats}\n")

## Commandes de rôle

@bot.command(name = "settriplet", help = "Signale au jeu que vous possédez un triplet.")
async def triplet_set(ctx):

    id = str(ctx.author.id)
    await appendfile("Listetriplet.txt", id)
    await ctx.send(f"Joueur {ctx.author.name} enregistré.")


@bot.command(name = "resettriplet", help = "Efface la liste des triplets.")
async def reset_triplet(ctx):

    await delfile("Listetriplet.txt")

    await ctx.send("Liste des triplet effacée.")


@bot.command(name = "triplet", help = "Choisit un triplet au hasard parmis les autres qui devra mourir à votre place.")
async def triplet_action(ctx):

    liste_triplet_id = await recupfile("Listetriplet.txt")
    guild = discord.utils.get(bot.guilds, name=GUILD)

    if len(liste_triplet_id) != 3:
        await ctx.send("Le nombre de triplets enregistrés est invalide.")

    else:
        while str(ctx.message.author.id) in liste_triplet_id:
            liste_triplet_id.remove(str(ctx.message.author.id))

        if liste_triplet_id:
            r = random.choice(liste_triplet_id)
            cible = guild.get_member(int(r))

            if not cible.dm_channel:

                await cible.create_dm()

            await cible.dm_channel.send("Votre triplet vient de mourir... Veuillez le retirer du jeu.")

        else:

            if not ctx.message.author.dm_channel:
                await ctx.message.author.create_dm()

            await ctx.message.author.dm_channel.send("Vous avez tous les triplets... Vous pouvez choisir celui à sacrifier.")
    await ctx.send("Effet appliqué.")


@bot.command(name = "informateur", help = "Choisit une question que vous devez poser à votre cible ! (informateur)")
async def select_question(ctx):

    liste = [
    "Combien il te reste de loup ?",
    "Combien il te reste de cartes à effet ?",
    "Quel est la dernière carte que tu as utilisé ?",
    "Te reste t-il des loups ?",
    "Te reste t-il une carte à effet ?",
    "As-tu  plus de loup que de cartes à effets ?",
    "Est-ce que ça va ?",
    "Combien de carte importante as-tu perdu ?",
    "Possède tu une carte trompeuse ? (loup imberbe etc..)",
    "Possède tu une carte informatrice ? (voyante, informateur, spiritiste etc..)"
    ]

    Message = f"Vous devez poser la question suivante à votre victime :\n{random.choice(liste)}"
    await ctx.send(Message)


@bot.command(name = "moonchild", help = "Révèle la volonté de la lune!(enfant de la lune)")
async def moon_child(ctx):

    liste = [
    "les loups tuent deux fois cette nuit",
    "Pas de lune : les loup ne font que blesser leur victime sans les tuer (juste les dévoile)",
    "pas de loup ce soir / peut utiliser plusieurs loups si on en a",
    "les loups qui attaque ce soir seront dévoilé",
    "les loups ne peuvent pas choisir leur victimes (le hasard)",
    "un villageois devient un loup dans chaque village (ou un seul pour plus de fun)",
    "un seul village peut attaquer ce soir / les meurtres ne sont plus anonyme ce soir",
    "les morts sont dévoilé ce soir",
    "mais rien ne se passe",
    "les loups utiliser deviendront des villageois",
    "les loups ne peuvent mourir ce soir",
    "seules les loups peuvent être tué ce soir",
    "les loups mort reviennent à la vie pour cette nuit (en gros on peut juste utiliser leur effets)",
    "les loups doivent tué dans leur propre village cette nuit",
    "si un loup mange une carte à effet il meurt",
    "Seuls les personnes qui ont un seul loup peuvent tué ce soir",
    "Seul la personne avec le moins de villageois peut tuer",
    "Chaque joueur doit attaqué le même village qu'au tour précédent",
    "Les joueurs doivent attaqué le village avec le plus de villageois (sauf lui même qui n'attaque pas"
    ]

    IDlist = await recupfile("Listejoueurs.txt")
    transmission = random.choice(liste)

    if not IDlist:
        await ctx.send("Aucun joueur ne participe !")

    guild = discord.utils.get(bot.guilds, name=GUILD)

    for ID in IDlist:
        user = guild.get_member(int(ID))
        if user:
            if not user.dm_channel:
                await user.create_dm()

            await user.dm_channel.send(transmission)

    await ctx.send("Pouvoir appliqué !")


## Commandes bullshit



## Lancement du bot

bot.run(TOKEN)
