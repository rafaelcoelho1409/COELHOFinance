import streamlit as st
import yfinance as yf
import yahooquery as yq
import datetime as dt
import pandas as pd
import json
import investpy
import numpy as np
import cvxpy as cp
import plotly.express as px
import base64
import requests
import vectorbt as vbt
from dateutil.relativedelta import relativedelta
import ccxt
#ANOMALY DETECTION
from adtk.data import validate_series
from streamlit_extras.row import row
from streamlit_extras.grid import grid
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.switch_page_button import switch_page
from st_pages import show_pages, Page, Section, add_indentation
#MODELS
from arch import arch_model

with open("./data/periods_and_intervals_binance.json", "r") as f:
    intervals_binance = json.load(f)

@st.cache_resource
def get_unimarket(
    element, 
    period,
    interval,
    source):
    if source == "YFinance":
        ticker = yf.Ticker(element)
    elif source == "YahooQuery":
        ticker = yq.Ticker(element)
    else:
        raise ValueError("Choose YFinance or YahooQuery as data source")
    data = ticker.history(
        period = period,
        interval = interval
    )
    return (
        ticker, 
        data)

@st.cache_resource
def get_unistats(
    element, 
    period,
    interval,
    source = None):
    ticker = yf.Ticker(element)
    data = yf.download(
        element,
        period = period,
        interval = interval
    )
    return ticker, data

@st.cache_resource
def get_multimarket(
    elements, 
    period,
    interval,
    source):
    if source == "YFinance":
        elements_ = " ".join(elements)
        tickers = yf.Tickers(elements_)
    elif source == "YahooQuery":
        tickers = yq.Ticker(elements)
    else:
        raise ValueError("Choose YFinance or YahooQuery as data source")
    data = tickers.history(
        period = period,
        interval = interval
    )
    return (
        tickers, 
        data)

def indicator_metrics(
    stock,
    pattern, 
    indicators, 
    ticker, 
    items_per_line,
    attribute,
    source):
    metrics = [x for x in indicators.keys() if pattern in x]
    #st.header(pattern.capitalize())
    rows = row(items_per_line, vertical_align = True)
    if source == "YFinance":
        for x in metrics:
            rows.metric(
                label = x,
                value = ticker.__getattribute__(attribute)[indicators[x]]
            )
    elif source == "YahooQuery":
        for x in metrics:
            rows.metric(
                label = x,
                value = ticker.__getattribute__(attribute)[stock][indicators[x]]
            )
    style_metric_cards(
        background_color = "#000000"
    )

def general_indicator_metrics(
    _stock,
    _patterns, 
    _indicators, 
    _ticker, 
    _items_per_line,
    _attribute,
    _source):
    #st.header("General indicators")
    general_indicators = _indicators.copy()
    indicators_filtered = {}
    for key, value in _indicators.items():
        for pattern in _patterns[1:]:
            try:
                if pattern in key:
                    indicators_filtered[key] = value
            except:
                pass
    for x in _indicators.keys():
        if x in indicators_filtered.keys():
            general_indicators.pop(x)
    rows = row(_items_per_line, vertical_align = True)
    if _source == "YFinance":
        for x in general_indicators:
            rows.metric(
                label = x,
                value = _ticker.__getattribute__(_attribute)[_indicators[x]]
            )
    elif _source == "YahooQuery":
        for x in general_indicators:
            rows.metric(
                label = x,
                value = _ticker.__getattribute__(_attribute)[_stock][_indicators[x]]
            )
    style_metric_cards(
        background_color = "#000000",
        border_color = "#FF0000"
    )

def get_news(news):
    try:
        news_df = pd.DataFrame(news)
        news_df = news_df[[
            "publisher", 
            "providerPublishTime", 
            "title",
            "link",
            "type",
            "thumbnail",
            "relatedTickers"]]
    except:
        news_df = news_df[[
            "publisher", 
            "providerPublishTime", 
            "title",
            "link",
            "type",
            "thumbnail"]]  
    news_df["providerPublishTime"] = news_df["providerPublishTime"].apply(lambda x: dt.datetime.fromtimestamp(x))
    for x in news_df.iterrows():
        st.markdown(f"### [{x[1]['title']}]({x[1]['link']})")
        st.write("$$\\textbf{Publisher:}$$  " + str(x[1]['publisher']))
        st.write("$$\\textbf{Time:}$$  " + str(x[1]['providerPublishTime']))
        try:
            st.write("$$\\textbf{Related Tickers:}$$  " + ', '.join(y for y in x[1]['relatedTickers']))
        except:
            pass
        st.divider()

def get_reports(reports):
    data = pd.DataFrame(reports)
    for x in data.iterrows():
        st.markdown(f"### {x[1]['headHtml']}")
        st.markdown(f"**ID:** {x[1]['id']}")
        st.markdown(f"**PROVIDER:** {x[1]['provider']}")
        st.markdown(f"**REPORT DATE:** {x[1]['reportDate']}")
        st.markdown(f"**REPORT TITLE:** {x[1]['reportTitle']}")
        st.markdown(f"**TARGET PRICE:** {x[1]['targetPrice']}")
        st.markdown(f"**INVESTMENT RATING:** {x[1]['investmentRating']}")
        st.divider()

def get_sec_reports(sec_reports):
    data = pd.DataFrame(sec_reports)
    for x in data.iterrows():
        st.markdown(f"### [{x[1]['title']}]({x[1]['snapshotUrl']})")
        st.markdown(f"**ID:** {x[1]['id']}")
        st.markdown(f"**TYPE:** {x[1]['type']}")
        st.markdown(f"**DESCRIPTION:** {x[1]['description']}")
        st.markdown(f"**FILING DATE:** {str(dt.datetime.fromtimestamp(x[1]['filingDate']/1000))}")
        st.markdown(f"**FORM TYPE:** {x[1]['formType']}")
        st.divider()

