import time
import pandas as pd
from binance.client import Client
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(filename='crypto_scan.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Binance API credentials (replace with your own)
api_key = "API KEY"
api_secret = "API SECRET"

# Initialize Binance client
client = Client(api_key, api_secret)

def get_usdt_pairs(max_pairs=200):
    """Fetch USDT trading pairs, excluding stablecoins and specific pairs."""
    try:
        exchange_info = client.get_exchange_info()
        stablecoins = {'USDT', 'USDC', 'TUSD', 'BUSD', 'DAI', 'PAX', 'USDP', 'GUSD', 'XUSD', 'USD1'}
        excluded_pairs = {'XUSDUSDT', 'USD1USDT'}
        usdt_pairs = [
            symbol['symbol'] for symbol in exchange_info['symbols']
            if symbol['quoteAsset'] == 'USDT' and 
               symbol['status'] == 'TRADING' and 
               symbol['baseAsset'] not in stablecoins and
               symbol['symbol'] not in excluded_pairs
        ]
        # Filter for recently listed pairs (within last 7 days)
        recent_pairs = []
        for symbol in usdt_pairs:
            try:
                klines = client.get_historical_klines(
                    symbol=symbol,
                    interval=Client.KLINE_INTERVAL_1DAY,
                    start_str='7 days ago UTC'
                )
                if klines and len(klines) < 7:  # Less than 7 days of data
                    recent_pairs.append(symbol)
            except:
                continue
        return recent_pairs[:max_pairs] if recent_pairs else usdt_pairs[:max_pairs]
    except Exception as e:
        logging.error(f"Error fetching USDT pairs: {e}")
        print(f"Error fetching USDT pairs: {e}")
        return []

def get_historical_data(symbol, start_date='2017-01-01', end_date=None):
    """Fetch historical daily kline data and check first-day pattern."""
    try:
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        klines = client.get_historical_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1DAY,
            start_str=start_date,
            end_str=end_date
        )
        if not klines:
            logging.warning(f"No historical data for {symbol}")
            return None, None, None, None
        
        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'num_trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        
        # Calculate all-time low
        all_time_low = df['low'].min()
        
        # Check first-day pattern (high on day 1, decline on day 2)
        first_day_pattern = False
        if len(df) >= 2:
            first_day = df.iloc[0]
            second_day = df.iloc[1]
            if first_day['high'] > first_day['open'] and second_day['close'] < first_day['close']:
                first_day_pattern = True
                logging.info(f"{symbol} shows first-day high pattern: Day 1 High ${first_day['high']:.8f}, Day 2 Close ${second_day['close']:.8f}")
        
        # Check for recent price increase (latest close > previous close)
        price_increase = False
        if len(df) >= 2:
            latest_close = df['close'].iloc[-1]
            previous_close = df['close'].iloc[-2]
            price_increase = latest_close > previous_close
        
        # Get 24-hour volume
        volume = df['volume'].iloc[-1] if len(df) > 0 else None
        
        return all_time_low, df, price_increase, volume
    except Exception as e:
        logging.error(f"Error fetching historical data for {symbol}: {e}")
        print(f"Error fetching historical data for {symbol}: {e}")
        return None, None, None, None

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
    # Get USDT trading pairs (prioritize recent listings)
    usdt_pairs = get_usdt_pairs(max_pairs=200)
    if not usdt_pairs:
        print("No USDT pairs found or error occurred.")
        logging.error("No USDT pairs found or error occurred.")
        return
    
    print(f"Found {len(usdt_pairs)} USDT trading pairs.")
    
    # List to store coins near all-time low with upward potential
    coins_at_low = []
    
    # Progress counter
    total_pairs = len(usdt_pairs)
    for i, symbol in enumerate(usdt_pairs, 1):
        print(f"Processing {symbol} ({i}/{total_pairs})...")
        
        # Get historical data and indicators
        all_time_low, df, price_increase, volume = get_historical_data(symbol)
        if all_time_low is None:
            continue
        
        # Get current price
        current_price = get_current_price(symbol)
        if current_price is None:
            continue
        
        # Check if current price is within 15% of all-time low
        threshold = all_time_low * 1.15
        if current_price <= threshold:
            # Check for upward potential: recent price increase
            if price_increase:
                coin = symbol.replace('USDT', '')
                coins_at_low.append({
                    'coin': coin,
                    'symbol': symbol,
                    'all_time_low': all_time_low,
                    'current_price': current_price,
                    'volume': volume,
                    'first_day_pattern': len(df) < 7  # Assume recent listing if <7 days
                })
        
        # Avoid API rate limits
        time.sleep(0.5)
    
    # Sort by proximity to all-time low and volume
    coins_at_low = sorted(
        coins_at_low,
        key=lambda x: (
            x['current_price'] / x['all_time_low'],
            -x['volume'] if x['volume'] is not None else 0
        )
    )
    
    # Output top 10 coins
    print("\nTop 10 coins near all-time low with potential to rise today (August 3, 2025):")
    if coins_at_low:
        for i, coin_data in enumerate(coins_at_low[:10], 1):
            print(f"{i}. {coin_data['coin']}")
            print(f"   Symbol: {coin_data['symbol']}")
            print(f"   All-time Low: ${coin_data['all_time_low']:.8f}")
            print(f"   Current Price: ${coin_data['current_price']:.8f}")
            print(f"   Ratio (Current/ATL): {coin_data['current_price'] / coin_data['all_time_low']:.2f}x")
            print(f"   24h Volume: {coin_data['volume']:.2f} {coin_data['coin']}")
            print(f"   Recent Price Increase: {'Yes' if coin_data['first_day_pattern'] else 'No'}")
            print(f"   First-Day Pattern: {'High then decline' if coin_data['first_day_pattern'] else 'Not observed'}")
            logging.info(f"Coin: {coin_data['coin']}, Symbol: {coin_data['symbol']}, "
                        f"ATL: ${coin_data['all_time_low']:.8f}, Current: ${coin_data['current_price']:.8f}, "
                        f"Volume: {coin_data['volume']:.2f}, "
                        f"Recent Price Increase: {'Yes' if coin_data['first_day_pattern'] else 'No'}, "
                        f"First-Day Pattern: {'High then decline' if coin_data['first_day_pattern'] else 'Not observed'}")
    else:
        print("No coins found within 15% of their all-time low with upward potential.")
        logging.info("No coins found within 15% of their all-time low with upward potential.")

if __name__ == "__main__":
    main()