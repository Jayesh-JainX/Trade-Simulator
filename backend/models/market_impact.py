import numpy as np
from datetime import datetime
from utils.logger import logger

class AlmgrenChrissModel:
    def __init__(self, sigma=0.3, eta=2.0, gamma=0.15, T=1.0, N=100):
        """
        Initialize Almgren-Chriss model parameters
        :param sigma: volatility of the asset
        :param eta: temporary impact parameter
        :param gamma: permanent impact parameter
        :param T: total time horizon for execution
        :param N: number of trading intervals
        """
        self.sigma = sigma  # market volatility
        self.eta = eta      # temporary impact parameter
        self.gamma = gamma  # permanent impact parameter
        self.T = T          # time horizon
        self.N = N          # number of intervals
        self.dt = T/N       # time step size

    def calculate_optimal_trade_schedule(self, X, S0):
        """
        Calculate optimal trading trajectory
        :param X: total shares to execute
        :param S0: initial price
        :return: tuple of (trades per period, expected costs)
        """
        try:
            # Calculate tau (time scale)
            tau = self.gamma / (2.0 * self.eta)
            
            # Calculate trading trajectory
            kappa = np.sqrt(self.eta / self.gamma) * self.sigma
            alpha = np.sqrt(2.0 * self.eta * self.gamma) * np.sinh(kappa * self.T)
            
            # Calculate trading rates
            t = np.linspace(0, self.T, self.N)
            n = len(t)
            v = np.zeros(n)
            
            # Check for numerical stability
            sinh_denominator = np.sinh(kappa * self.T)
            if abs(sinh_denominator) < 1e-10:  # Avoid division by very small numbers
                logger.warning("Unstable market impact calculation, using fallback method")
                v = np.full(n, X/n)  # Uniform distribution as fallback
            else:
                for i in range(n):
                    v[i] = X * np.sinh(kappa * (self.T - t[i])) / sinh_denominator
            
            # Calculate expected implementation shortfall
            E_IS = 0.5 * self.gamma * X**2 + self.eta * np.sum(v**2) * self.dt
            
            return v, E_IS
            
        except Exception as e:
            logger.error(f"Error in optimal trade schedule calculation: {e}")
            return None, None

    def calculate_market_impact(self, volume, volatility, liquidity, current_price):
        """
        Calculate market impact using Almgren-Chriss model
        :param volume: trading volume
        :param volatility: current market volatility
        :param liquidity: market liquidity
        :param current_price: current asset price
        :return: estimated market impact
        """
        try:
            # Update model parameters based on current market conditions
            self.sigma = volatility
            
            # Calculate optimal trading schedule
            trades, expected_cost = self.calculate_optimal_trade_schedule(volume, current_price)
            
            if trades is None or expected_cost is None:
                # Fallback to simple impact model if optimal calculation fails
                logger.warning("Falling back to simple impact model")
                return self.gamma * volume + self.eta * volatility * np.sqrt(volume / liquidity)
            
            # Calculate temporary and permanent impact components
            temp_impact = self.eta * np.sum(trades**2) * self.dt
            perm_impact = self.gamma * volume
            
            total_impact = temp_impact + perm_impact
            
            # Log the impact components for analysis
            logger.info(f"Market Impact - Temporary: {temp_impact:.6f}, Permanent: {perm_impact:.6f}")
            
            return total_impact
            
        except Exception as e:
            logger.error(f"Error in market impact calculation: {e}")
            return self.gamma * volume  # Fallback to simple linear impact

# Create a global instance for use throughout the application
market_impact_model = AlmgrenChrissModel()

def calculate_market_impact(volume, volatility, liquidity, current_price=None):
    """
    Wrapper function for market impact calculation
    """
    if current_price is None:
        current_price = 1.0  # Default to 1.0 if price not provided
    
    return market_impact_model.calculate_market_impact(volume, volatility, liquidity, current_price)
