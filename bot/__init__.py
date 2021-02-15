import logging
import os
import threading
import time

import aria2p
import telegram.ext as tg
import socket
import faulthandler
from pyrogram import Client
from telegraph import Telegraph
from bot.helper.config import dynamic

faulthandler.enable()

socket.setdefaulttimeout(600)

botStartTime = time.time()
if os.path.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()],
                    level=logging.INFO)

dynamic.handler()

Interval = []


LOGGER = logging.getLogger(__name__)

try:
    if bool(os.environ['_____REMOVE_THIS_LINE_____']):
        logging.error('The README.md file there to be read! Exiting now!')
        exit()
except KeyError:
    pass

aria2 = aria2p.API(aria2p.Client(host="http://localhost", port=6800, secret=""))

DOWNLOAD_DIR = None
BOT_TOKEN = None
TELEGRAM_API = None
TELEGRAM_HASH = None

download_dict_lock = threading.Lock()
status_reply_dict_lock = threading.Lock()
# Key: update.effective_chat.id
# Value: telegram.Message
status_reply_dict = {}
# Key: update.message.message_id
# Value: An object of Status
download_dict = {}
# Stores list of users and chats the bot is authorized to use in
AUTHORIZED_CHATS = set()
if os.path.exists('authorized_chats.txt'):
    with open('authorized_chats.txt', 'r+') as f:
        lines = f.readlines()
        for line in lines:
            #    LOGGER.info(line.split())
            AUTHORIZED_CHATS.add(int(line.split()[0]))
try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    parent_id = os.environ['GDRIVE_FOLDER_ID']
    DOWNLOAD_DIR = os.environ['DOWNLOAD_DIR']
    if DOWNLOAD_DIR[-1] != '/' or DOWNLOAD_DIR[-1] != '\\':
        DOWNLOAD_DIR = DOWNLOAD_DIR + '/'
    DOWNLOAD_STATUS_UPDATE_INTERVAL = int(os.environ['DOWNLOAD_STATUS_UPDATE_INTERVAL'])
    OWNER_ID = int(os.environ['OWNER_ID'])
    AUTO_DELETE_MESSAGE_DURATION = int(os.environ['AUTO_DELETE_MESSAGE_DURATION'])
    TELEGRAM_API = os.environ['TELEGRAM_API']
    TELEGRAM_HASH = os.environ['TELEGRAM_HASH']
except KeyError as e:
    LOGGER.error("One or more env variables missing! Exiting now")
    exit(1)

# Generate USER_SESSION_STRING
LOGGER.info("Generating USER_SESSION_STRING...")
with Client(':memory:', api_id=int(TELEGRAM_API), api_hash=TELEGRAM_HASH, bot_token=BOT_TOKEN) as app:
    USER_SESSION_STRING = app.export_session_string()

# Generate TELEGRAPH_TOKEN
LOGGER.info("Generating TELEGRAPH_TOKEN...")
telegraph = Telegraph()
telegraph.create_account(short_name="tg-mirror-bot")
telegraph_token = telegraph.get_access_token()

try:
    INDEX_URL = os.environ['INDEX_URL']
    if len(INDEX_URL) == 0:
        INDEX_URL = None
except KeyError:
    INDEX_URL = None
try:
    BUTTON_THREE_NAME = os.environ['BUTTON_THREE_NAME']
    BUTTON_THREE_URL = os.environ['BUTTON_THREE_URL']
    if len(BUTTON_THREE_NAME) == 0 or len(BUTTON_THREE_URL) == 0:
        raise KeyError
except KeyError:
    BUTTON_THREE_NAME = None
    BUTTON_THREE_URL = None
try:
    BUTTON_FOUR_NAME = os.environ['BUTTON_FOUR_NAME']
    BUTTON_FOUR_URL = os.environ['BUTTON_FOUR_URL']
    if len(BUTTON_FOUR_NAME) == 0 or len(BUTTON_FOUR_URL) == 0:
        raise KeyError
except KeyError:
    BUTTON_FOUR_NAME = None
    BUTTON_FOUR_URL = None
try:
    BUTTON_FIVE_NAME = os.environ['BUTTON_FIVE_NAME']
    BUTTON_FIVE_URL = os.environ['BUTTON_FIVE_URL']
    if len(BUTTON_FIVE_NAME) == 0 or len(BUTTON_FIVE_URL) == 0:
        raise KeyError
except KeyError:
    BUTTON_FIVE_NAME = None
    BUTTON_FIVE_URL = None
try:
    STOP_DUPLICATE_MIRROR = os.environ['STOP_DUPLICATE_MIRROR']
    if STOP_DUPLICATE_MIRROR.lower() == 'true':
        STOP_DUPLICATE_MIRROR = True
    else:
        STOP_DUPLICATE_MIRROR = False
except KeyError:
    STOP_DUPLICATE_MIRROR = False
try:
    IS_TEAM_DRIVE = os.environ['IS_TEAM_DRIVE']
    if IS_TEAM_DRIVE.lower() == 'true':
        IS_TEAM_DRIVE = True
    else:
        IS_TEAM_DRIVE = False
except KeyError:
    IS_TEAM_DRIVE = False

try:
    USE_SERVICE_ACCOUNTS = os.environ['USE_SERVICE_ACCOUNTS']
    if USE_SERVICE_ACCOUNTS.lower() == 'true':
        USE_SERVICE_ACCOUNTS = True
    else:
        USE_SERVICE_ACCOUNTS = False
except KeyError:
    USE_SERVICE_ACCOUNTS = False

try:
    SHORTENER = os.environ['SHORTENER']
    SHORTENER_API = os.environ['SHORTENER_API']
    if len(SHORTENER) == 0 or len(SHORTENER_API) == 0:
        raise KeyError
except KeyError:
    SHORTENER = None
    SHORTENER_API = None

updater = tg.Updater(token=BOT_TOKEN,use_context=True)
bot = updater.bot
dispatcher = updater.dispatcher
