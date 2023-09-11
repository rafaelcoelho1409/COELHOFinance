import streamlit as st
import os
import json
import investpy
import datetime as dt
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import quantstats as qs
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
    commodities_filter_func2,
    efficient_frontier,
    efficient_frontier2,
    conditional_correlation_matrix)

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
        "$$\\textbf{ASSET ALLOCATION}$$",
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
with main_tabs[1]: #VOLATILITY TAB
    st.write("$$\\underline{\\huge{\\textbf{Multivariate Volatility Forecast}}}$$")
    try:
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
            fig3 = conditional_correlation_matrix(returns, element_filter)
            st.plotly_chart(
                fig3,
                use_container_width = True)
    except:
        st.write("No informations.")
with main_tabs[2]: #ASSET ALLOCATION TAB
    tabs = st.tabs([
        "$$\\textbf{Equally-weighted Portfolio}$$",
        "$$\\textbf{Efficient Frontier}$$",
        "$$\\textbf{Efficient Frontier \& Risk Aversion}$$",
    ])
    with tabs[0]:
        st.write("$$\\underline{\\huge{\\textbf{Equally-weighted Portfolio}}}$$")
        try:
            n_assets = len(element_filter)
            returns = multidata_yf[feature_filter].pct_change().dropna()
            portfolio_weights = n_assets * [1 / n_assets]
            portfolio_returns = pd.Series(
                np.dot(portfolio_weights, returns.T),
                index = returns.index
            )
            img_code = np.random.randint(1000000)
            qs.reports.html(
                portfolio_returns,
                benchmark = "SPY",
                title = "1/n portfolio",
                output = f"assets/portfolio_evaluation_{img_code}.html"
            )
            st.download_button(
                label = "Get Full Report",
                data = open(f"assets/portfolio_evaluation_{img_code}.html", "r").read(),
                file_name = f"assets/portfolio_evaluation_{img_code}.html",
                mime = "text/html",
                use_container_width = True
            )
            os.remove(f"assets/portfolio_evaluation_{img_code}.html")
            st.write("$$\\huge{\\textbf{1/n Portfolio's Performance}}$$")
            qs.plots.snapshot(
                portfolio_returns,
                savefig = f"assets/portfolio_returns_{img_code}.png"
            )
            st.image(
                f"assets/portfolio_returns_{img_code}.png",
                use_column_width = True)
            os.remove(f"assets/portfolio_returns_{img_code}.png")
        except:
            st.write("No informations.")
    with tabs[1]:
        st.write("$$\\underline{\\huge{\\textbf{Efficient Frontier (Monte Carlo Simulation)}}}$$")
        try:
            fig = efficient_frontier(multidata_yf, element, feature_filter)
            st.pyplot(
                fig,
                use_container_width = True
            )
        except:
            st.write("No informations.")
    with tabs[2]:
        st.write("$$\\underline{\\huge{\\textbf{Efficient Frontier \& Risk Aversion}}}$$")
        try:
            fig1, fig2 = efficient_frontier2(multidata_yf, feature_filter, element)
            cols = st.columns(2)
            with cols[0]:
                st.write("$$\\Large{\\textbf{Risk-Aversion Allocation}}$$")
                st.pyplot(
                    fig1,
                    use_container_width = True
                )
            with cols[1]:
                st.write("$$\\Large{\\textbf{Efficient Frontier (Convex Optimization)}}$$")
                st.pyplot(
                    fig2,
                    use_container_width = True
                )
        except:
            st.write("No informations.")
with main_tabs[3]: #NEWS TAB
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
