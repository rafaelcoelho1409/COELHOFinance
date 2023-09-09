import streamlit as st
import json
import investpy
import datetime as dt
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
#MODELS
from arch import arch_model
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
        "$$\\textbf{VOLATILITY}$$",
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
with main_tabs[1]:
    st.write("$$\\underline{\\huge{\\textbf{Multivariate Volatility Forecast}}}$$")
    data = multidata_yf[[x for x in multidata_yf.columns if x[0] == feature_filter]]
    returns = 100 * data[feature_filter].pct_change().dropna()
    cols = st.columns(2)
    with cols[0]:
        fig = make_subplots(
            rows = len(returns.columns),
            cols = 1
        )
        for i, x in enumerate(returns.columns):
            fig.add_trace(
                go.Scatter(
                    x = returns.index,
                    y = returns[x],
                    mode = "lines",
                    name = x
                ),
                row = i + 1,
                col = 1
            )
        fig.update_layout(
            height = 800
        )
        fig.layout.title = "RETURNS"
        st.plotly_chart(fig)
    with cols[1]:
        st.write("$$\\huge{\\textbf{Conditional Correlation Matrix}}$$")
        coeffs, cond_vol, std_resids, models = [], [], [], []
        with st.spinner(
            text = "Loading GARCH models"
        ):
            for asset in returns.columns:
                model = arch_model(
                    returns[asset],
                    mean = "constant",
                    vol = "GARCH",
                    p = 1,
                    q = 1
                )
                model = model.fit(
                    update_freq = 0,
                    disp = "off"
                )
                coeffs.append(model.params)
                cond_vol.append(model.conditional_volatility)
                std_resids.append(model.std_resid)
                models.append(model)
            coeffs_df = pd.DataFrame(coeffs, index = returns.columns)
            cond_vol_df = pd.DataFrame(cond_vol).transpose().set_axis(returns.columns, axis = "columns")
            std_resids_df = pd.DataFrame(std_resids).transpose().set_axis(returns.columns, axis = "columns")
            #CONDITIONAL CORRELATION MATRIX (R)
            R = std_resids_df.transpose().dot(std_resids_df).div(len(std_resids_df))
            diag = []
            D = np.zeros((len(element_filter), len(element_filter)))
            for model in models:
                diag.append(
                    model.forecast(horizon = 1).variance.iloc[-1, 0]
                )
            #obtain volatility from variance
            diag = np.sqrt(diag)
            np.fill_diagonal(D, diag)
            #calculate the conditional covariance matrix
            D_R = np.matmul(D, R.values)
            H = np.matmul(D_R, D)
            H = pd.DataFrame(H, columns = returns.columns, index = returns.columns)
        #st.write(H)
        fig3 = px.imshow(
            H,
            text_auto = True,
            aspect = "auto",
            color_continuous_scale = "RdBu_r")
        st.plotly_chart(
            fig3,
            use_container_width = True)
with main_tabs[2]: #NEWS TAB
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
