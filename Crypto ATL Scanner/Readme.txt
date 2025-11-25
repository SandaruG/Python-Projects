--------------------------------------------------------------------

Disclaimer:
This tool is for research, analysis, and educational purposes only.
It does not provide financial advice or guarantee prediction accuracy.
Use responsibly and at your own risk.

--------------------------------------------------------------------

Project Name: Binance ATL Scanner

Description:
A Python-based automated screener that analyzes Binance USDT trading pairs, identifies coins near their all-time lows (ATL), and detects potential upward movement based on historical patterns and recent market behavior.

This tool is designed for traders, analysts, and quant researchers who want to monitor newly listed or recently active coins and identify bottom-level opportunities with rising momentum.

--------------------------------------------------------------------

Features:
- Fetches all USDT trading pairs from Binance (excluding stablecoins).
- Prioritizes recent listings (less than 7 days of trading history).
- Downloads full historical kline data for each trading pair.
- Calculates:
  • All-time low (ATL)
  • First-day listing pattern
  • Recent upward price movement
  • 24H trading volume
- Detects coins within 15% of ATL that show upward recovery signs.
- Sorts results based on:
  • Proximity to ATL
  • Trading volume
- Displays Top 10 potential coins for the day.
- Includes a full logging system (crypto_scan.log).
- Binance API rate-limit friendly due to timed requests.

--------------------------------------------------------------------

Requirements:
Install required Python packages:

pip install pandas python-binance

You will need:
- Python 3.8+
- A valid Binance API Key
- A valid Binance API Secret

--------------------------------------------------------------------

Configuration:
Add your Binance API credentials inside the script:

api_key = "YOUR API KEY"
api_secret = "YOUR API SECRET"

Use a read-only API key for safety.

--------------------------------------------------------------------

How to Run:

Run the main script from terminal or command prompt:

python main.py

The script will:
1. Fetch up to 200 USDT pairs.
2. Scan their historical price data.
3. Analyze volatility, ATL proximity, and trend movement.
4. Output the top 10 coins with potential upward movement.
5. Log all scanned data and errors to crypto_scan.log.

--------------------------------------------------------------------

Example Output:

Top 10 coins near all-time low with potential to rise today:
1. XYZ
   Symbol: XYZUSDT
   All-time Low: $0.00239481
   Current Price: $0.00250000
   Ratio: 1.04x
   Volume: 1.25M XYZ
   Recent Price Increase: Yes
   First-Day Pattern: High then decline

--------------------------------------------------------------------

Logic Summary:

A coin is marked as having upward potential when:

- The current price is within 15% above the all-time low.
- Recent price candles indicate upward momentum.
- Volume is sufficiently high to indicate trader interest.
- (Optional) First-day pattern detected:
  • Day 1 high spike
  • Day 2 decline
  • Current upward recovery

This combination often signals early accumulation zones or trend reversals.

--------------------------------------------------------------------

Project Structure:

binance-atl-scanner/
│── main.py
│── README.txt
│── crypto_scan.log   (generated automatically)
└── requirements.txt

--------------------------------------------------------------------

Disclaimer:
This tool is for research, analysis, and educational purposes only.
It does not provide financial advice or guarantee prediction accuracy.
Use responsibly and at your own risk.

--------------------------------------------------------------------

Contact:
If you need expanded features such as:
- Telegram / Discord alerts
- Automated trading bot integration
- CSV export
- Real-time websocket scanning
- Optimized multi-threaded version

Just request it.
