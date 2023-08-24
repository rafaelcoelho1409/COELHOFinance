import streamlit as st
import yfinance as yf
import yahooquery as yq
import datetime as dt
import pandas as pd
from streamlit_extras.row import row
from streamlit_extras.metric_cards import style_metric_cards
from st_pages import show_pages, Page, Section, add_indentation

@st.cache_resource
def get_unistock(
    stock, 
    period,
    interval,
    source):
    if source == "YFinance":
        ticker = yf.Ticker(stock)
    elif source == "YahooQuery":
        ticker = yq.Ticker(stock)
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
def get_unindex(
    index, 
    startdate_filter,
    enddate_filter):
    ticker = yf.Ticker(index)
    data = ticker.history(
        start = startdate_filter,
        end = enddate_filter
    )
    return (
        ticker, 
        data)

@st.cache_resource
def get_profile_report(data):
    return data.profile_report()

@st.cache_resource
def get_multistock(stocks, startdate_filter, enddate_filter):
    tickers = yf.Tickers(stocks)
    multidata = tickers.history(
        start = startdate_filter,
        end = enddate_filter
    )
    return tickers, multidata

@st.cache_resource
def get_multindex(indexes, startdate_filter, enddate_filter):
    tickers = yf.Tickers(indexes)
    multidata = tickers.history(
        start = startdate_filter,
        end = enddate_filter
    )
    return tickers, multidata

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
        st.markdown(f"**PUBLISHER:** {x[1]['publisher']}")
        st.markdown(f"**TIME:** {x[1]['providerPublishTime']}")
        try:
            st.markdown(f"**RELATED TICKERS:** {', '.join(y for y in x[1]['relatedTickers'])}")
        except:
            pass
        st.divider()

def option_menu():
    show_pages([
        Page("app.py", "COELHO Finance"),
        Section("Stock Exchange"),
        Page("pages/unistock.py", "UNISTOCK"),
        Page("pages/multistock.py", "MULTISTOCK"),
        Section("Market Index"),
        Page("pages/unindex.py", "UNINDEX"),
        Page("pages/multindex.py", "MULTINDEX"),
        Page("pages/forex.py", "FOREX", in_section = False),
        Page("pages/about.py", "About Us", in_section = False),
    ])

    add_indentation()