def option_menu():
    show_pages([
        Page("app.py", "COELHO Finance"),
        Section("Financial Market Analytics"),
        Page("pages/unimarket.py", "UNIMARKET"),
        Page("pages/unistats.py", "UNISTATS"),
        Page("pages/multimarket.py", "MULTIMARKET"),
        Page("pages/backtesting.py", "Backtesting"),
        Page("pages/about.py", "About Us", in_section = False),
    ])
    add_indentation()

def realized_volatility(x):
    return np.sqrt(np.sum(x ** 2))

def split_key_name(string):
    return ''.join(map(
                lambda y: y 
                if y.islower() 
                else " " + y, string)).capitalize()

def stocks_filter_func(
    periods_and_intervals, 
    page_title,
    filter_bar):
    with filter_bar.form("market_form"):
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
    with filter_bar.form("search_form"):
        market_data_yf = pd.json_normalize(
                json.load(open(f"./data/symbols/{market_filter.lower()}.json", "r")))\
                    .sort_values(by = "symbol")\
                    .reset_index(drop = True)
        market_data_yf["options"] = market_data_yf["symbol"] + " - " + market_data_yf["longName"] + " (" + market_data_yf["shortName"] + ")"
        element_filter = st.selectbox(
            label = f"Stock ({market_filter})",
            placeholder = "Stock",
            options = sorted(market_data_yf["options"][
                market_data_yf["options"].notnull()]),
            key = "stock_filter"
        )
        element = market_data_yf[market_data_yf["options"] == element_filter]["symbol"].iloc[0]
        exchange = market_data_yf[market_data_yf["options"] == element_filter]["exchange"].iloc[0]
        quote_type = market_data_yf[market_data_yf["options"] == element_filter]["quoteType"].iloc[0]
        short_name = market_data_yf[market_data_yf["options"] == element_filter]["shortName"].iloc[0]
        long_name = market_data_yf[market_data_yf["options"] == element_filter]["longName"].iloc[0]
        period_filter = st.selectbox(
            label = "Period",
            placeholder = "Period",
            options = periods_and_intervals[0]["period"],
            index = 5,
            key = "period_filter"
        )
        if page_title == "COELHO Finance - UNISTATS":
            interval_filter = "1 day"
        else:
            interval_filter = st.selectbox(
                label = "Interval",
                placeholder = "Interval",
                options = periods_and_intervals[1]["interval"],
                index = 8,
                key = "interval_filter"
            )
        search_button = st.form_submit_button(
            label = "Search",
            use_container_width = True
        )
        if search_button:
            period_filter = st.session_state["period_filter"]
            try:
                interval_filter = st.session_state["interval_filter"]
            except:
                pass
        return (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            quote_type,
            long_name,
            short_name
        )
    
def indices_filter_func(
    periods_and_intervals,
    page_title,
    filter_bar):
    index_data = investpy.indices.get_indices()
    index_data["options"] = index_data["symbol"] + " - " + index_data["name"]
    index_data["country"] = index_data["country"].str.upper()
    index_data["symbol_yf"] = "^" + index_data["symbol"]
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("market_form"):
            market_filter = st.selectbox(
                label = "Market",
                placeholder = "Market",
                options = sorted(index_data["country"].unique()),
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
                index_data["country"] == market_filter]["options"]
            index_filter = st.selectbox(
                label = f"Index ({market_filter})",
                placeholder = "Index",
                options = sorted(index_options),
                key = "index_filter"
            )
            index = index_data[index_data["options"] == index_filter]["symbol_yf"].tolist()[0]
            exchange = index_data[index_data["options"] == index_filter]["symbol"].tolist()[0]
            currency = index_data[index_data["options"] == index_filter]["currency"].tolist()[0]
            long_name = index_data[index_data["symbol_yf"] == index]["full_name"].tolist()[0]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            if page_title == "COELHO Finance - UNISTATS":
                interval_filter = "1 day"
            else:
                interval_filter = st.selectbox(
                    label = "Interval",
                    placeholder = "Interval",
                    options = periods_and_intervals[1]["interval"],
                    index = 8,
                    key = "interval_filter"
                )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
            try:
                interval_filter = st.session_state["interval_filter"]
            except:
                pass
    return (
        index,
        period_filter,
        interval_filter,
        index_filter,
        exchange,
        long_name,
        currency
    )

def bonds_filter_func(
    periods_and_intervals,
    page_title,
    filter_bar):
    bond_data = pd.read_json("./data/bonds.json")
    bond_data["options"] = bond_data["Symbol"] + " - " + bond_data["Name"]
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("search_form"):
            bond_filter = st.selectbox(
                label = f"Index",
                placeholder = "Index",
                options = sorted(bond_data["options"]),
                key = "index_filter"
            )
            bond = bond_data[bond_data["options"] == bond_filter]["Symbol"].tolist()[0]
            long_name = bond_data[bond_data["Symbol"] == bond]["Name"].tolist()[0]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            if page_title == "COELHO Finance - UNISTATS":
                interval_filter = "1 day"
            else:
                interval_filter = st.selectbox(
                    label = "Interval",
                    placeholder = "Interval",
                    options = periods_and_intervals[1]["interval"],
                    index = 8,
                    key = "interval_filter"
                )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
            try:
                interval_filter = st.session_state["interval_filter"]
            except:
                pass
    return (
        bond,
        period_filter,
        interval_filter,
        bond_filter,
        long_name,
    )

