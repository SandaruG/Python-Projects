import time
import pandas as pd
from binance.client import Client
from datetime import datetime
import logging

# Configure logging to save errors to a file
logging.basicConfig(filename='crypto_scan.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Binance API credentials (replace with your own)
api_key = "API KEY"
api_secret = "API SECRET"

# Initialize Binance client
client = Client(api_key, api_secret)

def get_usdt_pairs(max_pairs=450):
    """Fetch all trading pairs with USDT as the quote currency, excluding stablecoins."""
    try:
        exchange_info = client.get_exchange_info()
        # Exclude stablecoin base assets
        stablecoins = {'USDT', 'USDC', 'TUSD', 'BUSD', 'DAI', 'PAX', 'USDP', 'GUSD'}
        usdt_pairs = [
            symbol['symbol'] for symbol in exchange_info['symbols']
            if symbol['quoteAsset'] == 'USDT' and 
               symbol['status'] == 'TRADING' and 
               symbol['baseAsset'] not in stablecoins
        ]
        return usdt_pairs[:max_pairs]  # Limit to max_pairs
    except Exception as e:
        logging.error(f"Error fetching USDT pairs: {e}")
        print(f"Error fetching USDT pairs: {e}")
        return []

def get_historical_low(symbol, start_date='2017-01-01', end_date=None):
    """Fetch historical daily kline data and find the all-time low price."""
    try:
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        # Fetch historical klines (daily)
        klines = client.get_historical_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1DAY,
            start_str=start_date,
            end_str=end_date
        )
        if not klines:
            logging.warning(f"No historical data for {symbol}")
            return None, None
        
        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'num_trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        # Convert price columns to float
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        
        # Find all-time low
        all_time_low = df['low'].min()
        return all_time_low, df
    except Exception as e:
        logging.error(f"Error fetching historical data for {symbol}: {e}")
        print(f"Error fetching historical data for {symbol}: {e}")
        return None, None

def get_current_price(symbol):
    """Fetch the current price of a trading pair."""
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except Exception as e:
        logging.error(f"Error fetching current price for {symbol}: {e}")
        print(f"Error fetching current price for {symbol}: {e}")
        return None

def main():
    # Get all USDT trading pairs (limited to 450 for testing)
    usdt_pairs = get_usdt_pairs(max_pairs=450)
    if not usdt_pairs:
        print("No USDT pairs found or error occurred.")
        logging.error("No USDT pairs found or error occurred.")
        return
    
    print(f"Found {len(usdt_pairs)} USDT trading pairs.")
    
    # List to store coins at or near all-time low
    coins_at_low = []
    
    # Progress counter
    total_pairs = len(usdt_pairs)
    for i, symbol in enumerate(usdt_pairs, 1):
        print(f"Processing {symbol} ({i}/{total_pairs})...")
        
        # Get historical low and data
        all_time_low, df = get_historical_low(symbol)
        if all_time_low is None:
            continue
        
        # Get current price
        current_price = get_current_price(symbol)
        if current_price is None:
            continue
        
        # Check if current price is within 5% of all-time low
        threshold = all_time_low * 1.05  # 5% above all-time low
        if current_price <= threshold:
            coin = symbol.replace('USDT', '')  # Extract coin name (e.g., BTC from BTCUSDT)
            coins_at_low.append({
                'coin': coin,
                'symbol': symbol,
                'all_time_low': all_time_low,
                'current_price': current_price
            })
        
        # Avoid API rate limits
        time.sleep(0.5)  # 0.5s delay to avoid rate limits
    
    # Sort by how close current price is to all-time low
    coins_at_low = sorted(coins_at_low, key=lambda x: x['current_price'] / x['all_time_low'])
    
    # Output up to 3 coins
    print("\nCoins at or near all-time low (within 5%):")
    if coins_at_low:
        for i, coin_data in enumerate(coins_at_low[:3], 1):
            print(f"{i}. {coin_data['coin']}")
            print(f"   Symbol: {coin_data['symbol']}")
            print(f"   All-time Low: ${coin_data['all_time_low']:.8f}")
            print(f"   Current Price: ${coin_data['current_price']:.8f}")
            print(f"   Ratio (Current/ATL): {coin_data['current_price'] / coin_data['all_time_low']:.2f}x")
            logging.info(f"Coin at all-time low: {coin_data['coin']}, Symbol: {coin_data['symbol']}, "
                        f"ATL: ${coin_data['all_time_low']:.8f}, Current: ${coin_data['current_price']:.8f}")
    else:
        print("No coins found within 5% of their all-time low.")
        logging.info("No coins found within 5% of their all-time low.")

if __name__ == "__main__":
    main()