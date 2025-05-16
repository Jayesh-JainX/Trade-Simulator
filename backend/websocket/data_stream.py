import asyncio
import websockets
import json
import time
from datetime import datetime
from utils.logger import logger
from config.settings import OKX_WEBSOCKET_URL, TRADE_AMOUNT
import sys

class OrderBookManager:
    def __init__(self):
        self.bids = {}
        self.asks = {}
        self.processing_times = []
        print("\nInitializing OrderBook Manager...")
        logger.info("Initializing OrderBook Manager")

    def update_orderbook(self, data):
        try:
            start_time = time.perf_counter()

            # Update bids and asks
            for bid in data.get('bids', []):
                price, size = float(bid[0]), float(bid[1])
                if size == 0:
                    self.bids.pop(price, None)
                else:
                    self.bids[price] = size

            for ask in data.get('asks', []):
                price, size = float(ask[0]), float(ask[1])
                if size == 0:
                    self.asks.pop(price, None)
                else:
                    self.asks[price] = size

            # Sort orderbook
            self.bids = dict(sorted(self.bids.items(), reverse=True))
            self.asks = dict(sorted(self.asks.items()))

            # Calculate processing time
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            self.processing_times.append(processing_time)

            # Keep only last 1000 processing times
            if len(self.processing_times) > 1000:
                self.processing_times.pop(0)

            return {
                'timestamp': data.get('timestamp', datetime.utcnow().isoformat()),
                'bids': [[str(price), str(size)] for price, size in list(self.bids.items())[:10]],
                'asks': [[str(price), str(size)] for price, size in list(self.asks.items())[:10]],
                'processing_time': processing_time
            }

        except Exception as e:
            logger.error(f"Error updating orderbook: {e}")
            return None

    def get_average_latency(self):
        if not self.processing_times:
            return 0
        return sum(self.processing_times) / len(self.processing_times)

    def calculate_market_depth(self, side='bids', depth=10):
        try:
            book = self.bids if side == 'bids' else self.asks
            total_volume = sum(size for _, size in list(book.items())[:depth])
            return total_volume
        except Exception as e:
            logger.error(f"Error calculating market depth: {e}")
            return 0

async def connect_websocket():
    orderbook = OrderBookManager()
    reconnect_delay = 1
    max_retries = 10  # Increased max retries
    retry_count = 0
    last_error_time = time.time()

    while retry_count < max_retries:
        try:
            async with websockets.connect(OKX_WEBSOCKET_URL) as websocket:
                print("\nConnected to OKX WebSocket")
                logger.info("Connected to OKX WebSocket")
                reconnect_delay = 1  # Reset delay on successful connection
                retry_count = 0  # Reset retry count on successful connection

                # Subscribe to orderbook channel
                subscribe_message = {
                    "op": "subscribe",
                    "args": [{
                        "channel": "books",
                        "instId": "BTC-USDT-SWAP",
                        "instType": "SWAP"
                    }]
                }
                print("\nSubscribing to OKX orderbook...")
                await websocket.send(json.dumps(subscribe_message))

                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)

                        # Handle subscription confirmation
                        if 'event' in data:
                            print(f"\rWebSocket event: {data['event']}")
                            logger.info(f"WebSocket event: {data['event']}")
                            if data['event'] == 'error':
                                logger.error(f"WebSocket error: {data}")
                                print(f"\nWebSocket error: {data}")
                                break
                            if data['event'] == 'subscribe':
                                print("\nSuccessfully subscribed to orderbook stream")
                            continue

                        # Process orderbook data
                        if 'data' in data and data.get('data'):
                            try:
                                orderbook_data = data['data'][0] if isinstance(data['data'], list) else data['data']
                                if not isinstance(orderbook_data, dict) or 'bids' not in orderbook_data or 'asks' not in orderbook_data:
                                    logger.warning(f"Invalid orderbook data format: {orderbook_data}")
                                    continue
                                processed_data = orderbook.update_orderbook(orderbook_data)

                                if processed_data:
                                    # Calculate market depth
                                    market_depth = {
                                        'bids': orderbook.calculate_market_depth('bids'),
                                        'asks': orderbook.calculate_market_depth('asks')
                                    }
                                    processed_data['market_depth'] = market_depth
                                    processed_data['latency'] = orderbook.get_average_latency()

                                    # Print updates to console
                                    print(f"\rBest Bid: {processed_data['bids'][0][0]} | Best Ask: {processed_data['asks'][0][0]} | Depth: {market_depth['bids']:.2f}/{market_depth['asks']:.2f} | Latency: {processed_data['latency']:.5f}s", end='')
                                    sys.stdout.flush()

                                    yield processed_data
                            except Exception as e:
                                logger.error(f"Error processing orderbook data: {e}")
                                print(f"\rError processing data: {e}", end='')
                                continue

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"WebSocket error: {e}")
                        break

        except Exception as e:
            current_time = time.time()
            if current_time - last_error_time > 60:  # Reset retry count after 1 minute of successful operation
                retry_count = 0
                reconnect_delay = 1
            last_error_time = current_time
            
            logger.error(f"Connection error: {e}")
            print(f"\nConnection failed: {e}. Retrying in {reconnect_delay} seconds...")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 30)  # Reduced max delay to 30 seconds
            retry_count += 1

    print("\nFailed to establish WebSocket connection after maximum retries")
    logger.error("Failed to establish WebSocket connection after maximum retries")
    return
