from flask import Flask, redirect, url_for, request, render_template, session, Response
import threading
import sqlite3
from modules.command import *
from datetime import timedelta
from botv1 import discord_bot
from discord.ext import commands

app = Flask(__name__)
app.secret_key = "my_secret_key"

app.permanent_session_lifetime = timedelta(days=30)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

PORTS = 7777 # Port
HOSTS = '0.0.0.0' # Host
redirect_url = "ip or host" # redirect url
token = 'Token' #token bot
CLIENT_IDS = "clientid" # client id bot
CLIENT_SECRETS = "clientsecret" #client secret bot


@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('dashboard'))
@app.after_request
def add_header(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.errorhandler(500)
def page_not_found(error):
    return redirect(url_for('connexion'))


# Définir la vue pour la page d'autorisation de Discord
@app.route("/discord-authorized", methods=["GET"])
def discord_authorized():
    global r
    code = request.args.get('code')
    API_ENDPOINT = 'https://discord.com/api'
    CLIENT_ID = CLIENT_IDS
    CLIENT_SECRET = CLIENT_SECRETS
    REDIRECT_URI = f'http://{redirect_url}:7777/discord-authorized'
    discord_api = 'https://discordapp.com/api'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        return redirect(url_for('connexion'))
    data = r.json()
    name = data['access_token']
    url = discord_api + "/users/@me"
    url2 = discord_api + "/users/@me/guilds"
    url_connec = discord_api + "/users/@me/connections"

    headerss = {
        "Authorization": "Bearer {}".format(name)
    }
    user_object = requests.get(url=url, headers=headerss)
    user_object1 = requests.get(url=url2, headers=headerss)
    user_object2 = requests.get(url=url_connec, headers=headerss)
    user_json = user_object.json()
    user_json1 = user_object1.json()
    user_json2 = user_object2.json()

    print(user_json2)

    server_list = []
    for i in user_json1:
        owner = i['owner']
        if owner == True:
            name_server = i['name']
            id_server = i['id']
            icon_server = i['icon']
            icon_image = f'https://cdn.discordapp.com/icons/{id_server}/{icon_server}.webp?size=96'
            session['rank'] = 'Administrateur'
            server_list.append({'nom': name_server, 'id_server': id_server, 'icon': icon_image, 'url': url})

    session["serveur_lis"] = server_list
    print(user_json)

    username = user_json.get("username")
    tag = user_json.get("discriminator")
    ids = user_json.get("id")
    email = user_json.get("email")
    avatar = user_json.get("avatar")
    mfa_enabled = user_json.get("mfa_enabled")
    avatars_image = f'https://cdn.discordapp.com/avatars/{ids}/{avatar}.png'
    email_verified = user_json.get("verified")
    ip_adress = request.remote_addr
    user_agent = request.headers.get('User-Agent')

    if email_verified == True:
        session['username'] = f'{username}#{tag}'
        session['identifiant'] = ids
        session['email'] = email
        session['avatar'] = avatars_image
        session['adress_ip'] = ip_adress

        if 'Windows' in user_agent:
            os = 'Windows'
        elif 'Linux' in user_agent:
            os = 'Linux'
        elif 'Mac' in user_agent:
            os = 'Macos'
        else:
            os = 'Autre'
        with open(f"database/user/{ids}.json", "w+") as file:
            data = {
                "Username": f"{username}#{tag}",
                "Identifiant": f"{ids}",
                "Ip": f"{ip_adress}",
                "email": f"{email}",
                "OS": f"{os}",
                "Fond_xp": "bg.png",
                "mfa_enabled": f"{mfa_enabled}"
            }
            json.dump(data, file)
        return redirect(url_for('select_serveur'))
    else:
        return 'please verify your email'


@app.route("/connexion", methods=["POST", "GET"])
def connexion():
    session.clear()
    session.modified = True
    return render_template('authenticate.html')


@app.route("/discordss", methods=["GET"])
def discordss():
    return redirect(
        f'https://discord.com/api/oauth2/authorize?client_id={CLIENT_IDS}&redirect_uri=http%3A%2F%2F{redirect_url}%3A7777%2Fdiscord-authorized&response_type=code&scope=identify%20guilds%20email%20connections')


@app.route("/administration", methods=["POST", "GET"])
def administration():
    return render_template('administration/admin.html')


@app.route("/administration/<more_info>", methods=["POST", "GET"])
def more_info(more_info):
    print(more_info)
    return render_template('administration/admin.html')


@app.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    if request.method == 'POST':
        server_icon = request.form.get('server_icon')
        server_name = request.form.get('server_name')
        server_id = request.form.get('server_id')
        session["server_icon"] = server_icon
        session["server_name"] = server_name
        session["idserver"] = server_id

        if 'username' and 'email' and 'adress_ip' and 'identifiant' and 'avatar' in session:
            username = session['username']
            ids = session['identifiant']
            avatars_image = session['avatar']
            adresse_ip = session['adress_ip']
            id_serveur = session["idserver"]
            try:
                member_server = count_member(id_serveur, bot)
            except AttributeError:
                return redirect(
                    f'https://discord.com/api/oauth2/authorize?client_id={CLIENT_IDS}&permissions=8&scope=bot')

            server_list = session["serveur_lis"]
            name_server = session["server_name"]
            icon_server = session["server_icon"]

            return render_template('index.html', avatars_image=avatars_image, username=f'{username}',
                                   server_list=server_list, member_server=member_server, name_server=name_server,
                                   icon_server=icon_server, id_serveur=id_serveur)
        else:
            print('aucune session')
            return redirect(url_for('connexion'))
    elif request.method == 'GET':
        if 'username' and 'email' and 'adress_ip' and 'identifiant' and 'avatar' in session:
            if 'idserver' in session:
                username = session['username']
                avatars_image = session['avatar']
                id_serveur = session["idserver"]
                name_server = session["server_name"]
                icon_server = session["server_icon"]
                try:
                    member_server = count_member(id_serveur, bot)
                except AttributeError:
                    return redirect(
                        f'https://discord.com/api/oauth2/authorize?client_id={CLIENT_IDS}&permissions=8&scope=bot')

                server_list = session["serveur_lis"]

                return render_template('index.html', avatars_image=avatars_image, username=f'{username}',
                                       server_list=server_list, member_server=member_server, name_server=name_server,
                                       icon_server=icon_server, id_serveur=id_serveur)
            else:
                return redirect(url_for('select_serveur'))
        else:
            return redirect(url_for('connexion'))


@app.route("/info_account", methods=["GET"])
def info_account():
    global niveau, experience, SEUIL_EXPERIENCE_NIVEAU
    if 'username' and 'email' and 'adress_ip' and 'identifiant' and 'avatar' in session:
        username = session['username']
        id = session['identifiant']
        avatars_image = session['avatar']
        id_serveur = session["idserver"]
        serveur = session["server_name"]
        Rank = session['rank']

        with open(f"database/user/{id}.json", "r") as file:
            data = json.load(file)
            fond = data["Fond_xp"]
            if fond == 'bg.png':
                fonds = 'Foret verte'
            elif fond == 'bg2.png':
                fonds = 'Foret grise'
            elif fond == 'bg3.jpg':
                fonds = 'ciel étoilé'
            elif fond == 'bg4.jpg':
                fonds = 'eclair violet'
            elif fond == 'bg5.jpg':
                fonds = 'Petite maison'
            elif fond == 'bg6.jpg':
                fonds = 'fenetre mouillé'
            elif fond == 'bg7.jpg':
                fonds = 'planche de bois'


        try:
            # Ouvrir la base de données
            conn = sqlite3.connect('database/xpdata.db')

            # Créer un curseur
            cur = conn.cursor()

            # Exécuter une requête SQL pour récupérer les données d'un serveur Discord
            cur.execute('SELECT * FROM utilisateurs WHERE serveur_id = ? AND id = ?', (id_serveur, id))

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
        except sqlite3.OperationalError:
            niveau = 1
            experience = 0
            SEUIL_EXPERIENCE_NIVEAU = 100 * niveau

        try:
            buffer = settings_xp_card(bot, id, id_serveur, avatars_image, username, niveau, experience,
                                      SEUIL_EXPERIENCE_NIVEAU)
        except NameError:
            niveau = 1
            experience = 0
            SEUIL_EXPERIENCE_NIVEAU = 100 * niveau
            buffer = settings_xp_card(bot, id, id_serveur, avatars_image, username, niveau, experience,
                                      SEUIL_EXPERIENCE_NIVEAU)
        return render_template('account/account.html', username=username, rank=Rank, identifiant=id,
                               avatars_image=avatars_image, serveur=serveur, buffer=buffer, value=fond, fonds=fonds)
    else:
        return redirect(url_for('connexion'))


@app.route("/modération", methods=["GET"])
def moderation():
    global channel_id_name, channel_ids, xp_id_name, xp_ids
    if 'username' and 'email' and 'adress_ip' and 'identifiant' and 'avatar' in session:
        if 'idserver' in session:
            id_serveur = session["idserver"]

            with open(f"database/server/{id_serveur}.json", "r") as file:
                data = json.load(file)
                mots_interdit = data["mots_interdit"]
                anti_spam = data["anti_spam"]
                lien_filtered = data["lien_filtered"]
                zalgo = data["zalgo"]
                Mentions_excessif = data["Mentions_excessif"]
                Majuscule_excessif = data["Majuscule_excessif"]

                if mots_interdit == 'delete':
                    mots_interdits = "Supprimer le message"
                elif mots_interdit == 'delete_warn':
                    mots_interdits = "Supprimer le message & ajouter un avertissement"
                elif mots_interdit == 'disable':
                    mots_interdits = "Désactiver"

                if anti_spam == 'delete':
                    anti_spams = "Supprimer le message"
                elif anti_spam == 'delete_warn':
                    anti_spams = "Supprimer le message & ajouter un avertissement"
                elif anti_spam == 'disable':
                    anti_spams = "Désactiver"

                if lien_filtered == 'delete':
                    lien_filtereds = "Supprimer le message"
                elif lien_filtered == 'delete_warn':
                    lien_filtereds = "Supprimer le message & ajouter un avertissement"
                elif lien_filtered == 'disable':
                    lien_filtereds = "Désactiver"

                if zalgo == 'delete':
                    zalgos = "Supprimer le message"
                elif zalgo == 'delete_warn':
                    zalgos = "Supprimer le message & ajouter un avertissement"
                elif zalgo == 'disable':
                    zalgos = "Désactiver"

                if Mentions_excessif == 'delete':
                    Mentions_excessifs = "Supprimer le message"
                elif Mentions_excessif == 'delete_warn':
                    Mentions_excessifs = "Supprimer le message & ajouter un avertissement"
                elif Mentions_excessif == 'disable':
                    Mentions_excessifs = "Désactiver"

                if Majuscule_excessif == 'delete':
                    Majuscule_excessifs = "Supprimer le message"
                elif Majuscule_excessif == 'delete_warn':
                    Majuscule_excessifs = "Supprimer le message & ajouter un avertissement"
                elif Majuscule_excessif == 'disable':
                    Majuscule_excessifs = "Désactiver"

            log_id = data["logchannel"]
            xplogchannel_id = data["xplogchannel"]

            headersss = {
                "Authorization": "Bot {}".format(
                    token)
            }
            url_guild = f'https://discord.com/api/v9/guilds/{id_serveur}/channels'
            url_channel = f'https://discord.com/api/v9//channels/{log_id}'
            xplogchannel_id_channel = f'https://discord.com/api/v9//channels/{xplogchannel_id}'

            response_guild = requests.get(url_guild, headers=headersss)
            response_url_channel = requests.get(url_channel, headers=headersss)
            responsexplogchannel_id_channel = requests.get(xplogchannel_id_channel, headers=headersss)

            channels = response_guild.json()
            channel_id = response_url_channel.json()
            xp_id = responsexplogchannel_id_channel.json()
            try:
                if channel_id["code"] == 50035:
                    channel_id_name = "Selectionner un salon"
                    channel_ids = None

            except Exception:
                channel_id_name = channel_id["name"]
                channel_ids = log_id
            try:
                if xp_id["code"] == 50035:
                    xp_id_name = "Selectionner un salon"
                    xp_ids = None
            except Exception:
                xp_ids = xplogchannel_id
                xp_id_name = xp_id["name"]

            channelss = []
            for y in channels:
                if y['type'] == 0:
                    id_channel = y['id']
                    name_channel = y['name']
                    channelss.append({'name_channel': name_channel, 'id_channel': id_channel})

            return render_template("moderate/modération.html", mots_interdit=mots_interdit,
                                   mots_interdits=mots_interdits, anti_spam=anti_spam, anti_spams=anti_spams,
                                   lien_filtered=lien_filtered, lien_filtereds=lien_filtereds,
                                   Mentions_excessif=Mentions_excessif, Mentions_excessifs=Mentions_excessifs,
                                   Majuscule_excessif=Majuscule_excessif, Majuscule_excessifs=Majuscule_excessifs,
                                   zalgo=zalgo, zalgos=zalgos,
                                   channelss=channelss, channel_id_name=channel_id_name, channel_ids=channel_ids, xp_id_name=xp_id_name, xp_ids=xp_ids)
        else:
            return redirect(url_for('select_serveur'))
    else:
        return redirect(url_for('connexion'))


@app.route("/select_server", methods=["GET"])
def select_serveur():
    server_list = session["serveur_lis"]
    return render_template('select_server.html', server_list=server_list)


@app.route("/settings", methods=["POST"])
def settings_serveur():
    # Filtrage
    serveur = session["idserver"]
    mots_interdit = request.form.get('mots_interdis')
    anti_spam = request.form.get('anti-spam')
    lien_filtered = request.form.get('lien')
    zalgo = request.form.get('zalgos')
    Mentions_excessif = request.form.get('mentions')
    Majuscule_excessif = request.form.get('majuscules')
    emojis_excessif = request.form.get('emoji')
    logchannel = request.form.get('logchannel')
    xplogchannel = request.form.get('xplogchannel')
    with open(f"database/server/{serveur}.json", "r+") as file:
        data = json.load(file)
        data["mots_interdit"] = mots_interdit
        data["anti_spam"] = anti_spam
        data["lien_filtered"] = lien_filtered
        data["zalgo"] = zalgo
        data["Mentions_excessif"] = Mentions_excessif
        data["Majuscule_excessif"] = Majuscule_excessif
        data["emojis_excessif"] = emojis_excessif
        data["logchannel"] = logchannel
        data["xplogchannel"] = xplogchannel
        file.seek(0)
        json.dump(data, file)
        file.truncate()
    # Auto-mod

    return redirect(url_for('moderation'))


@app.route("/settings_card", methods=["POST"])
def settings_card():
    xp_fond = request.form.get('background_xp')
    id = session['identifiant']
    with open(f"database/user/{id}.json", "r+") as file:
        data = json.load(file)
        data["Fond_xp"] = xp_fond
        file.seek(0)
        json.dump(data, file)
        file.truncate()
    return redirect(url_for('info_account'))


def run_discord_bot():
    discord_bot(bot, HOSTS, PORTS)


def launch_discord_bot():
    bot.run(token)


discord_thread = threading.Thread(target=launch_discord_bot)
discord_thread2 = threading.Thread(target=run_discord_bot)
if __name__ == "__main__":
    discord_thread.start()
    discord_thread2.start()
    app.run(port=PORTS, host=HOSTS)
