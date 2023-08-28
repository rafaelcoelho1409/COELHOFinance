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
    get_unimarket,
    indicator_metrics,
    general_indicator_metrics,
    get_news,
    option_menu,
    get_reports,
    get_sec_reports,
    stocks_filter_func,
    indices_filter_func,
    funds_filter_func,
    etfs_filter_func,
    currency_crosses_filter_func,
    cryptos_filter_func)

st.set_page_config(
    page_title = "COELHO Finance - UNIMARKET",
    layout = "wide"
)

option_menu()

st.title("$$\\textbf{COELHO Finance - UNIMARKET}$$")

with open("./data/periods_and_intervals.json", "r") as f:
    periods_and_intervals = json.load(f)

with st.sidebar:
    asset_filter = st.selectbox(
        label = "Asset type",
        placeholder = "Asset type",
        options = [
            "Stocks",
            "Indices",
            "Funds",
            "ETFs",
            "Currency Crosses",
            "Crypto",
            "Commodities",
            "Certificates",
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
            short_name
        ) = stocks_filter_func(periods_and_intervals)
    elif asset_filter == "Indices":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            long_name,
            currency
        ) = indices_filter_func(periods_and_intervals)
    elif asset_filter == "Funds":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            currency
        ) = funds_filter_func(periods_and_intervals)
    elif asset_filter == "ETFs":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            long_name,
            currency
        ) = etfs_filter_func(periods_and_intervals)
    elif asset_filter == "Currency Crosses":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name,
            currency
        ) = currency_crosses_filter_func(periods_and_intervals)
    elif asset_filter == "Crypto":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name,
            currency
        ) = cryptos_filter_func(periods_and_intervals)
    else:
        st.write("$$\\textbf{UNDER CONSTRUCTION}$$")
        st.stop()
            

(
    ticker_yf, 
    data_yf) = get_unimarket(
        element, 
        periods_and_intervals[0]["period"][period_filter], 
        periods_and_intervals[1]["interval"][interval_filter],
        "YFinance")

(
    ticker_yq,
    data_yq
) = get_unimarket(
    element,
    periods_and_intervals[0]["period"][period_filter], 
    periods_and_intervals[1]["interval"][interval_filter],
    "YahooQuery")

if asset_filter == "Stocks":
    currency = ticker_yf.info["currency"]

st.write(f"**{element_filter}**")

main_tabs = st.tabs([
        "$$\\textbf{UNIMARKET}$$",
        "$$\\textbf{INFORMATIONS}$$",
        "$$\\textbf{INDICATORS}$$",
        "$$\\textbf{NEWS}$$",
        "$$\\textbf{FINANCIAL}$$",
        "$$\\textbf{TECHNICAL INSIGHTS}$$"
])

with main_tabs[0]: #UNIMARKET TAB
    grid1 = grid([5, 2], vertical_align = True)
    with grid1.expander(
        label = "$$\\textbf{\\underline{UNIMARKET - " + asset_filter + "}}$$",
        expanded = True
    ):
        try:
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
                title = element_filter,
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
        except:
            st.write("No informations.")
    with grid1.expander(
        label = "$$\\textbf{\\underline{BASIC INFORMATIONS}}$$",
        expanded = True
    ):
        try:
            informations = {}
            for x in ticker_yf.info.keys():
                if (type(ticker_yf.info[x]) in [str]) and (x != "longBusinessSummary"):
                    information = ''.join(map(
                        lambda y: y 
                        if y.islower() 
                        else " " + y, x)).upper()
                    informations[information] = x
            for key, value in informations.items():
                st.write("$$\\textbf{" + key.capitalize() + ":} $$ " + ticker_yf.info[value])
        except:
            st.write("No informations.")
