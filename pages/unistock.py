import streamlit as st
import json
import re
import datetime as dt
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
#STREAMLIT THIRD-PARTY
from streamlit_extras.grid import grid
from streamlit_extras.metric_cards import style_metric_cards
#internal functions
from functions import (
    get_unistock, 
    indicator_metrics,
    general_indicator_metrics,
    get_news,
    option_menu)

st.set_page_config(
    page_title = "COELHO Finance - UNISTOCK",
    layout = "wide"
)

option_menu()

st.title("COELHO Finance - UNISTOCK")

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
        stock_filter = st.selectbox(
            label = f"Stock ({market_filter})",
            placeholder = "Stock",
            options = market_data["options"][
                market_data["options"].notnull()],
            key = "stock_filter"
        )
        stock = market_data[market_data["options"] == stock_filter]["symbol"].iloc[0]
        exchange = market_data[market_data["options"] == stock_filter]["exchange"].iloc[0]
        quote_type = market_data[market_data["options"] == stock_filter]["quoteType"].iloc[0]
        short_name = market_data[market_data["options"] == stock_filter]["shortName"].iloc[0]
        long_name = market_data[market_data["options"] == stock_filter]["longName"].iloc[0]
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
            #key = "search_button",
            use_container_width = True
        )
        if search_button:
            stock = stock
            startdate_filter = st.session_state["startdate_filter"]
            enddate_filter = st.session_state["enddate_filter"]
            

(
    ticker, 
    data) = get_unistock(
        stock, 
        startdate_filter, 
        enddate_filter)
currency = ticker.info["currency"]

st.write(f"**{stock_filter}**")

main_tabs = st.tabs([
        "UNISTOCK",
        "INFORMATIONS",
        "INDICATORS",
        "SUMMARY",
        "NEWS",
        "HOLDERS",
        "DIVIDENDS & SPLITS",
        "INCOME STATEMENT",
        "FINANCIALS",
        "BALANCE SHEET",
        "CASH FLOW",
        "EARNINGS DATES",
        "SHARES FULL"   
])

with main_tabs[0]: #UNISTOCK TAB
    with st.expander(
        label = "Indicators",
        expanded = True
    ):
        grid1 = grid(5, vertical_align = "center")
        for (key, value) in [
            ("Currency", currency),
            ("Exchange", exchange),
            ("Quote type", quote_type),
            ("Start date", startdate_filter),
            ("End date", enddate_filter)
            ]:
            grid1.metric(
                label = key,
                value = str(value)
            )
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
        title = "<b>(OHLC)</b> " + stock_filter,
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
    for x in ticker.info.keys():
        if (type(ticker.info[x]) in [str]) and (x != "longBusinessSummary"):
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
            info_markdown = "".join(f"- **{key}:** {ticker.info[value]}\n" for key, value in info[i].items())
            st.markdown(info_markdown)
with main_tabs[2]: #INDICATORS TAB
    indicators = {}
    for x in ticker.info.keys():
        if type(ticker.info[x]) in [int, float]:
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
            ticker,
            5
        )
    for i, x in enumerate(patterns):
        if i != 0: #NOT THE GENERAL TAB
            with subtabs[i]:
                try:
                    indicator_metrics(x, indicators, ticker, 5)
                except:
                    st.write("No information.")
    #-----------------------
with main_tabs[3]: #SUMMARY TAB
    tabs = st.tabs([
        "SUMMARY",
        "COMPANY OFFICERS"
    ])
    with tabs[0]:
        st.markdown("# SUMMARY")
        #This method below was made to avoid the company name to stay apart of the rest of the paragraph
        try:
            join_string = False
            for x in ticker.info["longBusinessSummary"].replace(". ", ".. ").split(". "):
                if x == long_name:
                    join_string = True
                    string_to_be_joined = x
                    continue
                if join_string:
                    st.markdown(f"- {string_to_be_joined} {x}")
                    join_string = False
                else:
                    st.markdown(f"- {x}")
        except:
            st.write("No information.")
    with tabs[1]:
        st.markdown("# Company Officers")
        try:
            st.dataframe(
                ticker.info["companyOfficers"],
                use_container_width = True)
        except:
            st.write("No information.")
with main_tabs[4]: #NEWS TAB
    st.title("Latest News")
    try:
        get_news(ticker.news)
    except:
        st.write("No information.")
with main_tabs[5]: #HOLDERS TAB
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
                ticker.__getattribute__(list(holders_info.keys())[i]),
                hide_index = True,
                use_container_width = True)
with main_tabs[6]: #DIV. & SPL. TAB
    attrs = [
        "dividends", 
        "capital_gains", 
        "splits", 
        "actions"
        ]
    subtabs = st.tabs([
        x.replace("_", " ").upper() for x in attrs])
    for i, attr in enumerate(attrs):
        with subtabs[i]:
            try:
                st.markdown(f"# {attr.replace('_', ' ').capitalize()}")
                st.dataframe(ticker.__getattribute__(attr))
            except:
                st.markdown(f"# {attr.replace('_', ' ').capitalize()}")
                st.dataframe(ticker.__getattribute__(attr)())