def commodities_filter_func(
    periods_and_intervals,
    page_title,
    filter_bar):
    commodity_data = pd.read_json("./data/commodities.json")
    commodity_data["options"] = commodity_data["Symbol"] + " - " + commodity_data["Name"]
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("search_form"):
            commodity_filter = st.selectbox(
                label = f"Commodity",
                placeholder = "Commodity",
                options = sorted(commodity_data["options"]),
                key = "Commodity_filter"
            )
            commodity = commodity_data[commodity_data["options"] == commodity_filter]["Symbol"].tolist()[0]
            long_name = commodity_data[commodity_data["Symbol"] == commodity]["Name"].tolist()[0]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            if page_title == "COELHO Finance - UNISTATS":
                interval_filter = "1 day"
            else:
                interval_filter = st.selectbox(
                    label = "Interval",
                    placeholder = "Interval",
                    options = periods_and_intervals[1]["interval"],
                    index = 8,
                    key = "interval_filter"
                )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
            try:
                interval_filter = st.session_state["interval_filter"]
            except:
                pass
    return (
        commodity,
        period_filter,
        interval_filter,
        commodity_filter,
        long_name,
    )

def funds_filter_func(
    periods_and_intervals,
    page_title,
    filter_bar):
    funds_data = investpy.funds.get_funds()
    funds_data["options"] = funds_data["symbol"] + " - " + funds_data["name"]
    funds_data["country"] = funds_data["country"].str.upper()
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("market_form"):
            market_filter = st.selectbox(
                label = "Market",
                placeholder = "Market",
                options = sorted(funds_data["country"].unique()),
                key = "market_filter"
            )
            market_button = st.form_submit_button(
                label = "Select market",
                use_container_width = True
            )
            if market_button:
                market_filter = st.session_state["market_filter"]
        with st.form("search_form"):
            funds_options = funds_data[
                funds_data["country"] == market_filter]["options"]
            fund_filter = st.selectbox(
                label = f"Fund ({market_filter})",
                placeholder = "Fund",
                options = sorted(funds_options),
                key = "fund_filter"
            )
            fund = funds_data[funds_data["options"] == fund_filter]["symbol"].tolist()[0]
            exchange = funds_data[funds_data["options"] == fund_filter]["symbol"].tolist()[0]
            currency = funds_data[funds_data["options"] == fund_filter]["currency"].tolist()[0]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            if page_title == "COELHO Finance - UNISTATS":
                interval_filter = "1 day"
            else:
                interval_filter = st.selectbox(
                    label = "Interval",
                    placeholder = "Interval",
                    options = periods_and_intervals[1]["interval"],
                    index = 8,
                    key = "interval_filter"
                )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
            try:
                interval_filter = st.session_state["interval_filter"]
            except:
                pass
    return (
        fund,
        period_filter,
        interval_filter,
        fund_filter,
        exchange,
        currency
    )

def etfs_filter_func(
    periods_and_intervals,
    page_title,
    filter_bar):
    etf_data = investpy.etfs.get_etfs()
    etf_data["options"] = etf_data["symbol"] + " - " + etf_data["name"]
    etf_data["country"] = etf_data["country"].str.upper()
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("market_form"):
            market_filter = st.selectbox(
                label = "Market",
                placeholder = "Market",
                options = sorted(etf_data["country"].unique()),
                key = "market_filter"
            )
            market_button = st.form_submit_button(
                label = "Select market",
                use_container_width = True
            )
            if market_button:
                market_filter = st.session_state["market_filter"]
        with st.form("search_form"):
            etf_options = etf_data[
                etf_data["country"] == market_filter]["options"]
            etf_filter = st.selectbox(
                label = f"ETFs ({market_filter})",
                placeholder = "ETFs",
                options = sorted(etf_options),
                key = "etf_filter"
            )
            etf = etf_data[etf_data["options"] == etf_filter]["symbol"].tolist()[0]
            exchange = etf_data[etf_data["options"] == etf_filter]["symbol"].tolist()[0]
            currency = etf_data[etf_data["options"] == etf_filter]["currency"].tolist()[0]
            long_name = etf_data[etf_data["symbol"] == etf]["full_name"].tolist()[0]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            if page_title == "COELHO Finance - UNISTATS":
                interval_filter = "1 day"
            else:
                interval_filter = st.selectbox(
                    label = "Interval",
                    placeholder = "Interval",
                    options = periods_and_intervals[1]["interval"],
                    index = 8,
                    key = "interval_filter"
                )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
            try:
                interval_filter = st.session_state["interval_filter"]
            except:
                pass
    return (
        etf,
        period_filter,
        interval_filter,
        etf_filter,
        exchange,
        long_name,
        currency
    )

def currency_crosses_filter_func(
    periods_and_intervals,
    page_title,
    filter_bar):
    cc_data = investpy.currency_crosses.get_currency_crosses()
    cc_data["symbol_yf"] = cc_data["base"] + cc_data["second"] + "=X"
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("search_form"):
            cc_options = cc_data["full_name"].unique()
            cc_filter = st.selectbox(
                label = f"Currency Cross",
                placeholder = "Currency Cross",
                options = sorted(cc_options),
                key = "index_filter"
            )
            cc = cc_data[cc_data["full_name"] == cc_filter]["symbol_yf"].tolist()[0]
            currency = cc_data[cc_data["full_name"] == cc_filter]["name"].tolist()[0]
            long_name = cc_data[cc_data["full_name"] == cc_filter]["full_name"].tolist()[0]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            if page_title == "COELHO Finance - UNISTATS":
                interval_filter = "1 day"
            else:
                interval_filter = st.selectbox(
                    label = "Interval",
                    placeholder = "Interval",
                    options = periods_and_intervals[1]["interval"],
                    index = 8,
                    key = "interval_filter"
                )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
            try:
                interval_filter = st.session_state["interval_filter"]
            except:
                pass
    return (
        cc,
        period_filter,
        interval_filter,
        cc_filter,
        long_name,
        currency
    )