with main_tabs[1]: #INFORMATIONS TAB
    tabs = st.tabs([
        "Summary",
        "Company Officers",
    ])
    with tabs[0]:
        st.write("$$\\huge{\\textbf{Summary}}$$")
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
            st.write("No informations.")
    with tabs[1]:
        st.write("$$\\huge{\\textbf{Company Officers}}$$")
        try:
            st.dataframe(
                ticker_yf.info["companyOfficers"],
                use_container_width = True)
        except:
            st.write("No informations.")
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
        st.write("$$\\huge{\\textbf{Main Indicators}}$$")
        try:
            indicators = {}
            for x in ticker_yf.info.keys():
                if type(ticker_yf.info[x]) in [int, float]:
                    indicator = ''.join(map(
                        lambda y: y 
                        if y.islower() 
                        else " " + y, x)).upper()
                    indicators[indicator] = x
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
                    element,
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
                                element,
                                x, 
                                indicators, 
                                ticker_yf, 
                                5,
                                "info",
                                "YFinance")
                        except:
                            st.write("No informations.")
        except:
            pass
    with subtabs[1]:
        st.write("$$\\huge{\\textbf{ESG Scores}}$$")
        indicators_num, indicators_str = {}, {}
        try:
            for x in ticker_yq.esg_scores[element].keys():
                if type(ticker_yq.esg_scores[element][x]) in [int, float]:
                    indicator = ''.join(map(
                        lambda y: y 
                        if y.islower() 
                        else " " + y, x)).upper()
                    indicators_num[indicator] = x
                elif type(ticker_yq.esg_scores[element][x]) in [str]:
                    indicator = ''.join(map(
                        lambda y: y 
                        if y.islower() 
                        else " " + y, x)).upper()
                    indicators_str[indicator] = x
            #METRIC CARDS
            patterns = [
                "GENERAL INDICATORS",
            ]
            general_indicator_metrics(
                element,
                patterns,
                indicators_num,
                ticker_yq,
                5,
                "esg_scores",
                "YahooQuery"
            )
        except:
            st.write("No informations.")
    with subtabs[2]:
        st.write("$$\\huge{\\textbf{Grading History}}$$")
        try:
            st.dataframe(
                ticker_yq.grading_history,
                hide_index = True,
                use_container_width = True)
        except:
            st.write("No informations.")
    with subtabs[3]:
        st.write("$$\\huge{\\textbf{Institutional Ownership}}$$")
        try:
            st.dataframe(
                ticker_yq.institution_ownership.drop("maxAge", axis = 1),
                hide_index = True,
                use_container_width = True)
        except:
            st.write("No informations.")
    with subtabs[4]:
        st.write("$$\\huge{\\textbf{Key Stats}}$$")
        indicators_num, indicators_str = {}, {}
        try:
            for x in ticker_yq.key_stats[element].keys():
                if type(ticker_yq.key_stats[element][x]) in [int, float]:
                    indicator = ''.join(map(
                        lambda y: y 
                        if y.islower() 
                        else " " + y, x)).upper()
                    indicators_num[indicator] = x
                elif type(ticker_yq.key_stats[element][x]) in [str]:
                    indicator = ''.join(map(
                        lambda y: y 
                        if y.islower() 
                        else " " + y, x)).upper()
                    indicators_str[indicator] = x
            #METRIC CARDS
            patterns = [
                "GENERAL INDICATORS",
            ]
            subsubtabs = st.tabs([
                "MAIN INDICATORS",
                "MAIN INFORMATIONS"
            ])
            with subsubtabs[0]:
                general_indicator_metrics(
                    element,
                    patterns,
                    indicators_num,
                    ticker_yq,
                    5,
                    "key_stats",
                    "YahooQuery"
                )
            with subsubtabs[1]:
                general_indicator_metrics(
                    element,
                    patterns,
                    indicators_str,
                    ticker_yq,
                    5,
                    "key_stats",
                    "YahooQuery"
                )
        except:
            st.write("No informations.")
    with subtabs[5]:
        st.write("$$\\huge{\\textbf{Price}}$$")
        indicators_num, indicators_str = {}, {}
        try:
            for x in ticker_yq.price[element].keys():
                if type(ticker_yq.price[element][x]) in [int, float]:
                    indicator = ''.join(map(
                        lambda y: y 
                        if y.islower() 
                        else " " + y, x)).upper()
                    indicators_num[indicator] = x
                elif type(ticker_yq.price[element][x]) in [str]:
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
        subsubtabs = st.tabs([
            "Main Indicators",
            "Main Informations"
        ])
        with subsubtabs[0]:
            general_indicator_metrics(
                element,
                patterns,
                indicators_num,
                ticker_yq,
                5,
                "price",
                "YahooQuery"
            )
        with subsubtabs[1]:
            st.markdown("# Main informations")
            informations = {}
            try:
                for x in ticker_yq.price[element].keys():
                    information = ''.join(map(
                        lambda y: str(y) 
                        if str(y).islower() 
                        else " " + str(y), str(x))).upper()
                    if type(ticker_yq.price[element][x]) in [str]:
                        informations[information] = x
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
                        info_markdown = "".join(f"- **{key}:** {ticker_yq.price[element][value]}\n" for key, value in info[i].items())
                        st.markdown(info_markdown)
            except:
                st.write("No informations.")
    with subtabs[6]:
        st.write("$$\\huge{\\textbf{SEC Filings}}$$")
        try:
            sec_filings = ticker_yq.sec_filings.reset_index()
            sec_filings_exhibits = pd.json_normalize(sec_filings["exhibits"])
            sec_filings_final = pd.concat([
                sec_filings.drop("exhibits", axis = 1),
                sec_filings_exhibits
            ], axis = 1)
            st.dataframe(
                sec_filings_final.drop("maxAge", axis = 1),
                hide_index = True,
                use_container_width = True
            )
        except:
            st.write("No informations.")
    with subtabs[7]:
        st.write("$$\\huge{\\textbf{Share Purchase Activity}}$$")
        indicators = {}
        try:
            for x in ticker_yq.share_purchase_activity[element].keys():
                if type(ticker_yq.share_purchase_activity[element][x]) in [int, float, str]:
                    indicator = ''.join(map(
                        lambda y: y 
                        if y.islower() 
                        else " " + y, x)).upper()
                    indicators[indicator] = x
            #METRIC CARDS
            patterns = [
                "GENERAL INDICATORS",
            ]
            general_indicator_metrics(
                element,
                patterns,
                indicators,
                ticker_yq,
                5,
                "share_purchase_activity",
                "YahooQuery"
            )
        except:
            st.write("No informations.")
    with subtabs[8]:
        st.write("$$\\huge{\\textbf{Quotes}}$$")
        try:
            st.write(ticker_yq.quotes)
        except:
            st.write("No informations.")
    with subtabs[9]:
        st.write("$$\\huge{\\textbf{Recommendations}}$$")
        try:
            st.dataframe(
                ticker_yq.recommendations[element]["recommendedSymbols"],
                use_container_width = True)
        except:
            st.write("No informations.")
