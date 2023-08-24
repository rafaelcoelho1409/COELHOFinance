import streamlit as st
import json
import datetime as dt
import pandas as pd
import yfinance as yf
import yahooquery as yq
import plotly.graph_objects as go
import plotly.express as px
#STREAMLIT THIRD-PARTY
from streamlit_extras.grid import grid
from streamlit_extras.metric_cards import style_metric_cards
#internal functions
from functions import (
    get_unindex, 
    indicator_metrics,
    general_indicator_metrics,
    get_news,
    option_menu)

st.set_page_config(
    page_title = "COELHO Finance - UNINDEX",
    layout = "wide"
)

option_menu()

st.title("COELHO Finance - UNINDEX")

index_data = pd.json_normalize(
    json.load(open("./data/index_list.json", "r"))
)
index_data["options"] = index_data["indexId"] + " - " + index_data["indexName"]
index_data["market"] = index_data["market"].str.upper()
index_data["indexId"] = "^" + index_data["indexId"]

with st.sidebar:
    with st.form("market_form"):
        market_filter = st.selectbox(
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
            index_data["market"] == market_filter]["options"]
        index_filter = st.selectbox(
            label = f"Index ({market_filter})",
            placeholder = "Index",
            options = sorted(index_options),
            key = "stock_filter"
        )
        index = index_data[index_data["options"] == index_filter]["indexId"].tolist()[0]
        long_name = index_data[index_data["indexId"] == index]["indexName"]
        startdate_filter = st.date_input(
            "Start date",
            dt.datetime.now() - dt.timedelta(days = 90),
            key = "startdate_filter"
        )
        enddate_filter = st.date_input(
            "End date",
            dt.datetime.now(),
            key = "enddate_filter"
        )
        search_button = st.form_submit_button(
            label = "Search",
            use_container_width = True
        )
        if search_button:
            startdate_filter = st.session_state["startdate_filter"]
            enddate_filter = st.session_state["enddate_filter"]
            

(
    ticker_yf, 
    data) = get_unindex(
        index, 
        startdate_filter, 
        enddate_filter)
try:
    currency = ticker_yf.info["currency"]
except:
    pass

ticker_yf.history()

st.write(f"**{index_filter}**")

main_tabs = st.tabs([
        "UNINDEX",
        "INFORMATIONS",
        "INDICATORS",
        "NEWS",
        "HOLDERS"
])

with main_tabs[0]: #STOCK TAB
    with st.expander(
        label = "Indicators",
        expanded = True
    ):
        grid1 = grid(3, vertical_align = "center")
        for (key, value) in [
            ("Currency", currency),
            ("Start date", startdate_filter),
            ("End date", enddate_filter)
            ]:
            try:
                grid1.metric(
                    label = key,
                    value = str(value))
            except:
                pass
        style_metric_cards(
            background_color = "#000000",
    )
    checkboxes_grid = grid(5, vertical_align = True)
    checkboxes_grid.markdown("**OHLC filters**")
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x = data.index,
            open = data["Open"],
            high = data["High"],
            low = data["Low"],
            close = data["Close"],
        )
    )
    for x in ["Open", "High", "Low", "Close"]:
        if checkboxes_grid.checkbox(x):
            fig.add_trace(
                go.Scatter(
                    x = data.index,
                    y = data[x],
                    mode = "lines",
                    name = x
                )
            )
    fig2 = px.bar(
        x = data.index,
        y = data["Volume"]
    )
    fig.update_layout(
        xaxis_rangeslider_visible = False,
        legend = {
            "orientation": "h"
        },
        title = "<b>(OHLC)</b> " + index_filter
    )
    fig2.update_layout(
        height = 200,
        width = 800,
        xaxis_title = None,
        yaxis_title = None,
        title = "Volume",
        showlegend = False
    )
    fig2.update_traces(
        marker_color = [
            '#FF0000' 
            if row['Open'] - row['Close'] >= 0
            else '#00FF00' 
            for index, row in data.iterrows()]
    )
    # removing all empty dates
    # build complete timeline from start date to end date
    dt_all = pd.date_range(start = data.index[0], end = data.index[-1])
    # retrieve the dates that ARE in the original datset
    dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(data.index)]
    # define dates with missing values
    dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]
    fig.update_xaxes(
        rangebreaks=[dict(values=dt_breaks)],
        automargin = False)
    fig2.update_xaxes(
        rangebreaks=[dict(values=dt_breaks)])
    st.plotly_chart(
        fig,
        use_container_width = True)
    st.plotly_chart(
        fig2,
        use_container_width = True)
with main_tabs[1]: #INFORMATIONS TAB
    informations = {}
    for x in ticker_yf.info.keys():
        if (type(ticker_yf.info[x]) in [str]) and (x != "longBusinessSummary"):
            information = ''.join(map(
                lambda y: y 
                if y.islower() 
                else " " + y, x)).upper()
            informations[information] = x
    st.markdown("# Informations")
    info = {}, {}
    items_per_col = len(informations) // 2
    for i, (key, value) in enumerate(informations.items()):
        try:
            info[(i // items_per_col)][key] = value
        except:
            pass
    subcols = st.columns(2)
    for i in range(len(subcols)):
        with subcols[i]:
            info_markdown = "".join(f"- **{key}:** {ticker_yf.info[value]}\n" for key, value in info[i].items())
            st.markdown(info_markdown)
with main_tabs[2]: #INDICATORS TAB
    indicators = {}
    for x in ticker_yf.info.keys():
        if type(ticker_yf.info[x]) in [int, float]:
            indicator = ''.join(map(
                lambda y: y 
                if y.islower() 
                else " " + y, x)).upper()
            indicators[indicator] = x
    st.markdown("# MAIN INDICATORS")
    #METRIC CARDS
    patterns = [
        "GENERAL INDICATORS",
        "RISK",
        "MARKET",
        "DIVIDEND",
        "VOLUME",
        "SHARE",
        "DATE",
        "EPOCH",
        "DAY",
        "PRICE",
        "RATIO",
        "AVERAGE",
        "TRAILING",
        "FORWARD",
        "PERCENT",
        "FISCAL",
        "QUARTER",
        "ENTERPRISE"
    ]
    subtabs = st.tabs(patterns)
    with subtabs[0]:
        general_indicator_metrics(
            patterns,
            indicators,
            ticker_yf,
            5
        )
    for i, x in enumerate(patterns):
        if i != 0: #NOT THE GENERAL TAB
            with subtabs[i]:
                try:
                    indicator_metrics(x, indicators, ticker_yf, 5)
                except:
                    st.write("No information.")
    #-----------------------
with main_tabs[3]: #NEWS TAB
    st.title("Latest News")
    try:
        get_news(ticker_yf.news)
    except:
        st.write("No information.")
with main_tabs[4]: #HOLDERS TAB
    holders_info = {
        "major_holders": "Major holders",
        "institutional_holders": "Institutional holders",
        "mutualfund_holders": "Mutual fund holders"
    }
    tabs = st.tabs(holders_info.values())
    for i, tab in enumerate(tabs):
        with tab:
            st.markdown(f"# {list(holders_info.values())[i]}")
            st.dataframe(
                ticker_yf.__getattribute__(list(holders_info.keys())[i]),
                hide_index = True,
                use_container_width = True)
