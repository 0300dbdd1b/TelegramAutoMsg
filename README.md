
# TelegramAutoPub

TelegramAutoPub is a Telegram automation bot designed to manage group and channel interactions such as publishing messages, joining new groups or channels, and listing the existing ones associated with your Telegram account.

## Requirements

-   Python 3
-   Telethon: A Python library for interacting with Telegram's API

To install these dependencies, run:


    python3 -m pip install telethon

## Setup

### Configuration Files

Before you start the bot, you need to set up the following configuration files in the `config` directory:

1.  **config.json:** 
    
{
	"app_title": "TelegramAutoPub",
	"api_id": 123456,
	"api_hash":"YOUR_API_HASH",
	"phone": "+1111111111111",
	"messages_path": "./config/messages.txt",
	"groups_path": "./config/groups.txt",
	"channels_path": "./config/channel.txt",
	"forward_header": 0
	}

    
 You can obtain your API ID and API hash from [Telegram's developer portal](https://my.telegram.org/).
    
2.  **channels.txt and groups.txt:** These files will be automatically populated with the channel and group IDs that your account is part of. Initially, they can be empty.
    
3.  **message.txt:** This file should contain the message links you want to forward.

### Launch the Bot

Run the bot using the following command:

`python3 ./TelegramAutoPub.py` 

## How to Use

Once the bot is running, you can use the following commands in the console:

-   **.groups:** Retrieves and saves all the groups associated with your Telegram account to `config/groups.txt`.
    
-   **.channels:** Retrieves and saves all the channels associated with your Telegram account to `config/channels.txt`.
    
-   **.pub groups <time>:** Publishes messages to all groups. Replace `<time>` with the duration each rotation takes (e.g., `2h30m` for 2 hours and 30 minutes).
    
-   **.pub channels <time>:** Publishes messages to all channels. Replace `<time>` with the duration each rotation takes.
    
-   **.reload:** Reload the config and the messages.
    
    

## Additional Commands
    
    
-   **.exit:** Exits the bot.
    
-   **.help:** Displays help information and available commands.