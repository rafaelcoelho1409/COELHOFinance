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
    get_multindex,
    get_news,
    option_menu)

st.set_page_config(
    page_title = "COELHO Finance - MULTINDEX",
    layout = "wide"
)

option_menu()

st.title("COELHO Finance - MULTINDEX")

index_data = pd.json_normalize(
    json.load(open("./data/index_list.json", "r"))
)
index_data["options"] = index_data["indexId"] + " - " + index_data["indexName"]
index_data["market"] = index_data["market"].str.upper()
index_data["indexId"] = "^" + index_data["indexId"]
index_data["options2"] = index_data["indexId"] + " (" + index_data["market"] + ") - " + index_data["indexName"]

with st.sidebar:
    with st.form("market_form"):
        market_filter = st.multiselect(
            label = "Market",
            placeholder = "Market",
            options = sorted(
                set(
                    index_data["market"]
                )
            ),
            key = "market_filter"
        )
        market_button = st.form_submit_button(
            label = "Select market",
            use_container_width = True
        )
        if market_button:
            market_filter = st.session_state["market_filter"]
    with st.form("search_form"):
        index_options = index_data[
            index_data["market"].isin(market_filter)]["options2"]
        index_filter = st.multiselect(
            label = f"Index",
            placeholder = "Index",
            options = sorted(index_options),
            key = "stock_filter"
        )
        index = index_data[index_data["options2"].isin(index_filter)]["indexId"].tolist()
        long_name = index_data[index_data["indexId"].isin(index)]["indexName"]
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
            startdate_filter = st.session_state["startdate_filter"]
            enddate_filter = st.session_state["enddate_filter"]

multi_index = index_data[index_data["options2"].isin(index_filter)]["indexId"].tolist()
indexes = " ".join(multi_index)
try:
    tickers, multidata = get_multindex(indexes, startdate_filter, enddate_filter)
except:
    pass

main_tabs = st.tabs([
    "MULTINDEX",
    "NEWS"
])

with main_tabs[0]: #MULTINDEX TAB
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
            y_filter = [(feature_filter, ticker) for ticker in multi_index]
            for x in y_filter:
                fig.add_trace(
                    go.Scatter(
                        x = multidata.index,
                        y = multidata[x],
                        mode = "lines+markers",
                        name = x[1]
                    )
                )
            fig.layout.title = "INDEX COMPARISON"
            st.plotly_chart(fig)
        except:
            st.write("No information.")
    with col2:
        try:
            corr_df = multidata[[(feature_filter, ticker) for ticker in multi_index]].corr()
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
        label = "About indexes"
    ):
        st.dataframe(
            index_data[index_data["options2"].isin(index_filter)].drop([
                "options",
                "options2"], axis = 1),
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