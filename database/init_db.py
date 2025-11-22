import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DB_HOST = "localhost"
DB_PORT = "5432"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"

def init_db():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Successfully connected to the database.")
            
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            connection.commit()
            print("TimescaleDB extension enabled.")

            create_assets_table = """
            CREATE TABLE IF NOT EXISTS assets (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL UNIQUE,
                name VARCHAR(100),
                asset_type VARCHAR(20),
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
            connection.execute(text(create_assets_table))

            create_market_data_table = """
            CREATE TABLE IF NOT EXISTS market_data (
                time TIMESTAMPTZ NOT NULL,
                asset_id INT REFERENCES assets(id),
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                volume BIGINT,
                PRIMARY KEY (time, asset_id)
            );
            """
            connection.execute(text(create_market_data_table))
            
            create_hypertable_query = """
            SELECT create_hypertable('market_data', 'time', if_not_exists => TRUE);
            """
            connection.execute(text(create_hypertable_query))

            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
            connection.execute(text(create_users_table))
            
            create_portfolios_table = """
            CREATE TABLE IF NOT EXISTS portfolios (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id),  -- Legatura cu userul
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
            connection.execute(text(create_portfolios_table))


            create_portfolio_items_table = """
            CREATE TABLE IF NOT EXISTS portfolio_items (
                id SERIAL PRIMARY KEY,
                portfolio_id UUID REFERENCES portfolios(id),
                asset_id INT REFERENCES assets(id),
                weight DECIMAL(5, 4),
                monthly_investment DECIMAL(12, 2)
            );
            """
            connection.execute(text(create_portfolio_items_table))

            connection.commit()
            print("Database schema initialized successfully WITH Users support.")

    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()