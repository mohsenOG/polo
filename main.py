import asyncio
from polosdk import WsClientPublic, RestClient
from algorithm import AlgorithmFixedPrices

API_KEY = ''
API_SECRET = ''

async def main():
    # Connect to REST API
    #client = RestClient(API_KEY, API_SECRET)

    # Instantiate the algorithm with the client
    algorithm = AlgorithmFixedPrices()

    async def process_message(msg):
        try:
            # Check if 'channel' key exists in msg
            if 'channel' in msg and msg['channel'] == 'candles_day_1':
                data = msg['data']
                # Call the asynchronous method
                await algorithm.onNewData(data)
        except Exception as e:
            print(f"Error processing message: {e}")

    def on_message(msg):
        # Schedule the async process_message function in the event loop
        asyncio.create_task(process_message(msg))

    def on_error(err):
        print(err)

    # Connect to the public WebSocket
    ws_client_public = WsClientPublic(on_message=on_message, on_error=on_error)
    await ws_client_public.connect()
    await ws_client_public.subscribe(['candles_day_1'], ['wstusdt_usdt'])

    # Get the timestamp from REST API
    #markets = client.get_timestamp()
    #print(markets)

    # Keep the program running indefinitely
    await asyncio.Event().wait()

# Run the main function using asyncio
asyncio.run(main())
