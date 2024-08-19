import ta
import math
from bot import TelegramBot
from datetime import datetime, timedelta
import pandas as pd

class AlgorithmFixedPrices:
    def __init__(self):
        self.bot = TelegramBot()
        self.data = []
        self.counter = 0  # Counter to track onNewData calls
        self.last_message_time = None  # Track the last message sent time

    async def onNewData(self, new_data):
        self.counter += 1
        data = new_data[0]
        if data['symbol'] != 'WSTUSDT_USDT':
            return

        # Append new data to the list and Convert the data to a DataFrame
        self.data.append(data)
        df = pd.DataFrame(self.data)
        if len(df) < 10:
            return

        # Ensure required columns exist
        if 'close' not in df.columns or 'high' not in df.columns or 'low' not in df.columns:
            return

        # Calculate SMA, high, and low
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)

        # Compute SMA
        df['sma10'] = ta.trend.sma_indicator(df['close'], window=10)
        sma10 = df['sma10'].iloc[-1]
        high = df['high'].iloc[-1]
        low = df['low'].iloc[-1]
        close = df['close'].iloc[-1]

        # Calculate percentage range and adjusted prices
        percentage_range_sma10 = ((high - low) / sma10) / 2
        percentage_range_sma10_rounded = round(percentage_range_sma10, 2)
        one_plus_percentage_range_sma10_rounded = 1.0 + percentage_range_sma10_rounded
        one_minus_percentage_range_sma10_rounded = 1.0 - percentage_range_sma10_rounded

        buy_price = sma10 * one_minus_percentage_range_sma10_rounded
        sell_price = sma10 * one_plus_percentage_range_sma10_rounded

        # Check cooldown (5 minutes)
        now = datetime.now()
        if self.last_message_time and now - self.last_message_time < timedelta(minutes=5):
            return  # Do not send message if within cooldown period

        # Algorithm logic
        if close >= sell_price:
            msg = f'Sell Alert!! WST-USDT -->\nclose_price: {close}\nbuy_price= {buy_price}\nsell_price= {sell_price}\nCreate a new buy position with buy price....'
            await self.bot.send_message(msg)
            self.last_message_time = now  # Update last message time
        elif close <= buy_price:
            msg = f'Buy Alert!! WST-USDT -->\nclose_price: {close}\nbuy_price= {buy_price}\nsell_price= {sell_price}\nCreat a new sell position with sell price...'
            await self.bot.send_message(msg)
            self.last_message_time = now  # Update last message time

        # Add timestamp to the message
        timestamp = now.strftime('%d-%m-%Y %H:%M:%S')
        true_percentage = percentage_range_sma10 * 2.0
        msg = f'{timestamp} - WST-USDT :: close price= {close}, buy_price= {round(buy_price, 2)}, sell_price={round(sell_price, 2)}, percentage={round(true_percentage, 2)}'

        # Print the message every 20 calls to onNewData
        if self.counter % 20 == 0:
            self.counter = 0
            print(msg)
