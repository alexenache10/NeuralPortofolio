import os
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DB_HOST = "localhost"
DB_PORT = "5432"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"

# It can be extended later
INITIAL_ASSETS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "asset_type": "STOCK"},
    {"symbol": "MSFT", "name": "Microsoft Corp.", "asset_type": "STOCK"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "asset_type": "STOCK"},
    {"symbol": "NVDA", "name": "NVIDIA Corp.", "asset_type": "STOCK"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "asset_type": "STOCK"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "asset_type": "STOCK"},
    {"symbol": "BTC-USD", "name": "Bitcoin USD", "asset_type": "CRYPTO"},
    {"symbol": "ETH-USD", "name": "Ethereum USD", "asset_type": "CRYPTO"},
    {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "asset_type": "ETF"},
    {"symbol": "QQQ", "name": "Invesco QQQ Trust", "asset_type": "ETF"},
    {"symbol": "GLD", "name": "SPDR Gold Shares", "asset_type": "ETF"}
]

def get_db_engine():
    return create_engine(DATABASE_URL)

def seed_assets(engine):
    print("Seeding assets table...")
    with engine.connect() as connection:
        for asset in INITIAL_ASSETS:
            query = text("""
                INSERT INTO assets (symbol, name, asset_type)
                VALUES (:symbol, :name, :asset_type)
                ON CONFLICT (symbol) DO NOTHING
                RETURNING id;
            """)
            result = connection.execute(query, asset)
            connection.commit()
            if result.rowcount > 0:
                print(f"Inserted asset: {asset['symbol']}")
            else:
                print(f"Asset already exists: {asset['symbol']}")

def fetch_and_store_market_data(engine):
    print("Fetching market data from Yahoo Finance...")
    
    with engine.connect() as connection:
        assets_result = connection.execute(text("SELECT id, symbol FROM assets"))
        assets_map = {row.symbol: row.id for row in assets_result}
    
    for symbol, asset_id in assets_map.items():
        print(f"Processing {symbol}...")
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5y")
            
            if df.empty:
                print(f"No data found for {symbol}")
                continue
            
            df.reset_index(inplace=True)
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
            
            df['asset_id'] = asset_id
            
            df['time'] = pd.to_datetime(df['time'], utc=True)
            
            df.to_sql('market_data', engine, if_exists='append', index=False, method='multi', chunksize=1000)
            print(f"Successfully loaded {len(df)} records for {symbol}")
            
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

if __name__ == "__main__":
    engine = get_db_engine()
    seed_assets(engine)
    fetch_and_store_market_data(engine)
    print("Data ingestion pipeline completed.")