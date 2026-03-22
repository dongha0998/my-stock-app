import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="Plotly 주식 마스터", layout="wide")

st.title("📈 Plotly 프로페셔널 주식 차트")

# 2. 사이드바 설정
st.sidebar.header("조회 설정")
ticker = st.sidebar.text_input("종목 코드 (예: TSLA, AAPL, 005930.KS)", value="TSLA")
period = st.sidebar.selectbox("기간 선택", ["1mo", "3mo", "6mo", "1y", "5y", "max"])
interval = st.sidebar.selectbox("간격 선택", ["1d", "1wk", "1mo"])

# 3. 데이터 가져오기
@st.cache_data
def load_data(symbol, p, i):
    df = yf.download(symbol, period=p, interval=i)
    return df

try:
    data = load_data(ticker, period, interval)
    
    if not data.empty:
        # 4. Plotly 캔들스틱 차트 생성
        fig = go.Figure()

        # 캔들스틱 추가 (시가, 고가, 저가, 종가)
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='주가'
        ))

        # 이동평균선(MA20) 추가 (선택 사항)
        data['MA20'] = data['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], name='20일 이동평균선', line=dict(color='orange', width=1)))

        # 5. 차트 디자인 설정
        fig.update_layout(
            title=f"{ticker} 주가 분석 차트",
            yaxis_title="가격 (USD/KRW)",
            xaxis_rangeslider_visible=True, # 하단 범위 조절 바
            template="plotly_dark",         # 다크 모드 적용
            height=600
        )

        # 6. Streamlit 화면에 표시
        st.plotly_chart(fig, use_container_width=True)

        # 7. 보조 정보 출력
        col1, col2, col3 = st.columns(3)
        col1.metric("최고가", f"{data['High'].max():.2f}")
        col2.metric("최저가", f"{data['Low'].min():.2f}")
        col3.metric("거래량", f"{data['Volume'].iloc[-1]:,}")

    else:
        st.error("데이터를 불러올 수 없습니다. 종목 코드를 다시 확인하세요.")

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
