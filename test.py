import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="주식 검색 마스터", layout="wide")

st.title("🔍 스마트 주식 검색 & 차트")

# 에러가 났던 get_stock_list 대신, 직접 입력 방식으로 변경
st.sidebar.header("종목 검색")
search_input = st.sidebar.text_input("종목 코드 또는 이름을 입력하세요", value="AAPL")

# 한국 주식인지 확인하는 간단한 로직 (숫자 6자리면 .KS 붙이기)
if search_input.isdigit() and len(search_input) == 6:
    ticker_code = f"{search_input}.KS"
    display_name = f"한국 종목 ({search_input})"
else:
    ticker_code = search_input.upper()
    display_name = ticker_code

# 데이터 로드 및 차트 출력
try:
    # 데이터 가져오기 (기간 1년)
    data = yf.download(ticker_code, period="1y", interval="1d")
    
    if not data.empty:
        # Plotly 캔들스틱 차트
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=ticker_code
        )])
        
        fig.update_layout(
            title=f"{display_name} 주가 추이",
            template="plotly_dark",
            xaxis_rangeslider_visible=True
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # 지표 출력
        col1, col2 = st.columns(2)
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        col1.metric("현재가", f"{current_price:.2f}")
        col2.metric("전일대비", f"{current_price - prev_price:.2f}")
    else:
        st.warning(f"'{ticker_code}'에 대한 데이터를 찾을 수 없습니다. (예: 삼성전자는 005930, 애플은 AAPL)")

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
