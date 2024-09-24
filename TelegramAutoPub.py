
import json
import re
import time
import random
import asyncio
from telethon import TelegramClient, types
from telethon.tl.functions.channels import JoinChannelRequest

class Spammer:
    LOOP_DELAY = 720

    HELP_MESSAGE = '''
    HELP COMMANDS
    _____________
    .channels    | load channels and save them
    .groups      | load groups and save them
    .pub         | start the bot with a specified delay
    .reload      | reload the config
    .help        | show this message 
    .exit        | exit the program        
    '''

    @classmethod
    async def init(self, config_path):
        instance = self()
        await instance._async_init(config_path)
        return instance

    async def _async_init(self, config_path):
        self.config_path = config_path
        await self._load_config(config_path)
        print(self.config)
        self.client = TelegramClient(self.config['phone'], api_id=self.config['api_id'], api_hash=self.config['api_hash'])
        await self.client.start()
        await self._load_messages()

    async def _load_config(self, config_path):
        self.config = []
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    async def _load_groups(self):
        try:
            groups = []
            with open(self.config['groups_path'], 'r', encoding='utf8') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.split(' - ')[0].strip()
                    try:
                        entity = await self.client.get_entity(int(line))
                    except Exception as e:
                        self._logger(f"Could not load {line} : {e}")
                    groups.append(entity)
                return groups
        except:
            return []

    async def _load_channels(self):
        try:
            channels = []
            with open(self.config['groups_path'], 'r', encoding='utf8') as f:
                lines = f.readlines()
                for line in lines:
                    channels.append(line.split(' - ')[0].strip())
                return channels
        except:
            return []

    async def _get_groups(self):
        try:
            with open(self.config['groups_path'], 'a', encoding='utf8') as f:
                async for dialog in self.client.iter_dialogs():
                    if dialog.is_group:
                        link = self.construct_telegram_link(dialog)
                        f.write(f'{dialog.id} - {dialog.title} - {link}\n')
                        self._logger(f"Found Group : {dialog.id} - {dialog.title} - {link}")
            return True
        except:
            return False

    async def _get_channels(self):
        try:
            with open(self.config['channels_path'], 'a', encoding='utf8') as f:
                async for dialog in self.client.iter_dialogs():
                    if dialog.is_channel:
                        link = self.construct_telegram_link(dialog)
                        f.write(f"{dialog.id} - {dialog.title} - {link}\n")
                        self._logger(f"Found Channel : {dialog.id} - {dialog.title} - {link}")
            return True
        except Exception as e:
            print(e)
            return False

    async def _load_messages(self):
        self.channel_messages = {}
        with open(self.config['messages_path'], 'r', encoding='utf8') as f:
            lines = f.readlines()
            for line in lines:
                message_link, channel_link = line.strip().split(' - ')
                chat_id, message_id = await self._extract_from_url(message_link)
                message = await self.client.get_messages(chat_id, ids=message_id)
                
                # Extract the channel id from the channel link
                channel_id, _ = await self._extract_from_url(channel_link)
                
                # Store messages per channel in the right order
                if channel_id not in self.channel_messages:
                    self.channel_messages[channel_id] = []
                self.channel_messages[channel_id].append(message)

    async def _send_messages_to_channel(self, channel_id, messages, delay):
        """
        Send messages to a single channel with a custom delay between consecutive messages.
        """
        for message in messages:
            try:
                await self.client.send_message(channel_id, message)
                self._logger(f"Message sent to {channel_id}.")
                
                # Wait for the custom delay before sending the next message to this channel
                await asyncio.sleep(delay)
            except Exception as e:
                self._logger(f"Failed to send message to {channel_id}: {e}")
                continue

    async def _send_messages_per_channel(self, delay):
        """
        Send messages to each channel concurrently, with a custom delay for each channel.
        """
        tasks = []
        for channel_id, messages in self.channel_messages.items():
            # Create a task for each channel to send messages in order with the given delay between them
            task = asyncio.create_task(self._send_messages_to_channel(channel_id, messages, delay))
            tasks.append(task)

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

    async def _publish(self, delay):
        await self._load_messages()
        if not self.channel_messages:
            return False
        await self._send_messages_per_channel(delay)  # Send messages to each channel concurrently with a custom delay
        return True

    async def _handle_publish_command(self, command):
        parts = command.split(" ")
        if len(parts) != 3:
            print(f"Usage : .pub <groups/channels> <delay_in_seconds>")
            return
        try:
            target_type = parts[1]
            delay = int(parts[2])  # Custom delay for the messages
        except:
            print(f"Unknown command. Usage : .pub <groups/channels> <delay_in_seconds>")
            return

        if target_type == 'channels':
            entities = await self._load_channels()
        elif target_type == 'groups':
            entities = await self._load_groups()
        else:
            print(f"Unknown target type. Usage : .pub <groups/channels> <delay_in_seconds>")
            return
        
        self._logger(f"Starting the bot with a {delay}-second delay.\nSending {len(self.messages)} messages to {len(entities)} {target_type}.")
        while True:
            try:
                await self._publish(delay)
                await asyncio.sleep(self.LOOP_DELAY)
            except:
                break

    def _logger(self, command):
        print(command)

    async def run(self):
        while True:
            command = input(f">> ")
            if command == ".exit":
                break
            elif command == ".channels":
                await self._get_channels()
            elif command == ".groups":
                await self._get_groups()
            elif ".pub" in command:
                await self._handle_publish_command(command)
            elif command == ".reload":
                self._logger(f"Reloading config.")
                await self._load_config(self.config_path)
                await self._load_messages()
            elif command == ".help" or command == "help":
                print(self.HELP_MESSAGE)

    async def _extract_from_url(self, url):
        match = re.match(r'https://t\.me/(?:c/)?(\d+|[a-zA-Z0-9_]+)/(\d+)', url)
        if match:
            chat_id = match.group(1)
            message_id = int(match.group(2))
            return chat_id, message_id
        else:
            print("URL does not match the expected Telegram message pattern.")
            return None, None

    @staticmethod
    def construct_telegram_link(dialog):
        try:
            if hasattr(dialog.entity, 'username') and dialog.entity.username:
                return f'https://t.me/{dialog.entity.username}'
            else:
                # For private groups/channels without a username, use access_hash if available
                if hasattr(dialog.entity, 'access_hash'):
                    return f'https://t.me/joinchat/{dialog.entity.access_hash}'
                else:
                    return "No link available"
        except AttributeError:
            return "No link available"

async def main():
    spammer = await Spammer.init('./config/config.json')
    await spammer.run()

if __name__ == '__main__':
    asyncio.run(main())

