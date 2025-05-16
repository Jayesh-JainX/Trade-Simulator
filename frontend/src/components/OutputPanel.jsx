import React from 'react';
import { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import { styled } from '@mui/material/styles';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import Tooltip from '@mui/material/Tooltip';
import InfoIcon from '@mui/icons-material/Info';
import IconButton from '@mui/material/IconButton';
import CircularProgress from '@mui/material/CircularProgress';

const MetricCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  textAlign: 'center',
  color: theme.palette.text.secondary,
  background: theme.palette.background.paper,
  height: '100%',
  position: 'relative',
  '&:hover': {
    boxShadow: theme.shadows[4],
    transform: 'translateY(-2px)',
    transition: 'all 0.3s'
  }
}));

const InfoIconStyled = styled(InfoIcon)(({ theme }) => ({
  fontSize: '1rem',
  marginLeft: theme.spacing(0.5),
  color: theme.palette.text.secondary,
}));

const MetricHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: theme.spacing(1)
}));

const MetricValue = styled(Typography)(({ theme }) => ({
  fontSize: '1.5rem',
  fontWeight: 'bold',
  color: theme.palette.primary.main,
  marginTop: theme.spacing(1),
}));

const OutputPanel = ({ marketData, analysis }) => {
  const [chartData, setChartData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const tooltips = {
    bestBid: 'The highest price a buyer is willing to pay',
    bestAsk: 'The lowest price a seller is willing to accept',
    spread: 'The difference between best ask and best bid prices',
    volume: 'Total trading volume in the order book',
    slippage: 'Expected price difference due to order size and market depth',
    fees: 'Transaction fees based on selected fee tier',
    marketImpact: 'Price impact calculated using Almgren-Chriss model',
    netCost: 'Total transaction cost including fees, slippage, and market impact',
    makerTaker: 'Proportion of maker orders vs taker orders',
    latency: 'Internal processing time per market tick'
  };

  useEffect(() => {
    if (marketData && analysis) {
      setIsLoading(false);
      setChartData(prevData => {
        const newData = [...prevData, {
          time: new Date().toLocaleTimeString(),
          netCost: analysis.net_cost,
          slippage: analysis.slippage,
          impact: analysis.market_impact,
          timestamp: Date.now()
        }];
        // Keep last 50 data points
        return newData.slice(-50);
      });
    }
  }, [marketData, analysis]);

  const MetricCardWithTooltip = ({ title, value, tooltip }) => (
    <MetricCard>
      <MetricHeader>
        <Typography variant="body2">{title}</Typography>
        <Tooltip 
          title={tooltip} 
          arrow 
          placement="top"
          enterTouchDelay={0}
          leaveTouchDelay={1500}
        >
          <IconButton size="small" sx={{ ml: 0.5 }}>
            <InfoIconStyled />
          </IconButton>
        </Tooltip>
      </MetricHeader>
      <MetricValue>{value}</MetricValue>
    </MetricCard>
  );

  if (isLoading || !marketData || !analysis) {
    return (
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Connecting to market data...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Market Analysis
      </Typography>

      <Grid container spacing={2} sx={{ mb: 4 }}>
        {/* Market Data Section */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            Market Data
          </Typography>
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCardWithTooltip
            title="Best Bid"
            value={parseFloat(marketData.best_bid).toFixed(2)}
            tooltip={tooltips.bestBid}
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCardWithTooltip
            title="Best Ask"
            value={parseFloat(marketData.best_ask).toFixed(2)}
            tooltip={tooltips.bestAsk}
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCardWithTooltip
            title="Spread"
            value={parseFloat(marketData.spread).toFixed(4)}
            tooltip={tooltips.spread}
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCardWithTooltip
            title="Volume"
            value={parseFloat(marketData.volume).toFixed(2)}
            tooltip={tooltips.volume}
          />
        </Grid>

        {/* Analysis Section */}
        <Grid item xs={12} sx={{ mt: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            Cost Analysis
          </Typography>
        </Grid>
        <Grid item xs={6} md={4}>
          <MetricCardWithTooltip
            title="Expected Slippage"
            value={`${(analysis.slippage * 100).toFixed(4)}%`}
            tooltip={tooltips.slippage}
          />
        </Grid>
        <Grid item xs={6} md={4}>
          <MetricCardWithTooltip
            title="Expected Fees"
            value={`$${analysis.fees.toFixed(2)}`}
            tooltip={tooltips.fees}
          />
        </Grid>
        <Grid item xs={6} md={4}>
          <MetricCardWithTooltip
            title="Market Impact"
            value={`${(analysis.market_impact * 100).toFixed(4)}%`}
            tooltip={tooltips.marketImpact}
          />
        </Grid>
        <Grid item xs={6} md={4}>
          <MetricCardWithTooltip
            title="Net Cost"
            value={`$${analysis.net_cost.toFixed(2)}`}
            tooltip={tooltips.netCost}
          />
        </Grid>
        <Grid item xs={6} md={4}>
          <MetricCardWithTooltip
            title="Maker/Taker Ratio"
            value={`${(analysis.maker_taker_ratio * 100).toFixed(1)}%`}
            tooltip={tooltips.makerTaker}
          />
        </Grid>
        <Grid item xs={6} md={4}>
          <MetricCardWithTooltip
            title="Internal Latency"
            value={`${(analysis.latency * 1000).toFixed(2)}ms`}
            tooltip={tooltips.latency}
          />
        </Grid>
      </Grid>

      {/* Chart Section */}
      <Box sx={{ height: 300, mt: 4 }}>
        <Typography variant="subtitle1" gutterBottom>
          Cost Metrics Over Time
        </Typography>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `$${value.toFixed(2)}`}
            />
            <Tooltip
              contentStyle={{ background: '#1e1e1e', border: '1px solid #333' }}
              labelStyle={{ color: '#fff' }}
              formatter={(value) => [`$${value.toFixed(4)}`, null]}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="netCost" 
              name="Net Cost" 
              stroke="#8884d8"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6 }}
            />
            <Line 
              type="monotone" 
              dataKey="slippage" 
              name="Slippage" 
              stroke="#82ca9d"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6 }}
            />
            <Line 
              type="monotone" 
              dataKey="impact" 
              name="Market Impact" 
              stroke="#ffc658"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};

export default OutputPanel;