def cryptos_filter_func(
    periods_and_intervals,
    page_title,
    filter_bar):
    crypto_data = investpy.crypto.get_cryptos()
    crypto_data["options"] = crypto_data["symbol"] + " - " + crypto_data["name"]
    crypto_data["symbol_yf"] = crypto_data["symbol"] + "-" + crypto_data["currency"]
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("search_form"):
            crypto_filter = st.selectbox(
                label = f"Cryptocurrency",
                placeholder = "Cryptocurrency",
                options = sorted(crypto_data["options"].unique()),
                key = "crypto_filter"
            )
            crypto = crypto_data[crypto_data["options"] == crypto_filter]["symbol_yf"].tolist()[0]
            currency = crypto_data[crypto_data["options"] == crypto_filter]["currency"].tolist()[0]
            long_name = crypto_data[crypto_data["symbol_yf"] == crypto]["name"].tolist()[0]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            if page_title == "COELHO Finance - UNISTATS":
                interval_filter = "1 day"
            else:
                interval_filter = st.selectbox(
                    label = "Interval",
                    placeholder = "Interval",
                    options = periods_and_intervals[1]["interval"],
                    index = 8,
                    key = "interval_filter"
                )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
            try:
                interval_filter = st.session_state["interval_filter"]
            except:
                pass
    return (
        crypto,
        period_filter,
        interval_filter,
        crypto_filter,
        long_name,
        currency
    )

def stocks_filter_func2(
    periods_and_intervals,
    filter_bar):
    with filter_bar.form("market_form2"):
        market_filter = st.selectbox(
            label = "Market",
            placeholder = "Market",
            options = sorted([
                market["market"].upper()
                for market 
                in json.load(open("./data/market_list.json", "r"))]),
            key = "market_filter2"
        )
        market_button = st.form_submit_button(
            label = "Select market",
            use_container_width = True
        )
        if market_button:
            market_filter = st.session_state["market_filter2"]
    with filter_bar.form("search_form2"):
        market_data_yf = pd.json_normalize(
                json.load(open(f"./data/symbols/{market_filter.lower()}.json", "r")))\
                    .sort_values(by = "symbol")\
                    .reset_index(drop = True)
        market_data_yf["options"] = market_data_yf["symbol"] + " - " + market_data_yf["longName"] + " (" + market_data_yf["shortName"] + ")"
        element_filter = st.multiselect(
            label = f"Stock ({market_filter})",
            placeholder = "Stock",
            options = market_data_yf["options"][
                market_data_yf["options"].notnull()],
            key = "stock_filter2"
        )
        feature_filter = st.selectbox(
            label = "Feature",
            options = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ],
            index = 3,
            key = "feature_filter2")
        element = market_data_yf[market_data_yf["options"].isin(element_filter)]["symbol"]
        exchange = market_data_yf[market_data_yf["options"].isin(element_filter)]["exchange"]
        quote_type = market_data_yf[market_data_yf["options"].isin(element_filter)]["quoteType"]
        short_name = market_data_yf[market_data_yf["options"].isin(element_filter)]["shortName"]
        long_name = market_data_yf[market_data_yf["options"].isin(element_filter)]["longName"]
        period_filter = st.selectbox(
            label = "Period",
            placeholder = "Period",
            options = periods_and_intervals[0]["period"],
            index = 5,
            key = "period_filter2"
        )
        interval_filter = st.selectbox(
            label = "Interval",
            placeholder = "Interval",
            options = periods_and_intervals[1]["interval"],
            index = 8,
            key = "interval_filter2"
        )
        search_button = st.form_submit_button(
            label = "Search",
            use_container_width = True
        )
        if search_button:
            period_filter = st.session_state["period_filter2"]
            interval_filter = st.session_state["interval_filter2"]
        return (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            quote_type,
            long_name,
            short_name,
            feature_filter
        )
    
def indices_filter_func2(
    periods_and_intervals,
    filter_bar):
    index_data = investpy.indices.get_indices()
    index_data["options"] = index_data["symbol"] + " - " + index_data["name"]
    index_data["country"] = index_data["country"].str.upper()
    index_data["symbol_yf"] = "^" + index_data["symbol"]
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("market_form"):
            market_filter = st.multiselect(
                label = "Market",
                placeholder = "Market",
                options = sorted(index_data["country"].unique()),
                #index = 91,
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
                index_data["country"].isin(market_filter)]["options"]
            index_filter = st.multiselect(
                label = f"Index",
                placeholder = "Index",
                options = sorted(index_options),
                #index = 1059,
                key = "index_filter"
            )
            feature_filter = st.selectbox(
                label = "Feature",
                options = [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume"
                ],
            index = 3,
            key = "feature_filter2")
            index = index_data[index_data["options"].isin(index_filter)]["symbol_yf"]
            exchange = index_data[index_data["options"].isin(index_filter)]["symbol"]
            currency = index_data[index_data["options"].isin(index_filter)]["currency"]
            long_name = index_data[index_data["symbol_yf"].isin(index)]["full_name"]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            interval_filter = st.selectbox(
                label = "Interval",
                placeholder = "Interval",
                options = periods_and_intervals[1]["interval"],
                index = 8,
                key = "interval_filter"
            )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
                interval_filter = st.session_state["interval_filter"]
    return (
        index,
        period_filter,
        interval_filter,
        index_filter,
        exchange,
        long_name,
        currency,
        feature_filter
    )

