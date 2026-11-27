"""Build a reproducible SQLite database directly from the original ZIP archives."""
import argparse
import csv
import io
import sqlite3
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
DEFAULT = ['AAPL','MSFT','NVDA','AMZN','GOOGL','TSLA','SPY','QQQ','VTI','IWM']

def build(data_dir: Path, output: Path, symbols: list[str]):
    con = sqlite3.connect(output)
    con.executescript('''
    DROP VIEW IF EXISTS daily_returns;
    DROP TABLE IF EXISTS prices;
    DROP TABLE IF EXISTS securities;
    CREATE TABLE securities(symbol TEXT PRIMARY KEY, security_name TEXT, exchange TEXT, is_etf INTEGER);
    CREATE TABLE prices(symbol TEXT NOT NULL, date TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL, adj_close REAL, volume INTEGER, PRIMARY KEY(symbol,date), FOREIGN KEY(symbol) REFERENCES securities(symbol));
    CREATE INDEX idx_prices_date ON prices(date);
    ''')
    meta = {}
    with (data_dir/'symbols_valid_meta.csv').open(encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            meta[r['Symbol']] = r
    total = 0
    for archive,kind in [('stocks.zip','stocks'),('etfs.zip','etfs')]:
        with zipfile.ZipFile(data_dir/archive) as z:
            available = set(z.namelist())
            for symbol in symbols:
                name=f'{kind}/{symbol}.csv'
                if name not in available: continue
                m=meta.get(symbol,{})
                con.execute('INSERT OR REPLACE INTO securities VALUES (?,?,?,?)',(symbol,m.get('Security Name',symbol),m.get('Listing Exchange',''),int(kind=='etfs')))
                batch=[]
                with io.TextIOWrapper(z.open(name),encoding='utf-8-sig',newline='') as f:
                    for r in csv.DictReader(f):
                        try:
                            vals=(symbol,r['Date'],float(r['Open']),float(r['High']),float(r['Low']),float(r['Close']),float(r['Adj Close']),int(float(r['Volume'])))
                            if vals[6] <= 0 or vals[5] <= 0 or vals[7]<0: continue
                            batch.append(vals)
                        except (ValueError,KeyError,TypeError): continue
                        if len(batch)>=5000:
                            con.executemany('INSERT OR REPLACE INTO prices VALUES (?,?,?,?,?,?,?,?)',batch)
                            total+=len(batch);batch=[]
                    con.executemany('INSERT OR REPLACE INTO prices VALUES (?,?,?,?,?,?,?,?)',batch);total+=len(batch)
                print(f'{symbol}: loaded from {kind}')
    con.executescript('''
    CREATE VIEW daily_returns AS
    SELECT symbol,date,adj_close,volume,
      (adj_close / LAG(adj_close) OVER (PARTITION BY symbol ORDER BY date) - 1.0) AS daily_return
    FROM prices;
    ''')
    con.commit()
    print(f'Wrote {total:,} price rows to {output}')
    con.close()

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--data-dir',type=Path,default=BASE.parent)
    p.add_argument('--output',type=Path,default=BASE/'market.db')
    p.add_argument('--symbols',nargs='+',default=DEFAULT,help='Symbols to import; use a larger list to expand the project')
    a=p.parse_args()
    build(a.data_dir,a.output,[s.upper() for s in a.symbols])
