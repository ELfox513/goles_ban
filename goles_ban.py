import discord
import os
import logging
import logging.handlers

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(filename='goles_ban.log', encoding='utf-8', maxBytes=32 * 1024 * 1024)
handler.setFormatter(logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{'))
logger.addHandler(handler)

class MyClient(discord.Client):
    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message):

        # Use commands
        if message.author.guild_permissions.manage_guild and message.content.startswith('?goles') and len(message.content.split()) >= 2:
            str_command = message.content.split()[1]
            str_command_args = message.content.split()[2:] if len(message.content.split()) > 2 else ['<NONE>']
            
            if str_command == 'help':
                
                
                


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(os.getenv('TOKEN'), log_handler=None)