with main_tabs[3]: #NEWS TAB
    st.write("$$\\huge{\\textbf{Latest News}}$$")
    try:
        get_news(ticker_yf.news)
    except:
        st.write("No informations.")
with main_tabs[4]: #FINANCIAL TAB
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
            st.write("$$\\huge{\\textbf{Financials}}$$")
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
            st.write("$$\\huge{\\textbf{Quarterly Financials}}$$")
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
            st.write("$$\\huge{\\textbf{Financial Data}}$$")
            informations = {}
            try:
                for x in ticker_yq.financial_data[element].keys():
                    information = ''.join(map(
                        lambda y: str(y) 
                        if str(y).islower() 
                        else " " + str(y), str(x))).upper()
                    informations[information] = x
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
                        info_markdown = "".join(f"- **{key}:** {ticker_yq.financial_data[element][value]}\n" for key, value in info[i].items())
                        st.markdown(info_markdown)
            except:
                st.write("No informations.")
    with subtabs_[1]:
        subsubtabs = st.tabs([
            "Income Statement",
            "Quarterly Income Statement",
            "Income Statement Data"
        ])
        with subsubtabs[0]:
            st.write("$$\\huge{\\textbf{Income Statement}}$$")
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
            st.write("$$\\huge{\\textbf{Quarterly Income Statement}}$$")
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
            st.write("$$\\huge{\\textbf{Income Statement Data}}$$")
            try:
                st.dataframe(
                    ticker_yq.income_statement().reset_index().transpose().reset_index(),
                    hide_index = True,
                    use_container_width = True
                )
            except:
                st.write("No informations.")
    with subtabs_[2]:
        subsubtabs = st.tabs([
            "Balance Sheet",
            "Quarterly Balance Sheet",
            "Balance Sheet Data"
        ])
        with subsubtabs[0]:
            st.write("$$\\huge{\\textbf{Balance Sheet}}$$")
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
            st.write("$$\\huge{\\textbf{Quarterly Balance Sheet}}$$")
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
            st.write("$$\\huge{\\textbf{Balance Sheet Data}}$$")
            try:
                st.dataframe(
                    ticker_yq.balance_sheet().reset_index().transpose().reset_index(),
                    hide_index = True,
                    use_container_width = True
                )
            except:
                st.write("No informations.")
    with subtabs_[3]:
        subsubtabs = st.tabs([
            "Cash Flow",
            "Quarterly Cash Flow",
            "Cash Flow Data"
        ])
        with subsubtabs[0]:
            st.write("$$\\huge{\\textbf{Cash Flow}}$$")
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
            st.write("$$\\huge{\\textbf{Quarterly Cash Flow}}$$")
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
            st.write("$$\\huge{\\textbf{Cash Flow Data}}$$")
            try:
                st.dataframe(
                    ticker_yq.cash_flow().reset_index().transpose().reset_index(),
                    hide_index = True,
                    use_container_width = True
                )
            except:
                pass
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
            st.write("$$\\huge{\\textbf{Major Holders}}$$")
            st.dataframe(
                ticker_yf.major_holders,
                hide_index = True,
                use_container_width = True)
        with subsubtabs[1]:
            st.write("$$\\huge{\\textbf{Institutional Holders}}$$")
            st.dataframe(
                ticker_yf.institutional_holders,
                hide_index = True,
                use_container_width = True)
        with subsubtabs[2]:
            st.write("$$\\huge{\\textbf{Mutual Fund Holders}}$$")
            st.dataframe(
                ticker_yf.mutualfund_holders,
                hide_index = True,
                use_container_width = True)
        with subsubtabs[3]:
            st.write("$$\\huge{\\textbf{Insider Holders}}$$")
            try:
                st.dataframe(
                    ticker_yq.insider_holders.drop("maxAge", axis = 1),
                    hide_index = True,
                    use_container_width = True)
            except:
                st.write("No informations.")
        with subsubtabs[4]:
            st.write("$$\\huge{\\textbf{Insider Transactions}}$$")
            try:
                st.dataframe(
                    ticker_yq.insider_transactions.drop("maxAge", axis = 1),
                    hide_index = True,
                    use_container_width = True)
            except:
                st.write("No informations.")
        with subsubtabs[5]:
            st.write("$$\\huge{\\textbf{Major Holders Data}}$$")
            try:
                indicators = {}
                for x in ticker_yq.major_holders[element].keys():
                    indicator = ''.join(map(
                        lambda y: str(y) 
                        if str(y).islower() 
                        else " " + str(y), x)).upper()
                    indicators[indicator] = x
                #METRIC CARDS
                patterns = [
                    "GENERAL INDICATORS",
                ]
                general_indicator_metrics(
                    element,
                    patterns,
                    indicators,
                    ticker_yq,
                    5,
                    "major_holders",
                    "YahooQuery"
                )
            except:
                st.write("No informations.")
    with subtabs_[5]:
        subsubtabs = st.tabs([
            "Earnings Dates",
            "Earning History",
            "Earnings",
            "Earnings Trend"
        ])
        with subsubtabs[0]:
            st.write("$$\\huge{\\textbf{Earnings Dates}}$$")
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
                st.write("No informations.")
        with subsubtabs[1]:
            st.write("$$\\huge{\\textbf{Earning History}}$$")
            try:
                st.dataframe(
                    ticker_yq.earning_history.drop("maxAge", axis = 1),
                    hide_index = True,
                    use_container_width = True)
            except:
                st.write("No informations.")
        with subsubtabs[2]:
            st.write("$$\\huge{\\textbf{Earnings}}$$")
            try:
                st.dataframe(
                    pd.json_normalize(ticker_yq.earnings[element]).transpose(),
                    #hide_index = True,
                    use_container_width = True
                )
            except:
                st.write("No informations.")
        with subsubtabs[3]:
            st.write("$$\\huge{\\textbf{Earnings Trend}}$$")
            try:
                st.dataframe(
                    pd.json_normalize(ticker_yq.earnings_trend[element]["trend"]).transpose(),
                    use_container_width = True
                )
            except:
                st.write("No informations.")
    with subtabs_[6]:
        st.write("$$\\huge{\\textbf{Valuation Measures}}$$")
        try:
            st.dataframe(
                ticker_yq.valuation_measures,
                hide_index = True,
                use_container_width = True
            )
        except:
            st.write("No informations.")
    with subtabs_[7]:
        st.write("$$\\huge{\\textbf{Shares Full}}$$")
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
            st.write("No informations.")
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
                st.write("$$\\huge{\\textbf{" + attr.replace('_', ' ').capitalize() + "}}$$")
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
            st.write("$$\\huge{\\textbf{Index Trend}}$$")
            indicators = {}
            try:
                for x in ticker_yq.index_trend[element].keys():
                    if x != "estimates":
                        indicator = ''.join(map(
                            lambda y: str(y) 
                            if str(y).islower() 
                            else " " + str(y), str(x))).upper()
                        indicators[indicator] = x
                general_indicator_metrics(
                    element,
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
                        ticker_yq.index_trend[element]["estimates"]).transpose().reset_index(),
                        hide_index = True,
                        use_container_width = True
                )
            except:
                st.write("No informations.")
        with subsubtabs[1]:
            st.write("$$\\huge{\\textbf{Recommendations Trend}}$$")
            try:
                st.dataframe(
                    ticker_yq.recommendation_trend,
                    hide_index = True,
                    use_container_width = True
                )
            except:
                st.write("No informations.")
    with subtabs_[10]:
        st.write("$$\\huge{\\textbf{Option Chain}}$$")
        try:
            st.dataframe(
                ticker_yq.option_chain,
                hide_index = True,
                use_container_width = True)
        except:
            st.write("No informations.")
    with subtabs_[11]:
        subsubtabs = st.tabs([
            "Calendar Events",
            "Corporate Events"
        ])
        with subsubtabs[0]:
            st.write("$$\\huge{\\textbf{Calendar Events}}$$")
            try:
                st.dataframe(
                    pd.json_normalize(ticker_yq.calendar_events[element]).transpose().reset_index(),
                    hide_index = True,
                    use_container_width = True
                )
            except:
                st.write("No informations.")
        with subsubtabs[1]:
            st.write("$$\\huge{\\textbf{Corporate Events}}$$")
            try:
                st.dataframe(
                    ticker_yq.corporate_events,
                    hide_index = True,
                    use_container_width = True
                )
            except:
                st.write("No informations.")
