import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import FinanceDataReader as fdr # 종목 검색용
import pandas as pd

st.set_page_config(page_title="주식 검색 마스터", layout="wide")

# 1. 한국 주식 종목 리스트 불러오기 (캐싱 처리로 속도 업)
@st.cache_data
def get_stock_list():
    # 한국 거래소 종목 리스트
    krx = fdr.StockListing('KRX')
    return krx[['Symbol', 'Name']]

stock_df = get_stock_list()

st.title("🔍 스마트 주식 검색 & 차트")

# 2. 사이드바 검색 기능
st.sidebar.header("종목 검색")
search_name = st.sidebar.text_input("회사 이름을 입력하세요 (예: 삼성전자, 테슬라)", value="삼성전자")

# 이름으로 코드 찾기 로직
# 한국 주식 우선 검색
match = stock_df[stock_df['Name'].str.contains(search_name, na=False)]

if not match.empty:
    # 한국 주식일 경우 (코스피는 .KS, 코스닥은 .KQ 추가 필요)
    raw_code = match.iloc['Symbol']
    # 보통 6자리 숫자인 경우 한국 주식
    ticker_code = f"{raw_code}.KS" if len(raw_code) == 6 else raw_code
    st.sidebar.success(f"찾은 종목: {match.iloc['Name']} ({ticker_code})")
else:
    # 한국 주식에 없으면 미국 주식 코드로 직접 사용 (예: TSLA, AAPL)
    ticker_code = search_name.upper()
    st.sidebar.info(f"국내 종목에 없어 입력값 '{ticker_code}'를 직접 사용합니다.")

# 3. 데이터 로드 및 차트 출력 (Plotly)
try:
    data = yf.download(ticker_code, period="1y", interval="1d")
    
    if not data.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=ticker_code
        )])
        
        fig.update_layout(
            title=f"{search_name} ({ticker_code}) 1년 주가 추이",
            template="plotly_dark",
            xaxis_rangeslider_visible=True,
            width=1000 # 최신 경고 대응: stretch 대신 고정 혹은 width 조절
        )
        
        st.plotly_chart(fig, width='stretch') # 2026년형 옵션 적용
        
        # 간단 지표
        col1, col2 = st.columns(2)
        col1.metric("현재가", f"{data['Close'].iloc[-1]:.2f}")
        col2.metric("전일대비", f"{data['Close'].iloc[-1] - data['Close'].iloc[-2]:.2f}")
    else:
        st.warning("데이터를 가져올 수 없습니다. 정확한 이름을 입력해 주세요.")

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")