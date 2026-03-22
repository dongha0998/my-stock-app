import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# 1. 페이지 기본 설정
st.set_page_config(page_title="주식 차트 마스터", layout="wide")

# 2. 헤더 및 설명
st.title("📈 실시간 주식 분석 대시보드")
st.info("💡 **팁**: 삼성전자는 `005930`, 애플은 `AAPL`, 테슬라는 `TSLA`를 입력하세요.")

# 3. 사이드바 - 사용자 입력
st.sidebar.header("조회 설정")
user_input = st.sidebar.text_input("종목 코드 또는 티커 입력", value="005930").strip()
period = st.sidebar.selectbox("조회 기간", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)

# 4. [핵심] 종목 코드 판별 로직 (오류 방지)
if user_input.isdigit():
    if len(user_input) == 6:
        # 한국 주식 (숫자 6자리) -> .KS(코스피) 시도 후 데이터 없으면 .KQ(코스닥)
        ticker = f"{user_input}.KS"
    else:
        st.error("❗ 한국 종목 코드는 6자리 숫자여야 합니다.")
        st.stop()
else:
    # 미국 주식 또는 기타 (영문자)
    ticker = user_input.upper()

# 5. 데이터 불러오기
@st.cache_data(ttl=600) # 10분간 캐시 보관
def get_data(symbol, p):
    try:
        # 1차 시도 (입력된 티커로 가져오기)
        df = yf.download(symbol, period=p, interval="1d")
        
        # 만약 코스피(.KS)로 안 나오면 코스닥(.KQ)으로 한 번 더 시도
        if df.empty and symbol.endswith(".KS"):
            symbol_kq = symbol.replace(".KS", ".KQ")
            df = yf.download(symbol_kq, period=p, interval="1d")
            return df, symbol_kq
            
        return df, symbol
    except:
        return None, symbol

data, final_ticker = get_data(ticker, period)

# 6. 차트 및 정보 출력
if data is not None and not data.empty:
    # 상단 지표 (Metric)
    current_price = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[-2]
    change = current_price - prev_close
    percent = (change / prev_close) * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("최종 종목 코드", final_ticker)
    col2.metric("현재가", f"{current_price:,.2f}", f"{change:,.2f} ({percent:.2f}%)")
    col3.metric("거래량", f"{data['Volume'].iloc[-1]:,}")

    # Plotly 캔들스틱 차트 (봉차트)
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='주가'
    )])

    fig.update_layout(
        title=f"{final_ticker} 주가 흐름 (기간: {period})",
        template="plotly_dark",
        xaxis_rangeslider_visible=True,
        height=600,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    # 차트 출력 (2026년 규격: width='stretch')
    st.plotly_chart(fig, width='stretch')

    # 데이터 테이블
    with st.expander("최근 시세 데이터 보기"):
        st.dataframe(data.tail(10).sort_index(ascending=False), use_container_width=True)

else:
    st.error(f"❌ '{ticker}' 데이터를 찾을 수 없습니다. 코스피/코스닥 번호나 미국 티커를 확인하세요.")
