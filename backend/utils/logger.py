import logging

def setup_logger():
    logger = logging.getLogger("TradeSimulator")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("trade_simulator.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger

logger = setup_logger()
