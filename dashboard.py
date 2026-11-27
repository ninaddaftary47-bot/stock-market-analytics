"""Interactive stock and ETF analytics dashboard (historical data only)."""
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Stock Market Analytics',layout='wide')
st.title('Stock Market Analytics | Historical Data')
st.caption('Kaggle historical data through April 2020. Educational analysis, not live prices or investment advice.')
DB=Path(__file__).resolve().parent/'market.db'
if not DB.exists():
    st.error('Database not found. Run: python build_database.py');st.stop()
@st.cache_data
def load():
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query('SELECT p.*,s.security_name,s.is_etf FROM prices p JOIN securities s USING(symbol) ORDER BY symbol,date',con,parse_dates=['date'])
df=load()
syms=sorted(df.symbol.unique())
selected=st.sidebar.multiselect('Stocks and ETFs',syms,default=[s for s in ['AAPL','MSFT','NVDA','SPY'] if s in syms])
if not selected: st.info('Select at least one security.');st.stop()
lo,hi=df.date.min().date(),df.date.max().date()
start,end=st.sidebar.date_input('Date range',(max(lo,pd.Timestamp('2015-01-01').date()),hi),min_value=lo,max_value=hi)
if start>end:st.error('Start date must be before end date.');st.stop()
x=df[df.symbol.isin(selected)&df.date.between(pd.Timestamp(start),pd.Timestamp(end))].copy()
if x.empty:st.warning('No data for these filters.');st.stop()
x=x.sort_values(['symbol','date'])
x['daily_return']=x.groupby('symbol')['adj_close'].pct_change(fill_method=None)
x['normalized']=100*x['adj_close']/x.groupby('symbol')['adj_close'].transform('first')
x['running_peak']=x.groupby('symbol')['adj_close'].cummax()
x['drawdown']=x['adj_close']/x['running_peak']-1
stats=x.groupby('symbol').agg(start_price=('adj_close','first'),end_price=('adj_close','last'),avg_volume=('volume','mean'),trading_days=('date','count'))
stats['total_return_pct']=(stats.end_price/stats.start_price-1)*100
stats['annual_volatility_pct']=x.groupby('symbol').daily_return.std()*np.sqrt(252)*100
stats['max_drawdown_pct']=x.groupby('symbol').drawdown.min()*100
st.subheader('Portfolio comparison KPIs')
a,b,c,d=st.columns(4)
a.metric('Securities',len(stats));b.metric('Price records',f'{len(x):,}');c.metric('Average total return',f'{stats.total_return_pct.mean():.1f}%');d.metric('Total shares traded',f'{x.volume.sum():,.0f}')
st.plotly_chart(px.line(x,x='date',y='normalized',color='symbol',title='Normalized adjusted closing price (starting at 100)',labels={'normalized':'Index (start = 100)'}),use_container_width=True)
left,right=st.columns(2)
with left:
    st.plotly_chart(px.bar(stats.reset_index(),x='symbol',y='total_return_pct',title='Total return (%)',text_auto='.1f'),use_container_width=True)
with right:
    st.plotly_chart(px.bar(stats.reset_index(),x='symbol',y='annual_volatility_pct',title='Annualized volatility (%)',text_auto='.1f'),use_container_width=True)
st.plotly_chart(px.line(x,x='date',y='drawdown',color='symbol',title='Drawdown from previous peak'),use_container_width=True)
st.subheader('Correlation of daily returns')
returns=x.pivot(index='date',columns='symbol',values='daily_return')
cor=returns.corr(min_periods=20)
st.plotly_chart(px.imshow(cor,text_auto='.2f',zmin=-1,zmax=1,color_continuous_scale='RdBu_r',title='Daily-return correlations'),use_container_width=True)
st.subheader('Security summary')
st.dataframe(stats.round(2),use_container_width=True)
st.download_button('Download filtered price data',x.to_csv(index=False).encode('utf-8'),'filtered_prices.csv','text/csv')
