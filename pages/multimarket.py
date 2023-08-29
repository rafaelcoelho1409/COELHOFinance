import streamlit as st
import json
import investpy
import datetime as dt
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
#STREAMLIT THIRD-PARTY
from streamlit_extras.grid import grid
from streamlit_extras.metric_cards import style_metric_cards
#internal functions
from functions import (
    get_multimarket,
    get_news,
    option_menu,
    stocks_filter_func2,
    indices_filter_func2,
    cryptos_filter_func2,
    currency_crosses_filter_func2,
    funds_filter_func2,
    etfs_filter_func2,
    bonds_filter_func2,
    commodities_filter_func2)

st.set_page_config(
    page_title = "COELHO Finance - MULTIMARKET",
    layout = "wide"
)

option_menu()

st.title("$$\\large{\\textbf{COELHO Finance - MULTIMARKET}}$$")

with open("./data/periods_and_intervals.json", "r") as f:
    periods_and_intervals = json.load(f)

with st.sidebar:
    asset_filter = st.selectbox(
        label = "Asset type",
        placeholder = "Asset type",
        options = [
            "Stocks",
            "Indices",
            "Crypto",
            "Currency Crosses",
            "Funds",
            "ETFs",
            "Commodities",
            "Bonds"
        ],
        index = 0,
        key = "investment_filter")
    if asset_filter == "Stocks":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            quote_type,
            long_name,
            short_name,
            feature_filter
        ) = stocks_filter_func2(periods_and_intervals)
    elif asset_filter == "Indices":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            long_name,
            currency,
            feature_filter
        ) = indices_filter_func2(periods_and_intervals)
    elif asset_filter == "Crypto":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name,
            currency,
            feature_filter
        ) = cryptos_filter_func2(periods_and_intervals)
    elif asset_filter == "Currency Crosses":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name,
            currency,
            feature_filter
        ) = currency_crosses_filter_func2(periods_and_intervals)
    elif asset_filter == "Funds":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            currency,
            feature_filter
        ) = funds_filter_func2(periods_and_intervals)
    elif asset_filter == "ETFs":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            long_name,
            currency,
            feature_filter
        ) = etfs_filter_func2(periods_and_intervals)
    elif asset_filter == "Bonds":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name,
            feature_filter
        ) = bonds_filter_func2(periods_and_intervals)
    elif asset_filter == "Commodities":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name,
            feature_filter
        ) = commodities_filter_func2(periods_and_intervals)
    else:
        st.write("$$\\textbf{UNDER CONSTRUCTION}$$")
        st.stop()

main_tabs = st.tabs([
        "$$\\textbf{MULTIMARKET}$$",
        "$$\\textbf{NEWS}$$"
])

try:
    (
        tickers_yf,
        multidata_yf
    ) = get_multimarket(
        element,
        periods_and_intervals[0]["period"][period_filter], 
        periods_and_intervals[1]["interval"][interval_filter],
        "YFinance"
    )
    (
        tickers_yq,
        multidata_yq
    ) = get_multimarket(
        element,
        periods_and_intervals[0]["period"][period_filter], 
        periods_and_intervals[1]["interval"][interval_filter],
        "YahooQuery"
    )
except:
    pass

with main_tabs[0]: #COMPARISON TAB
    grid1 = grid([3, 3], [3, 3], vertical_align = True)
    grid1.write("$$\\textbf{Comparison Chart}$$")
    grid1.write("$$\\textbf{Correlation matrix (" + feature_filter + ")}$$")
    fig = go.Figure()
    y_filter = [(feature_filter, ticker) for ticker in element]
    for x in y_filter:
        fig.add_trace(
            go.Scatter(
                x = multidata_yf.index,
                y = multidata_yf[x],
                mode = "lines",
                name = x[1]
            )
        )
    grid1.plotly_chart(
        fig,
        use_container_width = True)
    try:
        corr_df = multidata_yf[[(feature_filter, ticker) for ticker in element]].corr()
        corr_df.columns = [x[1] for x in corr_df.columns]
        corr_df.index = [x[1] for x in corr_df.index]
        fig2 = px.imshow(
            corr_df,
            text_auto = True,
            aspect = "auto",
            color_continuous_scale = "RdBu_r")
        grid1.plotly_chart(
            fig2,
            use_container_width = True)
    except:
        pass
with main_tabs[1]: #NEWS TAB
    st.write("$$\\underline{\\huge{\\textbf{Latest News}}}$$")
    try:
        subtabs = st.tabs(element.tolist())
        for i, x in enumerate(element.tolist()):
            with subtabs[i]:
                try:
                    get_news(tickers_yf.news()[x])
                except:
                    st.write("No informations.")
    except:
        st.write("No informations.")