def cryptos_filter_func2(
    periods_and_intervals,
    filter_bar):
    crypto_data = investpy.crypto.get_cryptos()
    crypto_data["options"] = crypto_data["symbol"] + " - " + crypto_data["name"]
    crypto_data["symbol_yf"] = crypto_data["symbol"] + "-" + crypto_data["currency"]
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("search_form"):
            crypto_filter = st.multiselect(
                label = f"Cryptocurrency",
                placeholder = "Cryptocurrency",
                options = sorted(crypto_data["options"].unique()),
                key = "crypto_filter"
            )
            feature_filter = st.selectbox(
                label = "Feature",
                options = [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume"
                ],
            index = 3,
            key = "feature_filter2")
            crypto = crypto_data[crypto_data["options"].isin(crypto_filter)]["symbol_yf"]
            currency = crypto_data[crypto_data["options"].isin(crypto_filter)]["currency"]
            long_name = crypto_data[crypto_data["symbol_yf"].isin(crypto)]["name"]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            interval_filter = st.selectbox(
                label = "Interval",
                placeholder = "Interval",
                options = periods_and_intervals[1]["interval"],
                index = 8,
                key = "interval_filter"
            )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
                interval_filter = st.session_state["interval_filter"]
    return (
        crypto,
        period_filter,
        interval_filter,
        crypto_filter,
        long_name,
        currency,
        feature_filter
    )

def currency_crosses_filter_func2(
    periods_and_intervals,
    filter_bar):
    cc_data = investpy.currency_crosses.get_currency_crosses()
    cc_data["symbol_yf"] = cc_data["base"] + cc_data["second"] + "=X"
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("search_form"):
            cc_options = cc_data["full_name"].unique()
            cc_filter = st.multiselect(
                label = f"Currency Cross",
                placeholder = "Currency Cross",
                options = sorted(cc_options),
                key = "index_filter"
            )
            feature_filter = st.selectbox(
                label = "Feature",
                options = [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume"
                ],
            index = 3,
            key = "feature_filter2")
            cc = cc_data[cc_data["full_name"].isin(cc_filter)]["symbol_yf"]
            currency = cc_data[cc_data["full_name"].isin(cc_filter)]["name"]
            long_name = cc_data[cc_data["full_name"].isin(cc_filter)]["full_name"]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            interval_filter = st.selectbox(
                label = "Interval",
                placeholder = "Interval",
                options = periods_and_intervals[1]["interval"],
                index = 8,
                key = "interval_filter"
            )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
                interval_filter = st.session_state["interval_filter"]
    return (
        cc,
        period_filter,
        interval_filter,
        cc_filter,
        long_name,
        currency,
        feature_filter
    )

def funds_filter_func2(
    periods_and_intervals,
    filter_bar):
    funds_data = investpy.funds.get_funds()
    funds_data["options"] = funds_data["symbol"] + " - " + funds_data["name"]
    funds_data["country"] = funds_data["country"].str.upper()
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("market_form"):
            market_filter = st.selectbox(
                label = "Market",
                placeholder = "Market",
                options = sorted(funds_data["country"].unique()),
                index = 58,
                key = "market_filter"
            )
            market_button = st.form_submit_button(
                label = "Select market",
                use_container_width = True
            )
            if market_button:
                market_filter = st.session_state["market_filter"]
        with st.form("search_form"):
            funds_options = funds_data[
                funds_data["country"] == market_filter]["options"]
            fund_filter = st.multiselect(
                label = f"Fund ({market_filter})",
                placeholder = "Fund",
                options = sorted(funds_options),
                key = "fund_filter"
            )
            feature_filter = st.selectbox(
                label = "Feature",
                options = [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume"
                ],
            index = 3,
            key = "feature_filter2")
            fund = funds_data[funds_data["options"].isin(fund_filter)]["symbol"]
            exchange = funds_data[funds_data["options"].isin(fund_filter)]["symbol"]
            currency = funds_data[funds_data["options"].isin(fund_filter)]["currency"]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            interval_filter = st.selectbox(
                label = "Interval",
                placeholder = "Interval",
                options = periods_and_intervals[1]["interval"],
                index = 8,
                key = "interval_filter"
            )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
                interval_filter = st.session_state["interval_filter"]
    return (
        fund,
        period_filter,
        interval_filter,
        fund_filter,
        exchange,
        currency,
        feature_filter
    )

def etfs_filter_func2(
    periods_and_intervals,
    filter_bar):
    etf_data = investpy.etfs.get_etfs()
    etf_data["options"] = etf_data["symbol"] + " - " + etf_data["name"]
    etf_data["country"] = etf_data["country"].str.upper()
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("market_form"):
            market_filter = st.selectbox(
                label = "Market",
                placeholder = "Market",
                options = sorted(etf_data["country"].unique()),
                index = 47,
                key = "market_filter"
            )
            market_button = st.form_submit_button(
                label = "Select market",
                use_container_width = True
            )
            if market_button:
                market_filter = st.session_state["market_filter"]
        with st.form("search_form"):
            etf_options = etf_data[
                etf_data["country"] == market_filter]["options"]
            etf_filter = st.multiselect(
                label = f"ETFs ({market_filter})",
                placeholder = "ETFs",
                options = sorted(etf_options),
                key = "etf_filter"
            )
            feature_filter = st.selectbox(
                label = "Feature",
                options = [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume"
                ],
            index = 3,
            key = "feature_filter2")
            etf = etf_data[etf_data["options"].isin(etf_filter)]["symbol"]
            exchange = etf_data[etf_data["options"].isin(etf_filter)]["symbol"]
            currency = etf_data[etf_data["options"].isin(etf_filter)]["currency"]
            long_name = etf_data[etf_data["symbol"].isin(etf)]["full_name"]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            interval_filter = st.selectbox(
                label = "Interval",
                placeholder = "Interval",
                options = periods_and_intervals[1]["interval"],
                index = 8,
                key = "interval_filter"
            )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
                interval_filter = st.session_state["interval_filter"]
    return (
        etf,
        period_filter,
        interval_filter,
        etf_filter,
        exchange,
        long_name,
        currency,
        feature_filter
    )

