import telegram
import asyncio

# Define your credentials and message
API_KEY = ''
CHAT_ID_MOHSEN = ''
CHAT_ID_SANAZ = ''
CHAT_IDS = [CHAT_ID_MOHSEN, CHAT_ID_SANAZ]

# Ensure compatibility with Windows event loop policy
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class TelegramBot:
    def __init__(self):
        self.bot = telegram.Bot(token=API_KEY)
        asyncio.create_task(self.send_message('Bot is re-initialized....'))

    async def send_message(self, message):
        for chat_id in CHAT_IDS:
            await self.bot.send_message(chat_id=chat_id, text=message)
            print(f"Message sent to {chat_id}")


# Create an instance of the TelegramBot class
#bot = TelegramBot(API_KEY, CHAT_IDS)
