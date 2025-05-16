import re
import json
import asyncio
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.types import Message


api_id = 'your api id'
api_hash = 'your api hash'
channel_username = 'toronionlinks' 

output_file = 'onion_links.json'
last_id_file = 'last_id.txt'

onion_regex = r'(http[s]?://)?[a-z2-7]{16,56}\.onion\b'

def load_last_id():
    try:
        with open(last_id_file, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def save_last_id(last_id):
    with open(last_id_file, 'w') as f:
        f.write(str(last_id))

def extract_onion_links(text):
    return re.findall(onion_regex, text, re.IGNORECASE)

async def main():
    client = TelegramClient('anon', api_id, api_hash)
    await client.start()

    last_id = load_last_id()
    latest_id = last_id

    try:
        async for message in client.iter_messages(channel_username, min_id=last_id):
            if isinstance(message, Message) and message.text:
                text = message.text
                links = extract_onion_links(text)

                for link in links:
                    if not link.startswith("http"):
                        link = "http://" + link

                    data = {
                        "source": "telegram",
                        "url": link,
                        "discovered_at": datetime.utcnow().isoformat() + "Z",
                        "context": f"Found in Telegram channel @{channel_username}",
                        "status": "pending"
                    }
                    with open(output_file, 'a') as f:
                        f.write(json.dumps(data) + "\n")

                if message.id > latest_id:
                    latest_id = message.id

        save_last_id(latest_id)

    except Exception as e:
        print("Error occurred:", str(e))

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
