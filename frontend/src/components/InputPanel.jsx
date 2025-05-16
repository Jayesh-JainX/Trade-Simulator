import React from 'react';

import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import { styled } from '@mui/material/styles';

const StyledFormControl = styled(FormControl)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  width: '100%',
}));

const InputPanel = ({ params, onParamsChange }) => {
  const handleChange = (event) => {
    const { name, value } = event.target;
    onParamsChange({
      ...params,
      [name]: value
    });
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Input Parameters
      </Typography>

      <StyledFormControl>
        <InputLabel>Exchange</InputLabel>
        <Select
          name="exchange"
          value={params.exchange}
          label="Exchange"
          onChange={handleChange}
        >
          <MenuItem value="OKX">OKX</MenuItem>
        </Select>
      </StyledFormControl>

      <StyledFormControl>
        <InputLabel>Spot Asset</InputLabel>
        <Select
          name="spotAsset"
          value={params.spotAsset}
          label="Spot Asset"
          onChange={handleChange}
        >
          <MenuItem value="BTC-USDT">BTC/USDT</MenuItem>
          <MenuItem value="ETH-USDT">ETH/USDT</MenuItem>
          <MenuItem value="SOL-USDT">SOL/USDT</MenuItem>
        </Select>
      </StyledFormControl>

      <StyledFormControl>
        <InputLabel>Order Type</InputLabel>
        <Select
          name="orderType"
          value={params.orderType}
          label="Order Type"
          onChange={handleChange}
        >
          <MenuItem value="market">Market</MenuItem>
        </Select>
      </StyledFormControl>

      <StyledFormControl>
        <TextField
          name="quantity"
          label="Quantity (USD)"
          type="number"
          value={params.quantity}
          onChange={handleChange}
          InputProps={{
            inputProps: { min: 0 }
          }}
        />
      </StyledFormControl>

      <StyledFormControl>
        <TextField
          name="volatility"
          label="Volatility"
          type="number"
          value={params.volatility}
          onChange={handleChange}
          InputProps={{
            inputProps: { min: 0, step: 0.01 }
          }}
        />
      </StyledFormControl>

      <StyledFormControl>
        <InputLabel>Fee Tier</InputLabel>
        <Select
          name="feeTier"
          value={params.feeTier}
          label="Fee Tier"
          onChange={handleChange}
        >
          <MenuItem value="Tier1">Tier 1</MenuItem>
          <MenuItem value="Tier2">Tier 2</MenuItem>
          <MenuItem value="Tier3">Tier 3</MenuItem>
        </Select>
      </StyledFormControl>
    </Box>
  );
};

export default InputPanel;