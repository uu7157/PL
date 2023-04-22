import requests
from bs4 import BeautifulSoup
from pyrogram import Client
from pyrogram.types import Message
from config import Config
import time
import os
from typing import List

PASTES_FILE = 'pastes.txt'

def scrape_pastelink() -> List[str]:
    url = 'https://pastelink.net/recent'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', id='listing')
    rows = table.find_all('tr')[1:]  # skip the header row
    scraped_urls = set()
    if os.path.exists(PASTES_FILE):
        with open(PASTES_FILE, 'r') as f:
            scraped_urls = set(f.read().splitlines())
    messages = []
    for row in rows:
        cols = row.find_all('td')
        paste_url = cols[0].find('a')['href']
        paste_age = cols[1].text.strip()
        paste_views = cols[2].text.strip()
        paste_title = cols[0].text.strip()
        paste_url = f'https://pastelink.net{paste_url}'
        if paste_url in scraped_urls:
            continue
        paste_response = requests.get(paste_url)
        paste_soup = BeautifulSoup(paste_response.content, 'html.parser')
        paste_body = paste_soup.find('div', id='body-display').text.strip()
        message = f'<b>{paste_title}</b> ({paste_views} views, {paste_age})\n{paste_url}\n\n{paste_body}\n\n'
        messages.append(message)
        scraped_urls.add(paste_url)
        time.sleep(1)
    with open(PASTES_FILE, 'w') as f:
        f.write('\n'.join(scraped_urls))
    return messages

def send_to_telegram(client: Client, message: Message):
    messages = scrape_pastelink()
    for message in messages:
        client.send_message(chat_id=Config.CHANNEL_ID, text=message, parse_mode='HTML')
        time.sleep(4)

if __name__ == '__main__':
    client = Client(
        'my_session',
        api_id=Config.BOT_API_ID,
        api_hash=Config.BOT_API_HASH,
        bot_token=Config.BOT_TOKEN
    )

    with client:
        while True:
            send_to_telegram(client, None)
            time.sleep(14400)
