import discord
from io import BytesIO
import asyncio
import base64
import requests
import json
from PIL import Image, ImageDraw, ImageFont


def kick_user(bot, id, id_serveur):
    user_id = id
    guild_id = id_serveur
    guild = bot.get_guild(int(guild_id))
    user = discord.Object(id=user_id)
    asyncio.run_coroutine_threadsafe(guild.kick(user, reason="c'est un test2 expulsé"), bot.loop)
    print('utilisateur expulsé')


def ban_user(bot, id, id_serveur):
    user_id = id
    guild_id = id_serveur
    guild = bot.get_guild(int(guild_id))
    user = discord.Object(id=user_id)
    asyncio.run_coroutine_threadsafe(guild.ban(user, reason="c'est un test2 banni"), bot.loop)
    print('utilisateur banni')


def list_salon_in_server(bot, id_serveur):
    # Récupération de l'objet serveur correspondant à l'ID du serveur
    server = bot.get_guild(int(id_serveur))
    # Parcours de tous les salons du serveur
    for channel in server.channels:
        # Vérification que le salon est un salon texte et pas vocal ou autre
        if isinstance(channel, discord.TextChannel):
            id_serveur = channel.id
            name_serveur = channel.name
            print(id_serveur, name_serveur)


def member_permission(bot, id, id_serveur):
    user_id = id
    guild_id = id_serveur
    guild = bot.get_guild(int(guild_id))
    member = guild.get_member(int(user_id))
    role = discord.utils.get(member.guild.roles, name='membre')
    print(role)
    if role is None:
        print('the user as not a role member')
    if member is None:
        print(f"L'utilisateur avec l'ID {user_id} n'est pas sur ce serveur Discord.")
    elif member.guild_permissions.manage_guild:
        print(f"L'utilisateur avec l'ID {user_id} est fondateur.")
    elif member.guild_permissions.administrator:
        print(f"L'utilisateur avec l'ID {user_id} est administrateur.")


def count_member(id_serveur, bot):
    guild_id = id_serveur
    guild = bot.get_guild(int(guild_id))
    member_count = guild.member_count
    return member_count


def settings_xp_card(bot, id, id_serveur, avatars_image, username, niveau, experience, SEUIL_EXPERIENCE_NIVEAU):
    user_id = id
    guild_id = id_serveur

    with open(f"./database/user/{user_id}.json") as file:
        data = json.load(file)
        bg = data['Fond_xp']

    response_icon = requests.get(avatars_image)
    image_bytes = BytesIO(response_icon.content)

    guild = bot.get_guild(int(guild_id))
    member = guild.get_member(int(user_id))

    # génération de la carte

    backgrounds = Image.open(f"./modules/sassets/{bg}").convert("RGBA")
    profiles = Image.open(image_bytes).convert("RGBA")
    new_size = (867, 290)
    background = backgrounds.resize(new_size)

    mask = Image.new("L", profiles.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + profiles.size, fill=255)
    profiles.putalpha(mask)

    profiles_rezise = profiles.resize((150, 150))

    xp = Image.new("RGBA", (650, 40), (255, 255, 255, 255))
    mask = Image.new("L", xp.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, xp.width, xp.height), radius=20, fill="white")
    xp.putalpha(mask)
    Pourcentage = (experience / SEUIL_EXPERIENCE_NIVEAU)*650
    pink_box_width = Pourcentage
    pink_box_height = 40
    draw = ImageDraw.Draw(xp)
    draw.rounded_rectangle((0, 0, pink_box_width, pink_box_height), radius=20, fill=(255, 187, 92), outline=None,
                           width=0)

    bar = Image.new("RGBA", (375, 3), (255, 255, 255, 255))
    mask = Image.new("L", bar.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, bar.width, bar.height), radius=20, fill="white")
    bar.putalpha(mask)

    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("./modules/sassets/16020_FUTURAM.ttf", size=40)
    font_xp = ImageFont.truetype("./modules/sassets/16020_FUTURAM.ttf", size=30)
    draw.text((280, 170), username, font=font, fill=(255, 187, 92))
    draw.text((580, 15), f"Level : {niveau} : {experience}/{SEUIL_EXPERIENCE_NIVEAU}xp", font=font_xp, fill=(255, 187, 92))

    # Coller la carte de xp sur l'image de fond
    background.alpha_composite(profiles_rezise, (15, 35))
    background.alpha_composite(xp, (15, 220))
    background.alpha_composite(bar, (510, 50))

    buffer = BytesIO()
    background.save(buffer, format="PNG")
    buffer.seek(0)
    data_uri = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return data_uri


def xp_card(id, avatars_image, username, niveau, experience, SEUIL_EXPERIENCE_NIVEAU):

    user_id = id

    with open(f"./database/user/{user_id}.json") as file:
        data = json.load(file)
        bg = data['Fond_xp']

    response_icon = requests.get(f'{avatars_image}')
    image_bytes = BytesIO(response_icon.content)

    # génération de la carte

    backgrounds = Image.open(f"./modules/sassets/{bg}").convert("RGBA")
    profiles = Image.open(image_bytes).convert("RGBA")
    background = backgrounds.resize((867, 290))

    mask = Image.new("L", profiles.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + profiles.size, fill=255)
    profiles.putalpha(mask)

    profiles_rezise = profiles.resize((150, 150))

    xp = Image.new("RGBA", (650, 40), (255, 255, 255, 255))
    mask = Image.new("L", xp.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, xp.width, xp.height), radius=20, fill="white")
    xp.putalpha(mask)
    Pourcentage = (experience / SEUIL_EXPERIENCE_NIVEAU) * 650
    pink_box_width = Pourcentage
    pink_box_height = 40
    draw = ImageDraw.Draw(xp)
    draw.rounded_rectangle((0, 0, pink_box_width, pink_box_height), radius=20, fill=(255, 187, 92), outline=None,
                           width=0)

    bar = Image.new("RGBA", (375, 3), (255, 255, 255, 255))
    mask = Image.new("L", bar.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, bar.width, bar.height), radius=20, fill="white")
    bar.putalpha(mask)

    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("./modules/sassets/16020_FUTURAM.ttf", size=40)
    font_xp = ImageFont.truetype("./modules/sassets/16020_FUTURAM.ttf", size=30)
    draw.text((365, 170), username, font=font, fill=(255, 187, 92))
    draw.text((580, 15), f"Level : {niveau} : {experience}/{SEUIL_EXPERIENCE_NIVEAU}xp", font=font_xp, fill=(255, 187, 92))

    # Coller la carte de xp sur l'image de fond
    background.alpha_composite(profiles_rezise, (15, 35))
    background.alpha_composite(xp, (15, 220))
    background.alpha_composite(bar, (510, 50))

    buffer = BytesIO()
    background.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
