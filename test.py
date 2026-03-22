import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 설정 (웹 브라우저 탭 이름과 레이아웃)
st.set_page_config(page_title="나만의 주식 분석기", layout="wide")

# 2. 제목 및 사용법 안내
st.title("📊 실시간 주식 시세 & 차트 분석")
st.markdown("""
입력창에 **종목 코드**를 입력하세요.  
- **한국 주식:** 종목번호 6자리 (예: 삼성전자는 `005930`, SK하이닉스는 `000660`)  
- **미국 주식:** 티커 입력 (예: 테슬라는 `TSLA`, 애플은 `AAPL`, 엔비디아는 `NVDA`)
""")

# 3. 사이드바 구성
st.sidebar.header("조회 설정")
user_input = st.sidebar.text_input("종목 코드 입력", value="NVDA").strip()
period = st.sidebar.selectbox("조회 기간", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

# 4. 종목 코드 처리 (한국 주식 자동 인식)
if user_input.isdigit() and len(user_input) == 6:
    # 숫자 6자리면 한국 주식(KOSPI)으로 간주하여 .KS를 붙여줌
    ticker = f"{user_input}.KS"
else:
    # 그 외에는 입력한 문자 그대로(미국 주식 등) 사용
    ticker = user_input.upper()

# 5. 데이터 가져오기
@st.cache_data(ttl=3600) # 1시간 동안 데이터를 기억해서 속도를 높임
def load_stock_data(symbol, p):
    try:
        df = yf.download(symbol, period=p, interval="1d")
        return df
    except Exception:
        return None

data = load_stock_data(ticker, period)

# 6. 화면 출력 로직
if data is not None and not data.empty:
    # 현재가 및 등락폭 계산
    current_price = data['Close'].iloc[-1]
    prev_price = data['Close'].iloc[-2]
    change = current_price - prev_price
    change_percent = (change / prev_price) * 100

    # 지표 요약 (Metric)
    col1, col2, col3 = st.columns(3)
    col1.metric("종목", ticker)
    col2.metric("현재가", f"{current_price:.2f}", f"{change:.2f} ({change_percent:.2f}%)")
    col3.metric("거래량", f"{data['Volume'].iloc[-1]:,}")

    # 7. Plotly 캔들스틱 차트 생성
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='주가'
    )])

    # 차트 디자인 수정 (최신 Streamlit 규격 적용)
    fig.update_layout(
        title=f"{ticker} 주가 흐름 ({period})",
        yaxis_title="Price",
        template="plotly_dark",
        xaxis_rangeslider_visible=True,
        height=600,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    # 차트 출력
    st.plotly_chart(fig, width='stretch')

    # 8. 데이터 표 보여주기 (최근 5일)
    with st.expander("최근 데이터 상세보기"):
        st.table(data.tail(5).sort_index(ascending=False))

else:
    st.error(f"❌ '{ticker}' 데이터를 찾을 수 없습니다. 코드가 정확한지 확인해 주세요.")
