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
        "FINANCIAL",
        "TECHNICAL INSIGHTS"
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
            try:
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
            except:
                pass
        #METRIC CARDS
        patterns = [
            "GENERAL INDICATORS",
        ]
        st.markdown("# Price")
        subsubtabs = st.tabs([
            "Main Indicators",
            "Main Informations"
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
            informations = {}
            for x in ticker_yq.price[stock].keys():
                information = ''.join(map(
                    lambda y: str(y) 
                    if str(y).islower() 
                    else " " + str(y), str(x))).upper()
                if type(ticker_yq.price[stock][x]) in [str]:
                    informations[information] = x
            st.markdown("# Main informations")
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
                    info_markdown = "".join(f"- **{key}:** {ticker_yq.price[stock][value]}\n" for key, value in info[i].items())
                    st.markdown(info_markdown)
    with subtabs[6]:
        st.markdown("# SEC Filings")
        try:
            sec_filings = ticker_yq.sec_filings.reset_index()
            sec_filings_exhibits = pd.json_normalize(sec_filings["exhibits"])
            sec_filings_final = pd.concat([
                sec_filings.drop("exhibits", axis = 1),
                sec_filings_exhibits
            ], axis = 1)
            st.dataframe(
                sec_filings_final,
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
with main_tabs[5]: #FINANCIAL TAB
    subtab_names = [
        "FINANCIALS",
        "INCOME STATEMENT",
        "BALANCE SHEET",
        "CASH FLOW",
        "HOLDERS",
        "EARNINGS",
        "VALUATION MEASURES",
        "SHARES FULL",
        "DIVIDENDS & SPLITS",
        "TREND",
        "OPTION CHAIN",
        "EVENTS"
    ]
    subtabs_ = st.tabs(subtab_names)
    with subtabs_[0]:
        subsubtabs = st.tabs([
            "Financials",
            "Quarterly Financials",
            "Financial Data"
        ])
        with subsubtabs[0]:
            st.markdown("# Financials")
            information = ticker_yf.financials.transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = "financials_fb"
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
        with subsubtabs[1]:
            st.markdown("# Quarterly financials")
            information = ticker_yf.quarterly_financials.transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = "quarterly_financials_fb"
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
        with subsubtabs[2]:
            informations = {}
            for x in ticker_yq.financial_data[stock].keys():
                information = ''.join(map(
                    lambda y: str(y) 
                    if str(y).islower() 
                    else " " + str(y), str(x))).upper()
                informations[information] = x
            st.markdown("# Financial data")
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
                    info_markdown = "".join(f"- **{key}:** {ticker_yq.financial_data[stock][value]}\n" for key, value in info[i].items())
                    st.markdown(info_markdown)
    with subtabs_[1]:
        subsubtabs = st.tabs([
            "Income Statement",
            "Quarterly Income Statement",
            "Income Statement Data"
        ])
        with subsubtabs[0]:
            st.markdown("# Income Statement")
            information = ticker_yf.income_stmt.transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = "income_stmt_fb"
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
        with subsubtabs[1]:
            st.markdown("# Quarterly Income Statement")
            information = ticker_yf.income_stmt.transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = "quarterly_income_stmt_fb"
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
        with subsubtabs[2]:
            st.markdown("# Income Statement Data")
            st.dataframe(
                ticker_yq.income_statement().reset_index().transpose().reset_index(),
                hide_index = True,
                use_container_width = True
            )
    with subtabs_[2]:
        subsubtabs = st.tabs([
            "Balance Sheet",
            "Quarterly Balance Sheet",
            "Balance Sheet Data"
        ])
        with subsubtabs[0]:
            st.markdown("# Balance Sheet")
            information = ticker_yf.balance_sheet.transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = "balance_sheet_fb"
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
        with subsubtabs[1]:
            st.markdown("# Quarterly financials")
            information = ticker_yf.quarterly_balance_sheet.transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = "quarterly_balance_sheet_fb"
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
        with subsubtabs[2]:
            st.markdown("# Balance Sheet Data")
            st.dataframe(
                ticker_yq.balance_sheet().reset_index().transpose().reset_index(),
                hide_index = True,
                use_container_width = True
            )
    with subtabs_[3]:
        subsubtabs = st.tabs([
            "Cash Flow",
            "Quarterly Cash Flow",
            "Cash Flow Data"
        ])
        with subsubtabs[0]:
            st.markdown("# Cash Flow")
            information = ticker_yf.cash_flow.transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = "cash_flow_fb"
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
        with subsubtabs[1]:
            st.markdown("# Quarterly Cash Flow")
            information = ticker_yf.quarterly_cash_flow.transpose()
            filterbox = st.selectbox(
                label = "Feature",
                options = sorted(information.columns),
                key = "quarterly_cash_flow_fb"
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
        with subsubtabs[2]:
            st.markdown("# Cash Flow Data")
            st.dataframe(
                ticker_yq.cash_flow().reset_index().transpose().reset_index(),
                hide_index = True,
                use_container_width = True
            )
    with subtabs_[4]:
        subsubtabs = st.tabs([
            "Major Holders",
            "Institutional Holders",
            "Mutual Fund Holders",
            "Insider Holders",
            "Insider Transactions",
            "Major Holders Data"
        ])
        with subsubtabs[0]:
            st.markdown("# Major Holders")
            st.dataframe(
                ticker_yf.major_holders,
                hide_index = True,
                use_container_width = True)
        with subsubtabs[1]:
            st.markdown("# Institutional Holders")
            st.dataframe(
                ticker_yf.institutional_holders,
                hide_index = True,
                use_container_width = True)
        with subsubtabs[2]:
            st.markdown("# Mutual Fund Holders")
            st.dataframe(
                ticker_yf.mutualfund_holders,
                hide_index = True,
                use_container_width = True)
        with subsubtabs[3]:
            st.markdown("# Insider Holders")
            st.dataframe(
                ticker_yq.insider_holders,
                hide_index = True,
                use_container_width = True)
        with subsubtabs[4]:
            st.markdown("# Insider Transactions")
            st.dataframe(
                ticker_yq.insider_transactions,
                hide_index = True,
                use_container_width = True)
        with subsubtabs[5]:
            indicators = {}
            for x in ticker_yq.major_holders[stock].keys():
                #try:
                    indicator = ''.join(map(
                        lambda y: str(y) 
                        if str(y).islower() 
                        else " " + str(y), x)).upper()
                    indicators[indicator] = x
                #except:
                #    pass
            #METRIC CARDS
            patterns = [
                "GENERAL INDICATORS",
            ]
            st.markdown("# Major Holders Data")
            general_indicator_metrics(
                stock,
                patterns,
                indicators,
                ticker_yq,
                5,
                "major_holders",
                "YahooQuery"
            )
    with subtabs_[5]:
        subsubtabs = st.tabs([
            "Earnings Dates",
            "Earning History",
            "Earnings",
            "Earnings Trend"
        ])
        with subsubtabs[0]:
            st.markdown(f"# Earnings Dates")
            try:
                information = ticker_yf.earnings_dates.reset_index()
                filterbox = st.selectbox(
                    label = "Feature",
                    options = sorted(information.columns.drop("Earnings Date")),
                    key = "earnings_dates_fb"
                )
                fig = px.bar(
                    information,
                    x = "Earnings Date",
                    y = filterbox,
                )
                fig.layout.showlegend = False
                st.plotly_chart(
                    fig,
                    use_container_width = True)
            except:
                st.write("No information.")
        with subsubtabs[1]:
            st.markdown("# Earning History")
            st.dataframe(
                ticker_yq.earning_history,
                hide_index = True,
                use_container_width = True)
        with subsubtabs[2]:
            st.markdown("# Earning History")
            st.dataframe(
                pd.json_normalize(ticker_yq.earnings[stock]).transpose(),
                #hide_index = True,
                use_container_width = True
            )
        with subsubtabs[3]:
            st.markdown("# Earnings Trend")
            st.dataframe(
                pd.json_normalize(ticker_yq.earnings_trend[stock]["trend"]).transpose(),
                use_container_width = True
            )
    with subtabs_[6]:
        st.markdown("# Valuation Measures")
        st.dataframe(
            ticker_yq.valuation_measures,
            hide_index = True,
            use_container_width = True
        )
    with subtabs_[7]:
        st.markdown("# Shares Full")
        try:
            information = ticker_yf.get_shares_full().transpose()
            fig = px.bar(
                information.reset_index(),
                x = "index",
                y = 0,
            )
            fig.layout.showlegend = False
            st.plotly_chart(
                fig,
                use_container_width = True)
        except:
            st.write("No information.")
    with subtabs_[8]:
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
                st.markdown(f"# {attr.replace('_', ' ').capitalize()}")
                try:
                    st.dataframe(ticker_yf.__getattribute__(attr)())
                except:
                    try:
                        st.dataframe(ticker_yf.__getattribute__(attr))
                    except:
                        st.write("No informations.")
    with subtabs_[9]:
        subsubtabs = st.tabs([
            "Index Trend",
            "Recommendation Trend"
        ])
        with subsubtabs[0]:
            st.markdown("# Index Trend")
            indicators = {}
            for x in ticker_yq.index_trend[stock].keys():
                if x != "estimates":
                    indicator = ''.join(map(
                        lambda y: str(y) 
                        if str(y).islower() 
                        else " " + str(y), str(x))).upper()
                    indicators[indicator] = x
            general_indicator_metrics(
                stock,
                [],
                indicators,
                ticker_yq,
                5,
                "index_trend",
                "YahooQuery"
            )
            st.header("Estimates")
            st.dataframe(
                pd.DataFrame(
                    ticker_yq.index_trend[stock]["estimates"]).transpose().reset_index(),
                    hide_index = True,
                    use_container_width = True
            )
        with subsubtabs[1]:
            st.markdown("# Recommendations Trend")
            st.dataframe(
                ticker_yq.recommendation_trend,
                hide_index = True,
                use_container_width = True
            )
    with subtabs_[10]:
        st.markdown("# Option Chain")
        st.dataframe(
            ticker_yq.option_chain,
            hide_index = True,
            use_container_width = True)
    with subtabs_[11]:
        subsubtabs = st.tabs([
            "Calendar Events",
            "Corporate Events"
        ])
        with subsubtabs[0]:
            st.markdown("# Calendar Events")
            st.dataframe(
                pd.json_normalize(ticker_yq.calendar_events[stock]).transpose().reset_index(),
                hide_index = True,
                use_container_width = True
            )
        with subsubtabs[1]:
            st.markdown("# Corporate Events")
            st.dataframe(
                ticker_yq.corporate_events,
                hide_index = True,
                use_container_width = True
            )
with main_tabs[6]:
    st.markdown("# Technical Insights")
    tab_names = [
        "Instrument Info",
        "Company Snapshot",
        "Recommendation",
        "Upsell",
        "Upsell Search",
        "Events",
        "Reports",
        "Sig Devs",
        "SEC Reports"
    ]
    tabs = st.tabs(tab_names)
    with tabs[0]:
        st.write(ticker_yq.technical_insights[stock]["instrumentInfo"])
    with tabs[1]:
        st.write(ticker_yq.technical_insights[stock]["companySnapshot"])
    with tabs[2]:
        st.write(ticker_yq.technical_insights[stock]["recommendation"])
    with tabs[3]:
        st.write(ticker_yq.technical_insights[stock]["upsell"])
    with tabs[4]:
        st.write(ticker_yq.technical_insights[stock]["upsellSearchDD"])
    with tabs[5]:
        st.write(ticker_yq.technical_insights[stock]["events"])
    with tabs[6]:
        st.write(ticker_yq.technical_insights[stock]["reports"])
    with tabs[7]:
        st.write(ticker_yq.technical_insights[stock]["sigDevs"])
    with tabs[8]:
        st.write(ticker_yq.technical_insights[stock]["secReports"])