with main_tabs[5]: #TECHNICAL INSIGHTS TAB
    tab_names = [
        "Instrument Info",
        "Company Snapshot",
        "Recommendation",
        "Upsell",
        "Upsell Search",
        "Events",
        "Reports",
        "SEC Reports"
    ]
    tabs = st.tabs(tab_names)
    with tabs[0]:
        st.write("$$\\huge{\\textbf{Instrument Info}}$$")
        try:
            st.write(ticker_yq.technical_insights[element]["instrumentInfo"])
        except:
            st.write("No informations.")
    with tabs[1]:
        st.write("$$\\huge{\\textbf{Company Snapshot}}$$")
        try:
            st.write(ticker_yq.technical_insights[element]["companySnapshot"])
        except:
            st.write("No informations.")
    with tabs[2]:
        st.write("$$\\huge{\\textbf{Recommendation}}$$")
        try:
            st.write(ticker_yq.technical_insights[element]["recommendation"])
        except:
            st.write("No informations.")
    with tabs[3]:
        st.write("$$\\huge{\\textbf{Upsell}}$$")
        try:
            st.write(ticker_yq.technical_insights[element]["upsell"])
        except:
            st.write("No informations.")
    with tabs[4]:
        st.write("$$\\huge{\\textbf{Upsell Search}}$$")
        try:
            st.write(ticker_yq.technical_insights[element]["upsellSearchDD"])
        except:
            st.write("No informations.")
    with tabs[5]:
        st.write("$$\\huge{\\textbf{Events}}$$")
        try:
            st.write(ticker_yq.technical_insights[element]["events"])
        except:
            st.write("No informations.")
    with tabs[6]:
        st.write("$$\\huge{\\textbf{Reports}}$$")
        try:
            get_reports(ticker_yq.technical_insights[element]["reports"])
        except:
            st.write("No informations.")
    with tabs[7]:
        st.write("$$\\huge{\\textbf{SEC Reports}}$$")
        try:
            get_sec_reports(ticker_yq.technical_insights[element]["secReports"])
        except:
            st.write("No informations.")