def bonds_filter_func2(
    periods_and_intervals,
    filter_bar):
    bond_data = pd.read_json("./data/bonds.json")
    bond_data["options"] = bond_data["Symbol"] + " - " + bond_data["Name"]
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("search_form"):
            bond_filter = st.multiselect(
                label = f"Index",
                placeholder = "Index",
                options = sorted(bond_data["options"]),
                key = "bond_filter"
            )
            feature_filter = st.selectbox(
                label = "Feature",
                options = [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume"
                ],
            index = 3,
            key = "feature_filter2")
            bond = bond_data[bond_data["options"].isin(bond_filter)]["Symbol"]
            long_name = bond_data[bond_data["Symbol"].isin(bond)]["Name"]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            interval_filter = st.selectbox(
                label = "Interval",
                placeholder = "Interval",
                options = periods_and_intervals[1]["interval"],
                index = 8,
                key = "interval_filter"
            )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
                interval_filter = st.session_state["interval_filter"]
    return (
        bond,
        period_filter,
        interval_filter,
        bond_filter,
        long_name,
        feature_filter
    )

def commodities_filter_func2(
    periods_and_intervals,
    filter_bar):
    commodity_data = pd.read_json("./data/commodities.json")
    commodity_data["options"] = commodity_data["Symbol"] + " - " + commodity_data["Name"]
    with filter_bar.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("search_form"):
            commodity_filter = st.multiselect(
                label = f"Commodity",
                placeholder = "Commodity",
                options = sorted(commodity_data["options"]),
                key = "Commodity_filter"
            )
            feature_filter = st.selectbox(
                label = "Feature",
                options = [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume"
                ],
            index = 3,
            key = "feature_filter2")
            commodity = commodity_data[commodity_data["options"].isin(commodity_filter)]["Symbol"]
            long_name = commodity_data[commodity_data["Symbol"].isin(commodity)]["Name"]
            period_filter = st.selectbox(
                label = "Period",
                placeholder = "Period",
                options = periods_and_intervals[0]["period"],
                index = 5,
                key = "period_filter"
            )
            interval_filter = st.selectbox(
                label = "Interval",
                placeholder = "Interval",
                options = periods_and_intervals[1]["interval"],
                index = 8,
                key = "interval_filter"
            )
            search_button = st.form_submit_button(
                label = "Search",
                use_container_width = True
            )
            if search_button:
                period_filter = st.session_state["period_filter"]
                interval_filter = st.session_state["interval_filter"]
    return (
        commodity,
        period_filter,
        interval_filter,
        commodity_filter,
        long_name,
        feature_filter
    )

def binance_filter_func(filter_bar, _binance_symbols):
    with filter_bar.expander(
        label = "Cryptocurrencies",
        expanded = True
    ):
        symbol = st.selectbox(
            label = "Symbol",
            options = _binance_symbols,
            index = _binance_symbols.index("BTCUSDT"),
            key = "symbol1")
        feature = st.selectbox(
            label = "Feature",
            options = [
                'Open', 
                'High', 
                'Low', 
                'Close', 
                'Volume'],
            index = 3
        )
        start_date = st.date_input(
            label = "Start date",
            value = dt.datetime.now() - relativedelta(years = 1),
            min_value = dt.datetime.now() - relativedelta(years = 10),
            max_value = dt.datetime.now()
        )
        start_hour = st.time_input(
            label = "Start hour",
            value = dt.time(00, 00)
        )
        end_date = st.date_input(
            label = "End date",
            value = dt.datetime.now(),
            min_value = start_date,
            max_value = dt.datetime.now()
        )
        end_hour = st.time_input(
            label = "End hour",
            value = dt.time(00, 00)
        )
        return (
            symbol,
            start_date,
            start_hour,
            end_date,
            end_hour,
            feature,
        )
    
def ccxt_filter_func(filter_bar, _ccxt_symbols):
    with filter_bar.expander(
        label = "Cryptocurrencies",
        expanded = True
    ):
        symbol = st.selectbox(
            label = "Symbol",
            options = _ccxt_symbols,
            index = _ccxt_symbols.index("BTC/USDT:USDT"),
            key = "symbol1")
        feature = st.selectbox(
            label = "Feature",
            options = [
                'Open', 
                'High', 
                'Low', 
                'Close', 
                'Volume'],
            index = 3
        )
        start_date = st.date_input(
            label = "Start date",
            value = dt.datetime.now() - relativedelta(years = 1),
            min_value = dt.datetime.now() - relativedelta(years = 10),
            max_value = dt.datetime.now()
        )
        start_hour = st.time_input(
            label = "Start hour",
            value = dt.time(00, 00)
        )
        end_date = st.date_input(
            label = "End date",
            value = dt.datetime.now(),
            min_value = start_date,
            max_value = dt.datetime.now()
        )
        end_hour = st.time_input(
            label = "End hour",
            value = dt.time(00, 00)
        )
        return (
            symbol,
            start_date,
            start_hour,
            end_date,
            end_hour,
            feature,
        )
    
@st.cache_resource
def get_binance_data(
    symbol,
    start_date,
    start_hour,
    end_date,
    end_hour,
):
    data = vbt.BinanceData.download(
        symbols = symbol,
        start = f'{start_date} {start_hour} UTC',
        end = f'{end_date} {end_hour} UTC',
        interval = "1d"
    )
    return data

