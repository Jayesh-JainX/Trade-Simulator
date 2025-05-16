import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import useWebSocket from 'react-use-websocket';
import InputPanel from './components/InputPanel';
import OutputPanel from './components/OutputPanel';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
});

function App() {
  const [marketData, setMarketData] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [inputParams, setInputParams] = useState({
    exchange: 'OKX',
    spotAsset: 'BTC-USDT',
    orderType: 'market',
    quantity: 100,
    volatility: 0.02,
    feeTier: 'Tier1'
  });

  const { lastJsonMessage } = useWebSocket(
    'wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP',
    {
      onOpen: () => console.log('WebSocket Connected'),
      onError: (error) => console.error('WebSocket Error:', error),
      shouldReconnect: () => true,
      reconnectInterval: 3000,
      share: true,
    }
  );

  // Market metrics calculation (Almgren-Chriss inspired model)
  const calculateMarketMetrics = (orderbook, params) => {
    const midPrices = orderbook.bids.map(([price]) => parseFloat(price))
      .concat(orderbook.asks.map(([price]) => parseFloat(price)));

    const volatility = Math.sqrt(
      midPrices.reduce((acc, price) => {
        const diff = price - midPrices[0];
        return acc + diff * diff;
      }, 0) / midPrices.length
    );

    const liquidity = orderbook.bids.reduce((acc, [_, size]) => acc + parseFloat(size), 0) +
      orderbook.asks.reduce((acc, [_, size]) => acc + parseFloat(size), 0);

    const slippage = Math.min(0.01, (params.quantity / liquidity) * volatility);

    const feeRates = {
      'Tier1': 0.001,
      'Tier2': 0.0008,
      'Tier3': 0.0006
    };
    const fees = params.quantity * (feeRates[params.feeTier] || 0.001);

    const gamma = 0.1;
    const eta = 0.2;
    const marketImpact = (gamma * params.quantity / liquidity) +
      (eta * volatility * Math.sqrt(params.quantity / liquidity));

    return { slippage, fees, marketImpact, volatility, liquidity };
  };

  useEffect(() => {
    if (lastJsonMessage) {
      const startTime = performance.now();

      const newMarketData = {
        best_bid: lastJsonMessage.bids[0][0],
        best_ask: lastJsonMessage.asks[0][0],
        spread: (parseFloat(lastJsonMessage.asks[0][0]) - parseFloat(lastJsonMessage.bids[0][0])).toString(),
        volume: lastJsonMessage.bids.reduce((acc, [_, size]) => acc + parseFloat(size), 0)
      };

      const metrics = calculateMarketMetrics(lastJsonMessage, inputParams);
      const endTime = performance.now();

      const newAnalysis = {
        slippage: metrics.slippage,
        fees: metrics.fees,
        market_impact: metrics.marketImpact,
        net_cost: parseFloat(inputParams.quantity) * (1 + metrics.slippage + metrics.marketImpact) + metrics.fees,
        maker_taker_ratio: Math.max(0.5, Math.min(0.9, 1 - metrics.marketImpact)),
        latency: (endTime - startTime) / 1000
      };

      setMarketData(newMarketData);
      setAnalysis(newAnalysis);
    }
  }, [lastJsonMessage, inputParams]);

  const handleInputChange = (newParams) => {
    setInputParams(newParams);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          {/* Left Panel - Input Parameters */}
          <Grid item xs={12} md={6}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                height: 'calc(130vh - 100px)',
              }}
            >
              <InputPanel 
                params={inputParams} 
                onParamsChange={handleInputChange} 
              />
            </Paper>
          </Grid>

          {/* Right Panel - Output Values */}
          <Grid item xs={12} md={6}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                height: 'calc(130vh - 100px)',
              }}
            >
              <OutputPanel 
                marketData={marketData}
                analysis={analysis}
              />
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </ThemeProvider>
  );
}

export default App;
