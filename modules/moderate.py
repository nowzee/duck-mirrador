import json
import re
import asyncio
import discord
import time


def detecter_insulte(phrase):
    phrase = phrase.lower()

    with open("modules/filtrage.txt") as f:
        insultes = [ligne.strip() for ligne in f]

    pattern = re.compile(r'(\b' + '|'.join(insultes) + r')\b')
    match = re.search(pattern, phrase)
    if match:
        return True
    return False


def detecter_zalgos(message, seuil=5):
    regex_zalgos = re.compile('[\u0300-\u036f\u0483-\u0489\u1dc0-\u1dff\u2de0-\u2dff\ua670-\ua69f\ufb00-\ufffd]+')
    nb_zalgos = len(regex_zalgos.findall(message))
    return nb_zalgos > seuil

excess_mentions = []
def excess_mention(mentions, seuil):
    for mention in mentions:
        if mentions.count(mention) >= seuil:
            return True
        return False


def detecter_majuscules_excessives(phrase, seuil):
    majuscules_regex = re.compile(r'[A-Z]{{{},{}}}'.format(seuil + 1, 100))
    if majuscules_regex.search(phrase):
        return True
    return False
user_messages = {}
def spamming(message):
    if message.author.id in user_messages:
        message_times = user_messages[message.author.id]
        message_times.insert(0, time.time())
        if len(message_times) > 6 and message_times[0] - message_times[-1] < 4:
            return True
    else:
        user_messages[message.author.id] = [time.time()]
usage_count = {}
def warning(user, message, bot, type):
    with open(f'database/server/{message.guild.id}.json') as file:
        data = json.load(file)
        logchannel = data['logchannel']
        file.close()
    log = bot.get_channel(int(logchannel))

    Avertissement = discord.Embed(color=discord.Colour.orange(), title="Avertissement",
                                  description="L'utisateur est avertit au bout de 4 avertissement celui-ci est banni")
    bannissement = discord.Embed(color=discord.Colour.red(), title="Bannisssement",
                                 description="Pour demande de deban contacter le support du bot\nPour obtenir plus d'information sur la personne banni !info + ID\n"
                                             "L'utilisateur sera mit en blacklisted pendant 24h sur les serveurs non rejoins")
    expulsion = discord.Embed(color=discord.Colour.dark_gold(), title="Expulsion",
                              description="L'utilisateur sera expulsé")

    if user in usage_count:
        usage_count[message.author.id] += 1
        if usage_count[message.author.id] == 2:
            Avertissement.add_field(name="Auto Modération",
                                    value=f"""Deuxieme avertissment pour : {message.author} .\n\nMotif suivant : {type}\nRaison suivante : {message.content}\nID : {message.author.id}\n Serveur : {message.guild.name}""",
                                    inline=True)
            Avertissement.set_author(name=message.author, icon_url=message.author.avatar)
            Avertissement.set_thumbnail(url=bot.user.avatar)
            asyncio.run_coroutine_threadsafe(log.send(embed=Avertissement),
                                             bot.loop)
        if usage_count[message.author.id] == 3:
            Avertissement.add_field(name="Auto Modération",
                                    value=f"""Troisieme avertissment pour : {message.author} .\n\nMotif suivant : {type}\nRaison suivante : {message.content}\nID : {message.author.id}\n Serveur : {message.guild.name}""",
                                    inline=True)
            Avertissement.set_author(name=message.author, icon_url=message.author.avatar)
            Avertissement.set_thumbnail(url=bot.user.avatar)
            asyncio.run_coroutine_threadsafe(log.send(embed=Avertissement),
                                             bot.loop)
        if usage_count[message.author.id] == 4:
            bannissement.add_field(name="Auto Modération",
                                   value=f"""L'utilisateur {message.author} à été banni  par Duck-Mirrador\n\nRaison : 4 avertissement\nID : {message.author.id}""",
                                   inline=True)
            bannissement.set_author(name=message.author, icon_url=message.author.avatar)
            bannissement.set_thumbnail(url=bot.user.avatar)
            asyncio.run_coroutine_threadsafe(log.send(embed=bannissement),
                                             bot.loop)
            asyncio.run_coroutine_threadsafe(message.guild.ban(user,
                                                               reason="Auto-Modération"), bot.loop)
    else:
        usage_count[message.author.id] = 1
        Avertissement.add_field(name="Auto Modération",
                                value=f"""{message.author} est classé sous surveillance pour Premier Avertissement.\n\nMotif suivant : {type}\nRaison suivante : {message.content}\nID : {message.author.id}\n Serveur : {message.guild.name}""",
                                inline=True)
        Avertissement.set_author(name=message.author, icon_url=message.author.avatar)
        Avertissement.set_thumbnail(url=bot.user.avatar)
        asyncio.run_coroutine_threadsafe(log.send(embed=Avertissement),
                                         bot.loop)
