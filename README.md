# MarketScope — Historical Stock Market Analytics

An interactive historical equity and ETF research dashboard built with HTML, CSS, JavaScript and Plotly, with a companion Python/SQLite analytics prototype.

## Live demo
Enable GitHub Pages from the repository settings (main branch, root folder), then add the published URL here.

## Features
- Market overview, price performance, risk laboratory and market breadth
- Security screener and individual security research
- Monthly-rebalanced portfolio simulation with SPY benchmark
- Historical market regimes and methodology
- CSV export and interactive filters

## Data
The supplied Kaggle dataset contains historical stock and ETF prices through April 2020. The embedded dashboard snapshot includes 8,047 securities, 122,389 annual observations, and detailed daily/monthly series for 60 securities. The original Kaggle URL and redistribution license were not supplied; confirm them and add attribution before publishing the data publicly. The snapshot is historical, not live. Portfolio simulations omit transaction costs and taxes and may be affected by survivorship and hindsight bias.

## Run locally
Open `index.html` in a browser, or run `python -m http.server 8000` from the repository root and visit http://localhost:8000. No external chart CDN is required.

## Repository structure
- `index.html`: dashboard markup
- `assets/style.css`: dashboard styling
- `assets/app.js`: interactive analytics and chart logic
- `assets/data.js`: precomputed historical data snapshot
- `assets/plotly.min.js`: bundled Plotly.js (MIT)
- `python_sql/`: original Python/SQLite starter, SQL queries and optional Streamlit prototype

## Python and SQL companion
Place `stocks.zip`, `etfs.zip`, and `symbols_valid_meta.csv` in a local data directory. From `python_sql/` run:

```bash
pip install -r requirements.txt
python build_database.py --data-dir /path/to/data
streamlit run dashboard.py
```

The companion imports 10 selected securities by default; use `--symbols` to specify more. It is an earlier prototype, not the exact full-data aggregation pipeline that generated the embedded dashboard snapshot. SQL examples are in `python_sql/sql/analysis.sql`.

## Publishing
Do not commit raw ZIP archives or generated SQLite databases. Verify the source data license before publishing `assets/data.js`. Plotly retains its own MIT license notice.
