# Trade Simulator

A high-performance trade simulator leveraging real-time market data to estimate transaction costs and market impact. The system connects to WebSocket endpoints that stream full L2 orderbook data for cryptocurrency exchanges, providing accurate simulation of market dynamics and trade execution.

## System Architecture

### Frontend (React + Material-UI)
- Real-time data visualization with WebGL-accelerated charts
- Interactive parameter configuration with type-safe validation
- Responsive design with dark mode support and accessibility features
- WebSocket integration for live market data with automatic reconnection
- Efficient state management using React Context and hooks
- Optimized rendering with React.memo and useMemo

### Backend (Python)
- Asynchronous WebSocket server using FastAPI
- High-performance market impact modeling
- Transaction cost analysis with ML-enhanced predictions
- Performance optimization using NumPy vectorization
- Comprehensive logging and monitoring
- Efficient data compression and caching strategies

## Model Implementation

### Market Impact Model (Almgren-Chriss)

The implementation uses the Almgren-Chriss model for market impact calculation:

- **Temporary Impact**: Linear in trade size
- **Permanent Impact**: Square root of trade size
- **Key Parameters**:
  - γ (gamma): Controls linear price impact
  - η (eta): Controls non-linear price impact
  - σ (sigma): Market volatility

Formula: Impact = γ(Q/V) + η·σ·√(Q/V)
Where:
- Q: Order quantity
- V: Market volume

### Slippage Estimation

Implements advanced linear regression for slippage prediction:

- **Features**:
  - Order size relative to market depth
  - Market volatility and momentum
  - Bid-ask spread dynamics
  - Order book imbalance
  - Historical trade patterns
- **Model Selection**: Linear regression chosen for:
  - Real-time performance optimization
  - High interpretability
  - Robust outlier handling
  - Easy model updates

### Maker/Taker Prediction

Uses logistic regression with feature engineering:

- **Features**:
  - Market volatility trends
  - Order book imbalance ratios
  - Historical trade patterns
  - Time-series momentum
- **Output**: Probability distribution of order types
- **Validation**: Cross-validation with historical data

## Performance Optimization

### Data Processing
1. **Efficient Data Structures**
   - Optimized orderbook using sorted dictionaries
   - Memory-efficient market data handling
   - Circular buffers for historical data

2. **Algorithmic Optimizations**
   - Vectorized calculations with NumPy
   - Cached intermediate results
   - Minimized object creation
   - Parallel processing for heavy computations

3. **Network Optimization**
   - WebSocket connection pooling
   - Binary message serialization
   - Automatic reconnection with exponential backoff
   - Message batching and compression

### UI Performance
1. **React Optimization**
   - Memoized components with React.memo
   - Efficient state management
   - Debounced high-frequency updates
   - Virtual scrolling for large datasets

2. **Data Visualization**
   - WebGL-accelerated charts
   - Efficient data point decimation
   - Windowed data management
   - Responsive layout with CSS Grid

## Setup and Installation

### Prerequisites
- Node.js = 22.9.0
- Python = 3.11
- npm or yarn package manager

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Application Settings
```python
# config/settings.py
SERVER_PORT = 5000
MAX_CONNECTIONS = 1000
HEARTBEAT_INTERVAL = 30
```

## Performance Metrics

- Average processing time per tick: < 0.8ms
- UI update latency: < 16ms (60 FPS)
- WebSocket message handling: < 0.5ms
- Memory usage: < 750MB under full load

Detailed benchmarks available in [Performance Benchmarking](docs/PERFORMANCE_BENCHMARKING.md)

## Documentation

- [Optimization Report](docs/OPTIMIZATION_REPORT.md)
- [Performance Benchmarking](docs/PERFORMANCE_BENCHMARKING.md)
- [API Documentation](docs/API.md)

## Screenshots

![Screenshot of the app](/screenshots/screenshot-1.png)