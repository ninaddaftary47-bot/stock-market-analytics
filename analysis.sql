-- Run these queries against market.db in SQLite.
-- 1. Available securities and coverage
SELECT s.symbol, s.security_name, s.is_etf, COUNT(*) AS trading_days,
       MIN(p.date) AS first_date, MAX(p.date) AS last_date
FROM securities s JOIN prices p USING(symbol)
GROUP BY s.symbol ORDER BY trading_days DESC;

-- 2. Annual trading volume by stock
SELECT symbol, substr(date,1,4) AS year, SUM(volume) AS annual_volume
FROM prices GROUP BY symbol,substr(date,1,4)
ORDER BY year,symbol;

-- 3. Annual returns using adjusted closing prices
WITH annual AS (
  SELECT symbol,substr(date,1,4) AS year,date,adj_close,
         ROW_NUMBER() OVER(PARTITION BY symbol,substr(date,1,4) ORDER BY date) AS first_rank,
         ROW_NUMBER() OVER(PARTITION BY symbol,substr(date,1,4) ORDER BY date DESC) AS last_rank
  FROM prices
), summary AS (
 SELECT symbol,year,
 MAX(CASE WHEN first_rank=1 THEN adj_close END) AS first_adj_close,
 MAX(CASE WHEN last_rank=1 THEN adj_close END) AS last_adj_close
 FROM annual GROUP BY symbol,year
)
SELECT symbol,year,ROUND(100*(last_adj_close/NULLIF(first_adj_close,0)-1),2) AS return_pct
FROM summary ORDER BY year,symbol;

-- 4. Largest positive and negative single-day returns
SELECT symbol,date,ROUND(100*daily_return,2) AS daily_return_pct
FROM daily_returns WHERE daily_return IS NOT NULL
ORDER BY ABS(daily_return) DESC LIMIT 20;
