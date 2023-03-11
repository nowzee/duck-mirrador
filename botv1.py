import os
from colorama import Fore, Style
from modules.command import *
from io import BytesIO
from modules.moderate import *
import time


def discord_bot(bot):

    @bot.event
    async def on_ready():
        TIME = (Fore.GREEN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        print(TIME + " Logged in as " + Fore.YELLOW + bot.user.name)
        print(TIME + " BOT ID " + Fore.YELLOW + str(bot.user.id))
        print(TIME + " Discord Version " + Fore.YELLOW + discord.__version__)
        statut_name = discord.Activity(type=discord.ActivityType.playing, name="Le canard est en ligne !duck_help")
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
                        await message.channel.send(f"Attention, {message.author.mention}, votre message contient des mentions excessives")

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
        try:
            username = ctx.author.name
            id = ctx.author.id
            avatars_image = ctx.author.avatar
            channels = 1079998728955506789
            channel = bot.get_channel(int(channels))
            buffer = xp_card(id, avatars_image, username)
            asyncio.run_coroutine_threadsafe(ctx.send(file=discord.File(buffer, filename="image.png")), bot.loop)
        except FileNotFoundError:
            await ctx.send(
                'Connect to duck-mirrador with the link : http://192.168.1.140:7777/connexion for set your xp card but your xp data is saved')

    @bot.command(name='info')
    async def user_info(ctx, user_id):
        try:
            user = await bot.fetch_user(user_id)
            member = ctx.guild.get_member(user.id)

            embed = discord.Embed(title=f"User Info - {user}", color=0x13EB8A)
            embed.add_field(name="Création du compte", value=user.created_at.strftime("Le %Y-%m-%d %H:%M:%S"))
            embed.add_field(name="Membre de ce serveur", value=member.joined_at.strftime("Depuis %Y-%m-%d %H:%M:%S"))
            embed.set_footer(text=f'ID : {user.id}')
            embed.set_thumbnail(url=user.avatar)

            await ctx.send(embed=embed)

        except Exception:
            await ctx.send("User not found.")

    @bot.command(name='info-account')
    async def user_info(ctx, user_id):
        try:
            user = await bot.fetch_user(user_id)

            embed = discord.Embed(title=f"User Info - {user}", description=f"ID: {user.id}", color=0x13EB8A)
            embed.add_field(name="Création du compte", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            embed.set_thumbnail(url=user.avatar)

            await ctx.send(embed=embed)

        except Exception:
            await ctx.send("User not found.")

    @bot.command()
    async def duck(ctx):
        perm = ctx.author.guild_permissions
        if perm.administrator:
            help = discord.Embed(color=discord.Colour.dark_gold(), title="Help",
                                 description="Commande administrateur et utilisateur")
            await ctx.send(embed=help)
        else:
            help = discord.Embed(color=discord.Colour.dark_gold(), title="Help",
                                 description="Commande utilisateur")
            help.add_field(name="rank",
                                    value=f"!rank",
                                    inline=True)
            help.add_field(name="\nMusique",
                           value="!play\n"
                                 "!disconnect\n"
                                 "Compatible avec deezer",
                           inline=True)
            help.add_field(name="Compte détail",
                           value="!info + id pour le serveur"
                                 "\n!info-account + id",inline=True)
            help.add_field(name="Dasboard",
                           value="!dashboard\n"
                                 "Go to your dashboard", inline=True)
            help.set_thumbnail(url=bot.user.avatar)
            await ctx.send(embed=help)

