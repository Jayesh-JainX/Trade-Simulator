# main.py

import asyncio
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from websocket.data_stream import connect_websocket
from ui.main_window import TradeSimulatorUI
from models.market_impact import calculate_market_impact
from models.regression import estimate_slippage, maker_taker_ratio
from models.latency import measure_latency
from config.settings import TRADE_AMOUNT, FEE_TIERS
from utils.logger import logger
import sys

class TradingSimulator:
    def __init__(self):
        self.slippage_model = estimate_slippage([], [])
        self.maker_taker_model = maker_taker_ratio([], [])
        self.historical_data = []
        self.start_time = None
        self.running = True
        self.batch_size = 10  # Process data in batches for better performance

    def prepare_features(self, data):
        try:
            volume = float(data['bids'][0][1])
            spread = float(data['asks'][0][0]) - float(data['bids'][0][0])
            mid_price = (float(data['asks'][0][0]) + float(data['bids'][0][0])) / 2
            market_depth = data['market_depth']
            
            features = np.array([
                volume,
                spread,
                market_depth['bids'] / (market_depth['bids'] + market_depth['asks']),
                spread / mid_price,
                market_depth['bids'],
                market_depth['asks']
            ]).reshape(1, -1)
            
            return features, volume, mid_price
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None, None, None

    async def run_simulation(self, ui):
        print("\nStarting simulation...")
        logger.info("Starting simulation")
        self.start_time = datetime.now()
        self.running = True
        data_buffer = []
        
        try:
            async for data in connect_websocket():
                if not self.running:
                    logger.info("Simulation stopped")
                    break

                try:
                    data_buffer.append(data)
                    
                    if len(data_buffer) >= self.batch_size:
                        latest_data = data_buffer[-1]
                        features, volume, current_price = self.prepare_features(latest_data)
                        
                        if features is not None:
                            # Update historical data
                            for d in data_buffer:
                                if 'bids' in d and 'asks' in d:
                                    price = (float(d['asks'][0][0]) + float(d['bids'][0][0])) / 2
                                    vol = float(d['bids'][0][1])
                                    self.historical_data.append((datetime.now(), price, vol))
                            
                            # Maintain historical data size
                            while len(self.historical_data) > 1000:
                                self.historical_data = self.historical_data[-1000:]

                            # Calculate metrics
                            prices = np.array([d[1] for d in self.historical_data[-100:]]) if len(self.historical_data) > 100 else None
                            volatility = np.std(np.diff(prices) / prices[:-1]) if prices is not None else 0.02
                            
                            liquidity = latest_data['market_depth']['bids'] + latest_data['market_depth']['asks']
                            impact = calculate_market_impact(TRADE_AMOUNT, volatility, liquidity, current_price)
                            slippage = self.slippage_model.predict(features)[0]
                            maker_taker_proba = self.maker_taker_model.predict_proba(features)[0]
                            proportion = maker_taker_proba[1]

                            # Calculate fees
                            maker_fee = FEE_TIERS['Tier1'] * 0.8
                            taker_fee = FEE_TIERS['Tier1']
                            fees = (proportion * maker_fee + (1 - proportion) * taker_fee) * TRADE_AMOUNT

                            # Final metrics
                            net_cost = slippage + fees + impact
                            latency = latest_data.get('latency', 0.005)

                            # Update UI
                            print(f"\rSlippage: {slippage:.5f} | Fees: {fees:.5f} | Impact: {impact:.5f} | Net Cost: {net_cost:.5f} | M/T Ratio: {proportion:.2f} | Latency: {latency:.5f}s", end='')
                            sys.stdout.flush()
                            
                            ui.update_output(
                                f"{slippage:.5f}",
                                f"{fees:.5f}",
                                f"{impact:.5f}",
                                f"{net_cost:.5f}",
                                f"{proportion:.2f}",
                                f"{latency:.5f}"
                            )

                            data_buffer = []
                            await asyncio.sleep(0.01)

                except Exception as e:
                    logger.error(f"Error processing data: {e}")
                    data_buffer = []
                    continue

        except Exception as e:
            logger.error(f"Simulation error: {e}")
            self.running = False

async def run_async_app(ui, simulator):
    try:
        while True:
            if ui.simulation_running:
                try:
                    await simulator.run_simulation(ui)
                except Exception as e:
                    logger.error(f"Simulation error: {e}")
                    ui.simulation_running = False
                    ui.start_button.setText("Start Simulation")
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"Async app error: {e}")
        ui.simulation_running = False
        ui.start_button.setText("Start Simulation")

def start_ui():
    app = QApplication(sys.argv)
    ui = TradeSimulatorUI()
    ui.show()
    
    # Create event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Create simulator instance
    simulator = TradingSimulator()
    ui.simulator = simulator
    
    # Run the async loop in a separate thread
    def run_async():
        loop.run_until_complete(run_async_app(ui, simulator))
    
    import threading
    async_thread = threading.Thread(target=run_async, daemon=True)
    async_thread.start()
    
    # Start Qt event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    start_ui()
