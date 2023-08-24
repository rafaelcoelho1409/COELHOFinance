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

with open("./data/periods_and_intervals.json", "r") as f:
    periods_and_intervals = json.load(f)

with st.sidebar:
    with st.expander(
        "Filters",
        expanded = True
    ):
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
            stock_filter = st.selectbox(
                label = f"Stock ({market_filter})",
                placeholder = "Stock",
                options = market_data_yf["options"][
                    market_data_yf["options"].notnull()],
                key = "stock_filter"
            )
            stock = market_data_yf[market_data_yf["options"] == stock_filter]["symbol"].iloc[0]
            exchange = market_data_yf[market_data_yf["options"] == stock_filter]["exchange"].iloc[0]
            quote_type = market_data_yf[market_data_yf["options"] == stock_filter]["quoteType"].iloc[0]
            short_name = market_data_yf[market_data_yf["options"] == stock_filter]["shortName"].iloc[0]
            long_name = market_data_yf[market_data_yf["options"] == stock_filter]["longName"].iloc[0]
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
                stock = stock
                period_interval = st.session_state["period_filter"]
                interval_filter = st.session_state["interval_filter"]
            

(
    ticker_yf, 
    data_yf) = get_unistock(
        stock, 
        periods_and_intervals[0]["period"][period_filter], 
        periods_and_intervals[1]["interval"][interval_filter],
        "YFinance")
(
    ticker_yq,
    data_yq
) = get_unistock(
    stock,
    periods_and_intervals[0]["period"][period_filter], 
    periods_and_intervals[1]["interval"][interval_filter],
    "YahooQuery")

currency = ticker_yf.info["currency"]

st.write(f"**{stock_filter}**")

main_tabs = st.tabs([
        "UNISTOCK",
        "INFORMATIONS",
        "INDICATORS",
        "COMPANY",
        "NEWS",
        "HOLDERS",
        "DIVIDENDS & SPLITS",
        "FINANCIAL",
        "EARNINGS",
        "SHARES FULL"   
])