@st.cache_resource
def get_ccxt_data(
    symbol,
    start_date,
    start_hour,
    end_date,
    end_hour,
):
    data = vbt.CCXTData.download(
        symbols = symbol,
        start = f'{start_date} {start_hour} UTC',
        end = f'{end_date} {end_hour} UTC',
    )
    return data
    
@st.cache_resource
def binance_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    data = requests.get(url).json()
    symbols = [symbol['symbol'] for symbol in data['symbols']]
    return symbols

@st.cache_resource
def ccxt_symbols():
    exchange_id = 'binance'
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
    markets = exchange.load_markets()
    symbols = list(markets.keys())  # Gets all available symbols/pairs
    return symbols

@st.cache_resource
def simulate_gbm(s_0, mu, sigma, n_sims, T, N, random_seed = 42):
    np.random.seed(random_seed)
    dt = T / N
    dW = np.random.normal(scale = np.sqrt(dt), size = (n_sims, N))
    W = np.cumsum(dW, axis = 1)
    time_step = np.linspace(dt, T, N)
    time_steps = np.broadcast_to(time_step, (n_sims, N))
    S_t = s_0 * np.exp((mu - 0.5 * sigma ** 2) * time_steps + sigma * W)
    S_t = np.insert(S_t, 0, s_0, axis = 1)
    return S_t

@st.cache_data
def efficient_frontier(multidata_yf, element, feature_filter):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    N_PORTFOLIOS = 10 ** 5
    N_DAYS = 252
    n_assets = len(element)
    returns_df = multidata_yf[feature_filter].pct_change().dropna()
    #annualized returns
    avg_returns = returns_df.mean() * N_DAYS
    cov_mat = returns_df.cov() * N_DAYS
    #portfolio weights
    np.random.seed(42)
    weights = np.random.random(size = (N_PORTFOLIOS, n_assets))
    weights /= np.sum(weights, axis = 1)[:, np.newaxis]
    #portfolio metrics
    portf_rtns = np.dot(weights, avg_returns)
    portf_vol = []
    for i in range(0, len(weights)):
        vol = np.sqrt(
            np.dot(
                weights[i].T,
                np.dot(cov_mat, weights[i])
            )
        )
        portf_vol.append(vol)
    portf_vol = np.array(portf_vol)
    portf_sharpe_ratio = portf_rtns / portf_vol
    portf_results_df = pd.DataFrame(
        {
            "returns": portf_rtns,
            "volatility": portf_vol,
            "sharpe_ratio": portf_sharpe_ratio
        }
    )
    N_POINTS = 100
    ef_rtn_list, ef_vol_list = [], []
    possible_ef_rtns = np.linspace(
        portf_results_df["returns"].min(),
        portf_results_df["returns"].max(),
        N_POINTS
    )
    #locate the points creating the efficient frontier
    possible_ef_rtns = np.round(possible_ef_rtns, 2)
    portf_rtns = np.round(portf_rtns, 2)
    for rtn in possible_ef_rtns:
        if rtn in portf_rtns:
            ef_rtn_list.append(rtn)
            matched_ind = np.where(portf_rtns == rtn)
            ef_vol_list.append(
                np.min(
                    portf_vol[matched_ind]
                )
            )
    #plot the efficient frontier
    fig, ax = plt.subplots()
    portf_results_df.plot(
        kind = "scatter", 
        x = "volatility",
        y = "returns", 
        c = "sharpe_ratio",
        cmap = "RdYlGn", 
        edgecolors = "black",
        ax = ax)
    ax.set(
        xlabel = "Volatility",
        ylabel = "Expected Returns",
        title = "Efficient Frontier")
    ax.plot(ef_vol_list, ef_rtn_list, "b--")

    for asset_index in range(n_assets):
        ax.scatter(
            x = np.sqrt(cov_mat.iloc[asset_index, asset_index]),
            y = avg_returns[asset_index],
            marker = list(Line2D.markers.keys())[asset_index],
            s = 150, 
            color = "black",
            label = element.reset_index(drop = True).iloc[asset_index])
    ax.legend()
    return ax.figure

@st.cache_data
def efficient_frontier2(
    multidata_yf,
    feature_filter,
    element
):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    N_DAYS = 252
    n_assets = len(element)
    returns_df = multidata_yf[feature_filter].pct_change().dropna()
    avg_returns = returns_df.mean() * N_DAYS
    avg_returns = avg_returns.values
    cov_mat = returns_df.cov() * N_DAYS
    cov_mat = cov_mat.values
    #optimization
    weights = cp.Variable(n_assets)
    gamma_par = cp.Parameter(nonneg = True)
    portf_rtn_cvx = avg_returns @ weights
    portf_vol_cvx = cp.quad_form(weights, cov_mat)
    objective_function = cp.Maximize(
        portf_rtn_cvx - gamma_par * portf_vol_cvx
    )
    problem = cp.Problem(
        objective_function,
        [cp.sum(weights) == 1, weights >= 0]
    )
    #efficient frontier
    N_POINTS = 25
    portf_rtn_cvx_ef, portf_vol_cvx_ef, weights_ef = [], [], []
    gamma_range = np.logspace(-3, 3, num = N_POINTS)
    for gamma in gamma_range:
        gamma_par.value = gamma
        problem.solve()
        portf_vol_cvx_ef.append(cp.sqrt(portf_vol_cvx).value)
        portf_rtn_cvx_ef.append(portf_rtn_cvx.value)
        weights_ef.append(weights.value)
    #risk aversion allocations plot
    weights_df = pd.DataFrame(weights_ef, columns = element, index = np.round(gamma_range, 3))
    ax1 = weights_df.plot(kind = "bar", stacked = True)
    ax1.set(
        title = "Weights allocation per risk-aversion level",
        xlabel = "$\\gamma$",
        ylabel = "weight"
    )
    ax1.legend(bbox_to_anchor = (1, 1))
    #efficient frontier plot
    fig, ax2 = plt.subplots()
    ax2.plot(portf_vol_cvx_ef, portf_rtn_cvx_ef, "g-")
    for asset_index in range(n_assets):
        plt.scatter(
            x = np.sqrt(cov_mat[asset_index, asset_index]),
            y = avg_returns[asset_index],
            marker = list(Line2D.markers.keys())[asset_index],
            label = element.reset_index(drop = True).iloc[asset_index],
            s = 150
        )
    ax2.set(
        title = "Efficient Frontier",
        xlabel = "Volatility",
        ylabel = "Expected Returns"
    )
    ax2.legend()
    return ax1.figure, ax2.figure

