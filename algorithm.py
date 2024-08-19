import ta
from bot import TelegramBot
from datetime import datetime, timedelta
import pandas as pd

# Global variables for fixed buy and sell prices
FIXED_BUY_PRICE = 0.994
FIXED_SELL_PRICE = 1.04

class AlgorithmSmaRelatedPrices:
    def __init__(self):
        self.bot = TelegramBot()
        self.data = []
        self.counter = 0  # Counter to track onNewData calls
        self.last_message_time = None  # Track the last message sent time
        self.current_buy_price = None
        self.current_sell_price = None
        self.prices_calculated = False  # Flag to track if prices are calculated

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

        # Convert columns to float
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

        new_buy_price = sma10 * one_minus_percentage_range_sma10_rounded
        new_sell_price = sma10 * one_plus_percentage_range_sma10_rounded

        # Check cooldown (5 minutes)
        now = datetime.now()
        if self.last_message_time and now - self.last_message_time < timedelta(minutes=5):
            return  # Do not send message if within cooldown period

        # If it's the first time or current prices are not set, initialize them
        if self.current_buy_price is None or self.current_sell_price is None:
            self.current_buy_price = new_buy_price
            self.current_sell_price = new_sell_price
            return  # Do not send a signal on the first pass

        # Algorithm logic
        if close >= self.current_sell_price:
            msg = (f'Sell Alert!! WST-USDT -->\n'
                   f'close_price: {close}\n'
                   f'sell_price: {self.current_sell_price}\n'
                   f'new_buy_price= {new_buy_price}\n'
                   f'Create a new buy position with new buy price....')
            await self.bot.send_message(msg)
            self.last_message_time = now  # Update last message time
            # Update current prices after sending message
            self.current_buy_price = new_buy_price
            self.current_sell_price = new_sell_price
            self.prices_calculated = True  # Set flag to indicate prices have been recalculated
        elif close <= self.current_buy_price:
            msg = (f'Buy Alert!! WST-USDT -->\n'
                   f'close_price: {close}\n'
                   f'buy_price: {self.current_buy_price}\n'
                   f'new_sell_price= {new_sell_price}\n'
                   f'Create a new sell position with new sell price...')
            await self.bot.send_message(msg)
            self.last_message_time = now  # Update last message time
            # Update current prices after sending message
            self.current_buy_price = new_buy_price
            self.current_sell_price = new_sell_price
            self.prices_calculated = True  # Set flag to indicate prices have been recalculated

        # Add timestamp to the message
        timestamp = now.strftime('%d-%m-%Y %H:%M:%S')
        true_percentage = percentage_range_sma10 * 2.0
        msg = (f'{timestamp} - WST-USDT :: close price= {close}, '
               f'buy_price= {round(self.current_buy_price, 2)}, '
               f'sell_price={round(self.current_sell_price, 2)}, '
               f'percentage={round(true_percentage, 2)}')

        # Print the message every 20 calls to onNewData
        if self.counter % 20 == 0:
            self.counter = 0
            print(msg)


class AlgorithmFixedPrices:
    def __init__(self):
        self.bot = TelegramBot()
        self.counter = 0  # Counter to track onNewData calls
        self.last_message_time = None  # Track the last message sent time
        self.current_buy_price = FIXED_BUY_PRICE
        self.current_sell_price = FIXED_SELL_PRICE

    async def onNewData(self, new_data):
        self.counter += 1
        data = new_data[0]
        if data['symbol'] != 'WSTUSDT_USDT':
            return
        close = float(data['close'])
        
        # Check cooldown (5 minutes)
        now = datetime.now()
        if self.last_message_time and now - self.last_message_time < timedelta(minutes=5):
            return  # Do not send message if within cooldown period

        # Algorithm logic using fixed prices
        if close >= self.current_sell_price:
            msg = (f'Sell Alert!! WST-USDT -->\n'
                   f'close_price: {close}\n'
                   f'buy_price: {self.current_buy_price}\n'
                   f'sell_price: {self.current_sell_price}\n'
                   f'Open a buy position at buy price.')
            await self.bot.send_message(msg)
            self.last_message_time = now  # Update last message time

        elif close <= self.current_buy_price:
            msg = (f'Buy Alert!! WST-USDT -->\n'
                   f'close_price: {close}\n'
                   f'buy_price: {self.current_buy_price}\n'
                   f'sell_price: {self.current_sell_price}\n'
                   f'Open a sell position at buy price.')
            await self.bot.send_message(msg)
            self.last_message_time = now  # Update last message time

        # Add timestamp to the message
        timestamp = now.strftime('%d-%m-%Y %H:%M:%S')
        msg = (f'{timestamp} - WST-USDT :: close price= {close}, '
               f'buy_price= {self.current_buy_price}, '
               f'sell_price= {self.current_sell_price}')

        # Print the message every 20 calls to onNewData
        if self.counter % 20 == 0:
            self.counter = 0
            print(msg)