with main_tabs[0]: #UNISTOCK TAB
    with st.expander(
        label = "Indicators",
        expanded = True
    ):
        grid1 = grid(3, vertical_align = "center")
        for (key, value) in [
            ("Currency", currency),
            ("Exchange", exchange),
            ("Quote type", quote_type),
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
            x = data_yf.index,
            open = data_yf["Open"],
            high = data_yf["High"],
            low = data_yf["Low"],
            close = data_yf["Close"],
        )
    )
    for x in ["Open", "High", "Low", "Close"]:
        if checkboxes_grid.checkbox(x):
            fig.add_trace(
                go.Scatter(
                    x = data_yf.index,
                    y = data_yf[x],
                    mode = "lines",
                    name = x
                )
            )
    fig2 = px.bar(
        x = data_yf.index,
        y = data_yf["Volume"]
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
            for index, row in data_yf.iterrows()]
    )
    # removing all empty dates
    # build complete timeline from start date to end date
    dt_all = pd.date_range(start = data_yf.index[0], end = data_yf.index[-1])
    # retrieve the dates that ARE in the original datset
    dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(data_yf.index)]
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
    subtab_names = [
        "MAIN INDICATORS",
        "ESG SCORES",
        "GRADING HISTORY",
        "INSTITUTIONAL OWNERSHIP",
        "KEY STATS",
        "PRICE",
        "SEC FILINGS",
        "SHARE PURCHASE ACTIVITY",
        "QUOTES",
        "RECOMMENDATIONS"
    ]
    subtabs = st.tabs(subtab_names)
    with subtabs[0]:
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
        subsubtabs = st.tabs(patterns)
        with subsubtabs[0]:
            general_indicator_metrics(
                stock,
                patterns,
                indicators,
                ticker_yf,
                5,
                "info",
                "YFinance"
            )
        for i, x in enumerate(patterns):
            if i != 0: #NOT THE GENERAL TAB
                with subsubtabs[i]:
                    try:
                        indicator_metrics(
                            stock,
                            x, 
                            indicators, 
                            ticker_yf, 
                            5,
                            "info",
                            "YFinance")
                    except:
                        st.write("No information.")
    with subtabs[1]:
        indicators_num, indicators_str = {}, {}
        for x in ticker_yq.esg_scores[stock].keys():
            if type(ticker_yq.esg_scores[stock][x]) in [int, float]:
                indicator = ''.join(map(
                    lambda y: y 
                    if y.islower() 
                    else " " + y, x)).upper()
                indicators_num[indicator] = x
            elif type(ticker_yq.esg_scores[stock][x]) in [str]:
                indicator = ''.join(map(
                    lambda y: y 
                    if y.islower() 
                    else " " + y, x)).upper()
                indicators_str[indicator] = x
        #METRIC CARDS
        patterns = [
            "GENERAL INDICATORS",
        ]
        st.markdown("# ESG Scores")
        general_indicator_metrics(
            stock,
            patterns,
            indicators_num,
            ticker_yq,
            5,
            "esg_scores",
            "YahooQuery"
        )
    with subtabs[2]:
        st.markdown("# Grading history")
        try:
            st.dataframe(
                ticker_yq.grading_history,
                hide_index = True,
                use_container_width = True)
        except:
            st.write("No informations.")
    with subtabs[3]:
        st.markdown("# Institutional ownership")
        st.dataframe(
            ticker_yq.institution_ownership,
            hide_index = True,
            use_container_width = True)
    with subtabs[4]:
        indicators_num, indicators_str = {}, {}
        for x in ticker_yq.key_stats[stock].keys():
            if type(ticker_yq.key_stats[stock][x]) in [int, float]:
                indicator = ''.join(map(
                    lambda y: y 
                    if y.islower() 
                    else " " + y, x)).upper()
                indicators_num[indicator] = x
            elif type(ticker_yq.key_stats[stock][x]) in [str]:
                indicator = ''.join(map(
                    lambda y: y 
                    if y.islower() 
                    else " " + y, x)).upper()
                indicators_str[indicator] = x
        #METRIC CARDS
        patterns = [
            "GENERAL INDICATORS",
        ]
        st.markdown("# Key stats")
        subsubtabs = st.tabs([
            "MAIN INDICATORS",
            "MAIN INFORMATIONS"
        ])
        with subsubtabs[0]:
            general_indicator_metrics(
                stock,
                patterns,
                indicators_num,
                ticker_yq,
                5,
                "key_stats",
                "YahooQuery"
            )
        with subsubtabs[1]:
            general_indicator_metrics(
                stock,
                patterns,
                indicators_str,
                ticker_yq,
                5,
                "key_stats",
                "YahooQuery"
            )
    with subtabs[5]:
        indicators_num, indicators_str = {}, {}
        for x in ticker_yq.price[stock].keys():
            if type(ticker_yq.price[stock][x]) in [int, float]:
                indicator = ''.join(map(
                    lambda y: y 
                    if y.islower() 
                    else " " + y, x)).upper()
                indicators_num[indicator] = x
            elif type(ticker_yq.price[stock][x]) in [str]:
                indicator = ''.join(map(
                    lambda y: y 
                    if y.islower() 
                    else " " + y, x)).upper()
                indicators_str[indicator] = x
        #METRIC CARDS
        patterns = [
            "GENERAL INDICATORS",
        ]
        st.markdown("# Price")
        subsubtabs = st.tabs([
            "MAIN INDICATORS",
            "MAIN INFORMATIONS"
        ])
        with subsubtabs[0]:
            general_indicator_metrics(
                stock,
                patterns,
                indicators_num,
                ticker_yq,
                5,
                "price",
                "YahooQuery"
            )
        with subsubtabs[1]:
            general_indicator_metrics(
                stock,
                patterns,
                indicators_str,
                ticker_yq,
                5,
                "price",
                "YahooQuery"
            )   
    with subtabs[6]:
        st.markdown("# SEC Filings")
        try:
            st.dataframe(
                ticker_yq.sec_filings,
                hide_index = True,
                use_container_width = True
            )
        except:
            st.write("No informations.")
    with subtabs[7]:
        indicators = {}
        for x in ticker_yq.share_purchase_activity[stock].keys():
            if type(ticker_yq.share_purchase_activity[stock][x]) in [int, float, str]:
                indicator = ''.join(map(
                    lambda y: y 
                    if y.islower() 
                    else " " + y, x)).upper()
                indicators[indicator] = x
        #METRIC CARDS
        patterns = [
            "GENERAL INDICATORS",
        ]
        st.markdown("# Share purchase activity")
        general_indicator_metrics(
            stock,
            patterns,
            indicators,
            ticker_yq,
            5,
            "share_purchase_activity",
            "YahooQuery"
        )
    with subtabs[8]:
        st.markdown("# Quotes")
        try:
            st.write(ticker_yq.quotes)
        except:
            st.write("No informations.")
    with subtabs[9]:
        st.dataframe(
            ticker_yq.recommendations[stock]["recommendedSymbols"],
            use_container_width = True)
