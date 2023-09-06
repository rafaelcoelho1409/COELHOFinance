import streamlit as st
import yfinance as yf
import yahooquery as yq
import datetime as dt
import pandas as pd
import json
import investpy
import numpy as np
#ANOMALY DETECTION
from adtk.data import validate_series
from streamlit_extras.row import row
from streamlit_extras.metric_cards import style_metric_cards
from st_pages import show_pages, Page, Section, add_indentation

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
        Section("Market Analytics"),
        Page("pages/unimarket.py", "UNIMARKET"),
        Page("pages/unistats.py", "UNISTATS"),
        Page("pages/multimarket.py", "MULTIMARKET"),
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
    page_title):
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
            index = 15,
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
    page_title):
    index_data = investpy.indices.get_indices()
    index_data["options"] = index_data["symbol"] + " - " + index_data["name"]
    index_data["country"] = index_data["country"].str.upper()
    index_data["symbol_yf"] = "^" + index_data["symbol"]
    with st.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("market_form"):
            market_filter = st.selectbox(
                label = "Market",
                placeholder = "Market",
                options = sorted(index_data["country"].unique()),
                index = 91,
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
                index = 1059,
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
    page_title):
    bond_data = pd.read_json("./data/bonds.json")
    bond_data["options"] = bond_data["Symbol"] + " - " + bond_data["Name"]
    with st.expander(
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
    page_title):
    commodity_data = pd.read_json("./data/commodities.json")
    commodity_data["options"] = commodity_data["Symbol"] + " - " + commodity_data["Name"]
    with st.expander(
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
    page_title):
    funds_data = investpy.funds.get_funds()
    funds_data["options"] = funds_data["symbol"] + " - " + funds_data["name"]
    funds_data["country"] = funds_data["country"].str.upper()
    with st.expander(
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
            fund_filter = st.selectbox(
                label = f"Fund ({market_filter})",
                placeholder = "Fund",
                options = sorted(funds_options),
                index = 12215,
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
    page_title):
    etf_data = investpy.etfs.get_etfs()
    etf_data["options"] = etf_data["symbol"] + " - " + etf_data["name"]
    etf_data["country"] = etf_data["country"].str.upper()
    with st.expander(
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
            etf_filter = st.selectbox(
                label = f"ETFs ({market_filter})",
                placeholder = "ETFs",
                options = sorted(etf_options),
                index = 1776,
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
    page_title):
    cc_data = investpy.currency_crosses.get_currency_crosses()
    cc_data["symbol_yf"] = cc_data["base"] + cc_data["second"] + "=X"
    with st.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("search_form"):
            cc_options = cc_data["full_name"].unique()
            cc_filter = st.selectbox(
                label = f"Currency Cross",
                placeholder = "Currency Cross",
                options = sorted(cc_options),
                index = 1760,
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
    page_title):
    crypto_data = investpy.crypto.get_cryptos()
    crypto_data["options"] = crypto_data["symbol"] + " - " + crypto_data["name"]
    crypto_data["symbol_yf"] = crypto_data["symbol"] + "-" + crypto_data["currency"]
    with st.expander(
        label = "Market",
        expanded = True
    ):
        with st.form("search_form"):
            crypto_filter = st.selectbox(
                label = f"Cryptocurrency",
                placeholder = "Cryptocurrency",
                options = sorted(crypto_data["options"].unique()),
                index = 130,
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

def stocks_filter_func2(periods_and_intervals):
    with st.form("market_form2"):
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
    with st.form("search_form2"):
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
    
def indices_filter_func2(periods_and_intervals):
    index_data = investpy.indices.get_indices()
    index_data["options"] = index_data["symbol"] + " - " + index_data["name"]
    index_data["country"] = index_data["country"].str.upper()
    index_data["symbol_yf"] = "^" + index_data["symbol"]
    with st.expander(
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

def cryptos_filter_func2(periods_and_intervals):
    crypto_data = investpy.crypto.get_cryptos()
    crypto_data["options"] = crypto_data["symbol"] + " - " + crypto_data["name"]
    crypto_data["symbol_yf"] = crypto_data["symbol"] + "-" + crypto_data["currency"]
    with st.expander(
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

def currency_crosses_filter_func2(periods_and_intervals):
    cc_data = investpy.currency_crosses.get_currency_crosses()
    cc_data["symbol_yf"] = cc_data["base"] + cc_data["second"] + "=X"
    with st.expander(
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

def funds_filter_func2(periods_and_intervals):
    funds_data = investpy.funds.get_funds()
    funds_data["options"] = funds_data["symbol"] + " - " + funds_data["name"]
    funds_data["country"] = funds_data["country"].str.upper()
    with st.expander(
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

def etfs_filter_func2(periods_and_intervals):
    etf_data = investpy.etfs.get_etfs()
    etf_data["options"] = etf_data["symbol"] + " - " + etf_data["name"]
    etf_data["country"] = etf_data["country"].str.upper()
    with st.expander(
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

def bonds_filter_func2(periods_and_intervals):
    bond_data = pd.read_json("./data/bonds.json")
    bond_data["options"] = bond_data["Symbol"] + " - " + bond_data["Name"]
    with st.expander(
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

def commodities_filter_func2(periods_and_intervals):
    commodity_data = pd.read_json("./data/commodities.json")
    commodity_data["options"] = commodity_data["Symbol"] + " - " + commodity_data["Name"]
    with st.expander(
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