@st.cache_data
def conditional_correlation_matrix(returns, element_filter):
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
    fig = px.imshow(
        H,
        text_auto = True,
        aspect = "auto",
        color_continuous_scale = "RdBu_r")
    return fig

def image_border_radius(image_path, border_radius, width, height, page_object = None, is_html = False):
    if is_html == False:
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()
        # Create HTML string with the image
        img_html = f'<img src="data:image/jpeg;base64,{img_base64}" style="border-radius: {border_radius}px; width: {width}%; height: {height}%">'
        # Display the HTML string in Streamlit
        if page_object == None:
            st.markdown(img_html, unsafe_allow_html=True)
        else:
            page_object.markdown(img_html, unsafe_allow_html=True)
    else:
        # Create HTML string with the image
        img_html = f'<img src="{image_path}" style="border-radius: {border_radius}px; width: 300px;">'
        # Display the HTML string in Streamlit
        if page_object == None:
            st.markdown(img_html, unsafe_allow_html=True)
        else:
            page_object.markdown(img_html, unsafe_allow_html=True)

def create_scrollable_section(content, height="400px"):
    # Defining the HTML and CSS
    scrollable_section_html = f"""
    <div style="
        overflow-y: scroll;
        height: {height};
        border: 1px solid #ccc;
        padding: 10px;
        margin: 10px 0;
        ">
        {content}
    </div>
    """
    return scrollable_section_html    

def page_buttons():
    grid_ = grid(6, vertical_align = True)
    HOME = grid_.button(
        label = "$$\\textbf{Home}$$",
        use_container_width = True)
    UNIMARKET = grid_.button(
        label = "$$\\textbf{UNIMARKET}$$",
        use_container_width = True)
    UNISTATS = grid_.button(
        label = "$$\\textbf{UNISTATS}$$",
        use_container_width = True)
    MULTIMARKET = grid_.button(
        "$$\\textbf{MULTIMARKET}$$",
        use_container_width = True)
    BACKTESTING = grid_.button(
        "$$\\textbf{Backtesting}$$",
        use_container_width = True)
    ABOUT_US = grid_.button(
        "$$\\textbf{About Us}$$",
        use_container_width = True)
    if HOME:
        switch_page("coelho finance")
    if UNIMARKET:
        switch_page("UNIMARKET")
    if UNISTATS:
        switch_page("UNISTATS")
    if MULTIMARKET:
        switch_page("MULTIMARKET")  
    if BACKTESTING:
        switch_page("Backtesting")  
    if ABOUT_US:
        switch_page("About Us")
    st.divider()  


#BACKTESTING FUNCTIONS
def get_expectancy(total_return_by_type, level_name, init_cash):
    grouped = total_return_by_type.groupby(level_name, axis=0)
    win_rate = grouped.apply(lambda x: (x > 0).mean())
    avg_win = grouped.apply(lambda x: init_cash * x[x > 0].mean()).fillna(0)
    avg_loss = grouped.apply(lambda x: init_cash * x[x < 0].mean()).fillna(0)
    return win_rate * avg_win - (1 - win_rate) * np.abs(avg_loss)

def bin_return(total_return_by_type, bins):
    classes = pd.cut(total_return_by_type['Holding'], bins=bins, right=True)
    new_level = pd.Index(np.array(classes.apply(lambda x: x.right)), name='bin_right')
    return total_return_by_type.vbt.stack_index(new_level, axis=0)

def roll_in_and_out_samples(price, **kwargs):
    return price.vbt.rolling_split(**kwargs)

def simulate_holding(price, **kwargs):
    pf = vbt.Portfolio.from_holding(price, **kwargs)
    return pf.sharpe_ratio()

def simulate_all_params(price, windows, **kwargs):
    fast_ma, slow_ma = vbt.MA.run_combs(price, windows, r=2, short_names=['fast', 'slow'])
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)
    pf = vbt.Portfolio.from_signals(price, entries, exits, **kwargs)
    return pf.sharpe_ratio()

def get_best_index(performance, higher_better=True):
    if higher_better:
        return performance[performance.groupby('split_idx').idxmax()].index
    return performance[performance.groupby('split_idx').idxmin()].index

def get_best_params(best_index, level_name):
    return best_index.get_level_values(level_name).to_numpy()

def simulate_best_params(price, best_fast_windows, best_slow_windows, **kwargs):
    fast_ma = vbt.MA.run(price, window=best_fast_windows, per_column=True)
    slow_ma = vbt.MA.run(price, window=best_slow_windows, per_column=True)
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)
    pf = vbt.Portfolio.from_signals(price, entries, exits, **kwargs)
    return pf.sharpe_ratio()