with main_tabs[3]: #COMPANY TAB
    tabs = st.tabs([
        "SUMMARY",
        "COMPANY OFFICERS",
    ])
    with tabs[0]:
        st.markdown("# Summary")
        #This method below was made to avoid the company name to stay apart of the rest of the paragraph
        try:
            join_string = False
            for x in ticker_yf.info["longBusinessSummary"].replace(". ", ".. ").split(". "):
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
                ticker_yf.info["companyOfficers"],
                use_container_width = True)
        except:
            st.write("No information.")
with main_tabs[4]: #NEWS TAB
    st.title("Latest News")
    try:
        get_news(ticker_yf.news)
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
                ticker_yf.__getattribute__(list(holders_info.keys())[i]),
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
                st.dataframe(ticker_yf.__getattribute__(attr))
            except:
                st.markdown(f"# {attr.replace('_', ' ').capitalize()}")
                st.dataframe(ticker_yf.__getattribute__(attr)())
with main_tabs[7]: #FINANCIAL TAB
    attrs = [
        "financials",
        "income_stmt",
        "quarterly_income_stmt",
        "quarterly_financials",
        "balance_sheet",
        "quarterly_balance_sheet",
        "cash_flow",
        "quarterly_cash_flow"
        ]
    subtabs = st.tabs([x.replace("_", " ").upper() for x in attrs])
    for i, attr in enumerate(attrs):
        with subtabs[i]:
            st.markdown(f"# {attr.replace('_', ' ').replace('stmt', 'statement').capitalize()}")
            try:
                information = ticker_yf.__getattribute__(attr).transpose()
            except:
                information = ticker_yf.__getattribute__(attr)().transpose()
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
            st.plotly_chart(
                fig,
                use_container_width = True)
with main_tabs[8]: #EARNING DATES TAB
    attrs = [
        "earnings_dates"
        ]
    cols = st.columns(2)
    for i, attr in enumerate(attrs):
        with cols[i]:
            st.markdown(f"# {attr.replace('_', ' ').capitalize()}")
            try:
                information = ticker_yf.__getattribute__(attr).reset_index()
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
                    information = ticker_yf.__getattribute__(attr)().reset_index()
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
with main_tabs[9]: #FULL SHARES TAB
    attrs = [
        "get_shares_full"
        ]
    cols = st.columns(2)
    for i, attr in enumerate(attrs):
        with cols[i]:
            st.markdown(f"# {attr.replace('_', ' ').capitalize()}")
            try:
                information = ticker_yf.__getattribute__(attr).transpose()
                fig = px.bar(
                    information.reset_index(),
                    x = "index",
                    y = 0,
                )
                fig.layout.showlegend = False
                st.plotly_chart(fig)
            except:
                try:
                    information = ticker_yf.__getattribute__(attr)().transpose()
                    fig = px.bar(
                        information.reset_index(),
                        x = "index",
                        y = 0,
                    )
                    fig.layout.showlegend = False
                    st.plotly_chart(fig)
                except:
                    st.write("No information.")