with main_tabs[7]: #INCOME STATEMENT TAB
    attrs = [
        "income_stmt",
        "quarterly_income_stmt",
        ]
    cols = st.columns(2)
    for i, attr in enumerate(attrs):
        with cols[i]:
            st.markdown(f"# {attr.replace('_', ' ').replace('stmt', 'statement').capitalize()}")
            try:
                information = ticker.__getattribute__(attr).transpose()
            except:
                information = ticker.__getattribute__(attr)().transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = attr
            )
            fig = px.bar(
                information.reset_index(),
                x = "index",
                y = filterbox,
            )
            fig.layout.showlegend = False
            st.plotly_chart(fig)
with main_tabs[8]: #FINANCIALS TAB
    attrs = [
        "financials",
        "quarterly_financials",
        ]
    cols = st.columns(2)
    for i, attr in enumerate(attrs):
        with cols[i]:
            st.markdown(f"# {attr.replace('_', ' ').capitalize()}")
            try:
                information = ticker.__getattribute__(attr).transpose()
            except:
                information = ticker.__getattribute__(attr)().transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = attr
            )
            fig = px.bar(
                information.reset_index(),
                x = "index",
                y = filterbox,
            )
            fig.layout.showlegend = False
            st.plotly_chart(fig)
with main_tabs[9]: #BALANCE SHEET TAB
    attrs = [
        "balance_sheet",
        "quarterly_balance_sheet"
        ]
    cols = st.columns(2)
    for i, attr in enumerate(attrs):
        with cols[i]:
            st.markdown(f"# {attr.replace('_', ' ').replace('stmt', 'statement').capitalize()}")
            try:
                information = ticker.__getattribute__(attr).transpose()
            except:
                information = ticker.__getattribute__(attr)().transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = attr
            )
            fig = px.bar(
                information.reset_index(),
                x = "index",
                y = filterbox,
            )
            fig.layout.showlegend = False
            st.plotly_chart(fig)
with main_tabs[10]: #CASH FLOW TAB
    attrs = [
        "cash_flow",
        "quarterly_cash_flow"
        ]
    cols = st.columns(2)
    for i, attr in enumerate(attrs):
        with cols[i]:
            st.markdown(f"# {attr.replace('_', ' ').capitalize()}")
            try:
                information = ticker.__getattribute__(attr).transpose()
            except:
                information = ticker.__getattribute__(attr)().transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = attr
            )
            fig = px.bar(
                information.reset_index(),
                x = "index",
                y = filterbox,
            )
            fig.layout.showlegend = False
            st.plotly_chart(fig)
with main_tabs[11]: #EARNING DATES TAB
    attrs = [
        "earnings_dates"
        ]
    cols = st.columns(2)
    for i, attr in enumerate(attrs):
        with cols[i]:
            st.markdown(f"# {attr.replace('_', ' ').capitalize()}")
            try:
                information = ticker.__getattribute__(attr).reset_index()
                filterbox = st.selectbox(
                    label = "Feature",
                    options = sorted(information.columns.drop("Earnings Date")),
                    key = attr
                )
                fig = px.bar(
                    information,
                    x = "Earnings Date",
                    y = filterbox,
                )
                fig.layout.showlegend = False
                st.plotly_chart(fig)
            except:
                try:
                    information = ticker.__getattribute__(attr)().reset_index()
                    filterbox = st.selectbox(
                        label = "Feature",
                        options = information.columns.drop("Earnings Date"),
                        key = attr
                    )
                    fig = px.bar(
                        information,
                        x = "Earnings Date",
                        y = filterbox,
                    )
                    fig.layout.showlegend = False
                    st.plotly_chart(fig)
                except:
                    st.write("No information.")
with main_tabs[12]: #FULL SHARES TAB
    attrs = [
        "get_shares_full"
        ]
    cols = st.columns(2)
    for i, attr in enumerate(attrs):
        with cols[i]:
            st.markdown(f"# {attr.replace('_', ' ').capitalize()}")
            try:
                information = ticker.__getattribute__(attr).transpose()
                fig = px.bar(
                    information.reset_index(),
                    x = "index",
                    y = 0,
                )
                fig.layout.showlegend = False
                st.plotly_chart(fig)
            except:
                try:
                    information = ticker.__getattribute__(attr)().transpose()
                    fig = px.bar(
                        information.reset_index(),
                        x = "index",
                        y = 0,
                    )
                    fig.layout.showlegend = False
                    st.plotly_chart(fig)
                except:
                    st.write("No information.")
