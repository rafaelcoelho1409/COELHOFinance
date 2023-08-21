import streamlit as st
import json
import datetime as dt
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from streamlit_extras.row import row
from streamlit_extras.metric_cards import style_metric_cards
#internal functions
from functions import (
    get_multistock,
    get_news,
    option_menu)

st.set_page_config(
    page_title = "COELHO Finance - MULTISTOCK",
    layout = "wide"
)

option_menu()

st.title("COELHO Finance - MULTISTOCK")

with st.sidebar:
    with st.form("market_form"):
        market_filter = st.selectbox(
            label = "Market",
            placeholder = "Market",
            options = sorted([
                market["market"].upper()
                for market 
                in json.load(open("./data/market_list.json", "r"))]),
            key = "market_filter"
        )
        market_button = st.form_submit_button(
            label = "Select market",
            use_container_width = True
        )
        if market_button:
            market_filter = st.session_state["market_filter"]
    with st.form("search_form"):
        market_data = pd.json_normalize(
            json.load(open(f"./data/symbols/{market_filter.lower()}.json", "r")))\
                .sort_values(by = "symbol")\
                .reset_index(drop = True)
        market_data["options"] = market_data["symbol"] + " - " + market_data["longName"] + " (" + market_data["shortName"] + ")"
        stock_filter = st.multiselect(
            label = "Stock (You can choose more than one stock)",
            placeholder = "Stock",
            options = market_data["options"][
                market_data["options"].notnull()]
        )
        stock = market_data[market_data["options"].isin(stock_filter)]["symbol"]
        exchange = market_data[market_data["options"].isin(stock_filter)]["exchange"]
        quote_type = market_data[market_data["options"].isin(stock_filter)]["quoteType"]
        short_name = market_data[market_data["options"].isin(stock_filter)]["shortName"]
        long_name = market_data[market_data["options"].isin(stock_filter)]["longName"]
        startdate_filter = st.date_input(
            "Start date",
            dt.datetime.now() - dt.timedelta(days = 30),
            key = "startdate_filter"
        )
        enddate_filter = st.date_input(
            "End date",
            dt.datetime.now(),
            key = "enddate_filter"
        )
        feature_filter = st.selectbox(
            label = "Feature",
            placeholder = "Feature",
            options = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Dividends",
                "Stock Splits"
            ],
            index = 3,
            key = "feature_filter"
        )
        search_button = st.form_submit_button(
            label = "Search",
            use_container_width = True
        )
        if search_button:
            stock = stock
            startdate_filter = st.session_state["startdate_filter"]
            enddate_filter = st.session_state["enddate_filter"]

multi_stock = market_data[market_data["options"].isin(stock_filter)]["symbol"].tolist()
stocks = " ".join(multi_stock)
try:
    tickers, multidata = get_multistock(stocks, startdate_filter, enddate_filter)
except:
    pass

main_tabs = st.tabs([
    "MULTISTOCK",
    "NEWS"
])
with main_tabs[0]:
    with st.expander(
        label = "Indicators",
        expanded = True
    ):
        row1 = row(3, vertical_align = True)
        for x in {
            "Feature": feature_filter, 
            "Start date": startdate_filter, 
            "End date": enddate_filter}.items():
            row1.metric(
                label = x[0],
                value = str(x[1])
            )
        style_metric_cards(
            background_color = "#000000"
        )
    col1, col2 = st.columns(2)
    with col1:
        try:
            fig = go.Figure()
            y_filter = [(feature_filter, ticker) for ticker in multi_stock]
            for x in y_filter:
                fig.add_trace(
                    go.Scatter(
                        x = multidata.index,
                        y = multidata[x],
                        mode = "lines+markers",
                        name = x[1]
                    )
                )
            fig.layout.title = "STOCK COMPARISON"
            st.plotly_chart(fig)
        except:
            st.write("No information.")
    with col2:
        try:
            corr_df = multidata[[(feature_filter, ticker) for ticker in multi_stock]].corr()
            corr_df.columns = [x[1] for x in corr_df.columns]
            corr_df.index = [x[1] for x in corr_df.index]
            fig = px.imshow(
                corr_df,
                text_auto = True,
                aspect = "auto",
                color_continuous_scale = "RdBu_r")
            fig.layout.title = f"CORRELATION ({feature_filter})"
            st.plotly_chart(fig)
        except:
            st.write("No information.")
    with st.expander(
        label = "About stocks"
    ):
        st.dataframe(
            market_data[market_data["options"].isin(stock_filter)].drop("options", axis = 1),
            use_container_width = True,
            hide_index = True)
with main_tabs[1]: #NEWS TAB
    st.title("Latest News")
    try:
        news = tickers.news()
        subtabs = st.tabs(news.keys())
        for i, x in enumerate(news.keys()):
            with subtabs[i]:
                get_news(news[x])
    except:
        st.write("No information.")