import os

from colorama import Fore, Style
from modules.command import *
from modules.moderate import *
from discord import app_commands
import time
import sqlite3


def discord_bot(bot, HOSTS, PORTS):
    @bot.event
    async def on_ready():
        TIME = (Fore.GREEN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        print(TIME + " Logged in as " + Fore.YELLOW + bot.user.name)
        print(TIME + " BOT ID " + Fore.YELLOW + str(bot.user.id))
        print(TIME + " Discord Version " + Fore.YELLOW + discord.__version__)
        statut_name = discord.Activity(type=discord.ActivityType.playing, name="!duck for more help\nBeta version")
        statut_online = discord.Status.online
        await bot.change_presence(status=statut_online, activity=statut_name)
        synced = await bot.tree.sync()
        print(TIME + " Commandes synchro : " + Fore.YELLOW + str(len(synced)))
        print("Fonctionnel !")

    @bot.event
    async def on_guild_remove(guild):
        guilds = guild.id
        os.remove(f"database/server/{guilds}.json")

    @bot.event
    async def on_guild_join(guild):
        serveur = guild.id
        with open(f"database/server/{serveur}.json", "w+") as file:
            data = {
                "mots_interdit": "delete_warn",
                "anti_spam": "delete_warn",
                "lien_filtered": "delete_warn",
                "zalgo": "delete_warn",
                "Mentions_excessif": "delete_warn",
                "Majuscule_excessif": "delete_warn",
                "emojis_excessif": "delete_warn",
                "logchannel": "None",
                "xplogchannel": "None",
                "eventchannel": "None"
            }
            json.dump(data, file)
            file.close()

    @bot.event
    async def on_message(message):
        # filtrage
        phrase = message.content
        mentions = re.findall(r'<@!?(\d+)>', message.content)
        user = message.author.id

        perm = message.author.guild_permissions
        invite_regex = r"(?:https?://)?discord(?:.gg|(?:app)?.com/invite)/([a-zA-Z0-9-]+)"

        if not message.content.startswith(bot.command_prefix):
            # Connexion à la base de données
            conn = sqlite3.connect('database/xpdata.db')
            cursor = conn.cursor()

            cursor.execute('CREATE TABLE IF NOT EXISTS utilisateurs ('
                           'id INTEGER,'
                           'nom TEXT,'
                           'serveur_id INTEGER,'
                           'experience INTEGER,'
                           'niveau INTEGER,'
                           'PRIMARY KEY (id, serveur_id)'
                           ')')

            # Récupération de l'ID du serveur et de l'utilisateur
            serveur_id = message.guild.id
            utilisateur_id = message.author.id

            # Vérification si l'utilisateur existe dans la base de données pour ce serveur
            cursor.execute('SELECT id, experience, niveau FROM utilisateurs WHERE id = ? AND serveur_id = ?',
                           (utilisateur_id, serveur_id))
            result = cursor.fetchone()

            # Si l'utilisateur n'existe pas, on l'ajoute à la table des utilisateurs
            if result is None:
                cursor.execute(
                    'INSERT INTO utilisateurs (id, nom, serveur_id, experience, niveau) VALUES (?, ?, ?, ?, ?)',
                    (utilisateur_id, message.author.name, serveur_id, 0, 1))

            # Sinon, on récupère son expérience et son niveau actuel
            else:
                utilisateur_experience = result[1]
                utilisateur_niveau = result[2]

                # Ajout de l'expérience à l'utilisateur
                utilisateur_experience += 1
                cursor.execute('UPDATE utilisateurs SET experience = ? WHERE id = ? AND serveur_id = ?',
                               (utilisateur_experience, utilisateur_id, serveur_id))
                # Constantes
                SEUIL_EXPERIENCE_NIVEAU = 100 * utilisateur_niveau

                # Passage au niveau supérieur si l'utilisateur atteint le seuil d'expérience
                if utilisateur_experience >= SEUIL_EXPERIENCE_NIVEAU:
                    utilisateur_niveau += 1
                    cursor.execute('UPDATE utilisateurs SET niveau = ?, experience = ? WHERE id = ? AND serveur_id = ?',
                                   (utilisateur_niveau, 25, utilisateur_id, serveur_id))
                    await message.channel.send(f"{message.author.mention} a atteint le niveau {utilisateur_niveau} !")

            # Validation des changements dans la base de données
            conn.commit()
            conn.close()

            if perm.administrator:
                pass
            else:
                with open(f"database/server/{message.guild.id}.json") as file:
                    config = json.load(file)

                if re.search(invite_regex, message.content):
                    if config["lien_filtered"] == "disable":
                        pass
                    elif config["lien_filtered"] == "delete_warn":
                        await message.delete()
                        type = 'invitation discord'
                        warning(user, message, bot, type)
                        await message.channel.send(
                            f"{message.author.mention}, les invitations Discord ne sont pas autorisées ici !")
                    else:
                        await message.delete()
                        await message.channel.send(
                            f"{message.author.mention}, les invitations Discord ne sont pas autorisées ici !")

                if detecter_insulte(phrase):

                    if config["mots_interdit"] == 'disable':
                        pass
                    elif config["mots_interdit"] == 'delete_warn':
                        await message.delete()
                        type = 'mots inapproprié'
                        warning(user, message, bot, type)
                    else:
                        await message.delete()

                if excess_mention(mentions, seuil=5):
                    if config["Mentions_excessif"] == 'disable':
                        pass
                    elif config["Mentions_excessif"] == 'delete_warn':
                        await message.delete()
                        type = 'mentions excessives'
                        warning(user, message, bot, type)
                    else:
                        await message.delete()
                        await message.channel.send(
                            f"Attention, {message.author.mention}, votre message contient des mentions excessives")

                if detecter_majuscules_excessives(phrase, seuil=15):
                    if config["Majuscule_excessif"] == 'disable':
                        pass
                    elif config["Majuscule_excessif"] == 'delete_warn':
                        await message.delete()
                        type = 'Majuscules excessives'
                        warning(user, message, bot, type)
                    else:
                        await message.delete()
                        await message.channel.send(
                            f"Attention, {message.author.mention}, votre message contient trop de majuscule")

                if detecter_zalgos(phrase, seuil=5):
                    if config["zalgo"] == 'disable':
                        pass
                    elif config["zalgo"] == 'delete_warn':
                        await message.delete()
                        type = 'utilisation de zalgo'
                        warning(user, message, bot, type)
                    else:
                        await message.delete()
                        await message.channel.send(
                            f"Attention, {message.author.mention}, votre message contient des zalgos")
                if spamming(message):
                    if config["anti_spam"] == 'disable':
                        pass
                    elif config["anti_spam"] == 'delete_warn':
                        await message.delete()
                        type = 'Détection de spam'
                        warning(user, message, bot, type)
                    else:
                        await message.delete()
                        await message.channel.send(
                            f"Attention, {message.author.mention}, votre message est considéré comme un spam")

        else:
            if perm.administrator:
                pass
            else:
                if detecter_insulte(phrase):
                    await message.delete()
                    type = 'mots inapproprié'
                    warning(user, message, bot, type)
            await bot.process_commands(message)

    @bot.command()
    async def rank(ctx):
        global niveau, experience, SEUIL_EXPERIENCE_NIVEAU, log
        try:
            serveur_id = ctx.guild.id
            utilisateur_id = ctx.author.id

            # Ouvrir la base de données
            conn = sqlite3.connect('database/xpdata.db')

            # Créer un curseur
            cur = conn.cursor()

            # Exécuter une requête SQL pour récupérer les données d'un serveur Discord
            cur.execute('SELECT * FROM utilisateurs WHERE serveur_id = ? AND id = ?', (serveur_id, utilisateur_id))

            # Récupérer les résultats de la requête
            resultats = cur.fetchall()

            # Fermer le curseur et la connexion à la base de données
            cur.close()
            conn.close()

            # Traiter les résultats
            for resultat in resultats:
                experience = resultat[3]
                niveau = resultat[4]
                SEUIL_EXPERIENCE_NIVEAU = 100 * niveau

            username = ctx.author.name
            id = ctx.author.id
            avatars_image = ctx.author.avatar

            with open(f'database/server/{ctx.guild.id}.json') as file:
                data = json.load(file)
                xplogchannel = data['xplogchannel']
                file.close()
            log = bot.get_channel(int(xplogchannel))

            buffer = xp_card(id, avatars_image, username, niveau, experience, SEUIL_EXPERIENCE_NIVEAU)
            asyncio.run_coroutine_threadsafe(log.send(file=discord.File(buffer, filename="image.png")), bot.loop)
        except FileNotFoundError:
            await ctx.send(
                f'Connect to duck-mirrador with the link : http://{HOSTS}:{PORTS}/connexion for set your xp card but your xp data is saved')
        except Exception as e:
            print(e)
            try:
                with open(f'database/server/{ctx.guild.id}.json') as file:
                    data = json.load(file)
                    xplogchannel = data['xplogchannel']
                    file.close()
                log = bot.get_channel(int(xplogchannel))
                username = ctx.author.name
                id = ctx.author.id
                avatars_image = ctx.author.avatar
                SEUIL_EXPERIENCE_NIVEAU = 100 * niveau
                buffer = xp_card(id, avatars_image, username, niveau, experience, SEUIL_EXPERIENCE_NIVEAU)
                await log.send(file=discord.File(buffer, filename="image.png"))
            except Exception:
                username = ctx.author.name
                id = ctx.author.id
                avatars_image = ctx.author.avatar
                SEUIL_EXPERIENCE_NIVEAU = 100 * niveau

                buffer = xp_card(id, avatars_image, username, niveau, experience, SEUIL_EXPERIENCE_NIVEAU)
                await ctx.send(file=discord.File(buffer, filename="image.png"))

    @bot.tree.command(name='info')
    @app_commands.describe(member='Enter member')
    async def user_info(interaction: discord.Interaction, member:discord.Member=None):
        try:

            embed = discord.Embed(title=f"User Info - {member.name}", color=0x13EB8A)
            embed.add_field(name="Création du compte", value=member.created_at.strftime("Le %Y-%m-%d %H:%M:%S"))
            embed.add_field(name="Membre de ce serveur", value=member.joined_at.strftime("Depuis %Y-%m-%d %H:%M:%S"))
            embed.set_footer(text=f'ID : {member.id}')
            embed.set_thumbnail(url=member.avatar)

            await interaction.response.send_message(embed=embed)

        except Exception:
            await interaction.response.send_message("User not found.")

    @bot.tree.command(name='dashboard')
    async def dashboard(interaction: discord.Interaction):
        await interaction.response.send_message(f"http://{HOSTS}:{PORTS}/dashboard")

    @bot.tree.command(name='duck')
    async def duck(interaction: discord.Interaction):
        help = discord.Embed(color=discord.Colour.dark_gold(), title="Help",
                             description="Commande utilisateur")
        help.add_field(name="rank",
                       value=f"!rank",
                       inline=True)
        help.add_field(name="Compte détail",
                       value="\n/info+ @member", inline=True)
        help.add_field(name="Dasboard",
                       value="/dashboard\n"
                             "Go to your dashboard", inline=True)
        help.set_thumbnail(url=bot.user.avatar)
        await interaction.response.send_message(embed=help, ephemeral=True)
