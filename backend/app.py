from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import asyncio
import json
from websocket.data_stream import connect_websocket
from models.market_impact import calculate_market_impact
from models.regression import estimate_slippage, maker_taker_ratio
from models.latency import measure_latency
from config.settings import TRADE_AMOUNT, FEE_TIERS
from utils.logger import logger

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections: Dict[int, WebSocket] = {}

@app.get("/")
async def root():
    return {"message": "Trade Simulator API"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connection_id = id(websocket)
    active_connections[connection_id] = websocket
    
    try:
        # Initialize models
        slippage_model = estimate_slippage([], [])
        maker_taker_model = maker_taker_ratio([], [])
        historical_data = []
        
        async for data in connect_websocket():
            if connection_id not in active_connections:
                break
                
            try:
                # Process market data
                current_price = (float(data['asks'][0][0]) + float(data['bids'][0][0])) / 2
                volume = float(data['bids'][0][1])
                market_depth = data['market_depth']
                
                # Prepare features for models
                spread = float(data['asks'][0][0]) - float(data['bids'][0][0])
                features = [
                    volume,
                    spread,
                    market_depth['bids'] / (market_depth['bids'] + market_depth['asks']),
                    spread / current_price,
                    market_depth['bids'],
                    market_depth['asks']
                ]
                
                # Calculate metrics
                liquidity = market_depth['bids'] + market_depth['asks']
                volatility = 0.02  # Default value, can be calculated from historical data
                impact = calculate_market_impact(TRADE_AMOUNT, volatility, liquidity, current_price)
                slippage = slippage_model.predict([features])[0]
                maker_taker_proba = maker_taker_model.predict_proba([features])[0]
                proportion = maker_taker_proba[1]
                
                # Calculate fees
                maker_fee = FEE_TIERS['Tier1'] * 0.8
                taker_fee = FEE_TIERS['Tier1']
                fees = (proportion * maker_fee + (1 - proportion) * taker_fee) * TRADE_AMOUNT
                
                # Calculate net cost
                net_cost = slippage + fees + impact
                
                # Prepare response data
                response_data = {
                    "market_data": {
                        "best_bid": data['bids'][0][0],
                        "best_ask": data['asks'][0][0],
                        "spread": spread,
                        "volume": volume
                    },
                    "analysis": {
                        "slippage": float(slippage),
                        "fees": float(fees),
                        "market_impact": float(impact),
                        "net_cost": float(net_cost),
                        "maker_taker_ratio": float(proportion),
                        "latency": float(data.get('latency', 0.005))
                    }
                }
                
                # Send data to client
                await websocket.send_json(response_data)
                
            except Exception as e:
                logger.error(f"Error processing data: {e}")
                continue
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if connection_id in active_connections:
            del active_connections[connection_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)