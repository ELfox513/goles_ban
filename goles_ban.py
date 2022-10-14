import discord
import os
import logging
import logging.handlers
import json

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(filename='goles_ban.log', encoding='utf-8', maxBytes=32 * 1024 * 1024)
handler.setFormatter(logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{'))
logger.addHandler(handler)

db = {}
# db[server_id][member_id][0..n] = emoji_name
try:
    with open('goles_ban.json') as infile:
        db = json.load(infile)
except:
    db = {}
logger.info(f'Loaded db: {db}')

def get_member_name(message, id):
    member = message.guild.get_member(int(id))
    return member.name + '#' + member.discriminator if member else "<NONE>"

def check_db(message, db, user_id):
    if not str(message.guild.id) in db.keys():
        db.update({str(message.guild.id) : {}})
    if not user_id in db[str(message.guild.id)].keys():
        db[str(message.guild.id)].update({user_id : []})

async def goles_ban_command(message, str_command, str_command_args, is_correct, func):
    msg = func(str_command_args, message) if is_correct else f'Error in command "{str_command}"'
    await message.reply(msg, mention_author=True)
    logger.info(msg)

def goles_ban(str_command_args, message):
    check_db(message, db, str_command_args[0])
    arr = db[str(message.guild.id)][str_command_args[0]]
    if str_command_args[1] in arr:
        return f'Emoji :{str_command_args[1]}: is already assigned to the specified user **{get_member_name(message, str_command_args[0])}**'
    else:
        arr.append(str_command_args[1])
        with open('goles_ban.json', 'w') as outfile:
            json.dump(db, outfile)
        return f'Emoji :{str_command_args[1]}: assigned to the user **{get_member_name(message, str_command_args[0])}** successfully'

def goles_pardon(str_command_args, message):
    check_db(message, db, str_command_args[0])
    arr = db[str(message.guild.id)][str_command_args[0]]
    if str_command_args[1] in arr:
        arr.remove(str_command_args[1])
        with open('goles_ban.json', 'w') as outfile:
            json.dump(db, outfile)
        return f'Emoji :{str_command_args[1]}: removed from the user **{get_member_name(message, str_command_args[0])}** successfully'
    else:
        return f'Emoji :{str_command_args[1]}: is not assigned to the specified user **{get_member_name(message, str_command_args[0])}**'

def goles_megapardon(str_command_args, message):
    check_db(message, db, str_command_args[0])
    arr = db[str(message.guild.id)][str_command_args[0]]
    if arr == []:
        return f'No emojis are assigned to the user **{get_member_name(message, str_command_args[0])}**'
    else:
        arr.clear()
        with open('goles_ban.json', 'w') as outfile:
            json.dump(db, outfile)
        return f'All emojis removed from the user **{get_member_name(message, str_command_args[0])}** successfully'

def goles_list(str_command_args, message):
    if not str(message.guild.id) in db.keys():
        db.update({str(message.guild.id) : {}})
        
    text = '<NO_DATA>'
    if db[str(message.guild.id)] != {}:
        text = ''
        for user in db[str(message.guild.id)].keys():
            text += f'{get_member_name(message, user)} ({message.author.id}) = ['
            for emoji in db[str(message.guild.id)][user]:
                text += ':'+emoji+':; '
            text += "]\n"
    return text

def goles_notfound(str_command_args, message):
    return f'Command "{str_command_args}" not found'

class MyClient(discord.Client):
    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message):
        # DM messages
        if message.author.id != self.user.id and message.guild is None:
            logger.info(f'Message received in DM by @{message.author.name}#{message.author.discriminator} ({message.author.id}). Reject!')
            await message.reply("Sorry, but this bot only works on servers", mention_author=True)
            return
        
        # Use commands
        if message.author.guild_permissions.manage_guild and message.content.startswith('?goles') and len(message.content.split()) >= 2:
            str_command = message.content.split()[1]
            str_command_args = message.content.split()[2:]
            logger.info(f'Called {str_command} with args {str_command_args} on {message.guild.name} ({message.guild.id}) by @{message.author.name}#{message.author.discriminator} ({message.author.id})')
            
            if str_command == 'ban':
                await goles_ban_command(message, str_command, str_command_args,
                                        len(str_command_args) == 2 and str_command_args[0].isdecimal() and len(str_command_args[0]) == 18 and str_command_args[1].isidentifier(), goles_ban)
            elif str_command == 'pardon':
                await goles_ban_command(message, str_command, str_command_args,
                                        len(str_command_args) == 2 and str_command_args[0].isdecimal() and len(str_command_args[0]) == 18 and str_command_args[1].isidentifier(), goles_pardon)
            elif str_command == 'megapardon':
                await goles_ban_command(message, str_command, str_command_args,
                                        len(str_command_args) == 1 and str_command_args[0].isdecimal() and len(str_command_args[0]) == 18, goles_megapardon)
            elif str_command == 'list':
                await goles_ban_command(message, str_command, str_command_args, True, goles_list)
            else:
                await goles_ban_command(message, str_command, str_command, True, goles_notfound)
                
        # Guild messages
        if str(message.guild.id) in db.keys() and str(message.author.id) in db[str(message.guild.id)].keys():
            for emoji_str in db[str(message.guild.id)][str(message.author.id)]:
                emoji = discord.utils.get(message.guild.emojis, name=emoji_str)
                if emoji:
                    await message.add_reaction(emoji)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

client = MyClient(intents=intents)
client.run(os.getenv('GOLES_BAN_TOKEN'), log_handler=None)