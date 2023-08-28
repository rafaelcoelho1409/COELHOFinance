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
    get_multimarket,
    indicator_metrics,
    general_indicator_metrics,
    get_news,
    option_menu,
    get_reports,
    get_sec_reports,
    stocks_filter_func,
    stocks_filter_func2,
    indices_filter_func)

st.set_page_config(
    page_title = "COELHO Finance - MULTIMARKET",
    layout = "wide"
)

option_menu()

st.title("$$\\textbf{COELHO Finance - MULTIMARKET}$$")

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
            "Bonds",
            "Commodities",
            "Certificates",
            "Crypto"
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
    else:
        st.write("$$\\textbf{UNDER CONSTRUCTION}$$")
        st.stop()

main_tabs = st.tabs([
        "$$\\textbf{MULTIMARKET}$$",
        "$$\\textbf{INFORMATIONS}$$",
        "$$\\textbf{INDICATORS}$$",
        "$$\\textbf{NEWS}$$",
        "$$\\textbf{FINANCIAL}$$",
        "$$\\textbf{TECHNICAL INSIGHTS}$$",
])

with main_tabs[0]: #COMPARISON TAB
    grid1 = grid([3, 3], [3, 3], vertical_align = True)
    grid1.write("$$\\textbf{Comparison Chart}$$")
    grid1.write("$$\\textbf{Correlation matrix (" + feature_filter + ")}$$")
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
    except:
        pass
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
#with main_tabs[2]: #INFORMATIONS TAB
#    tabs = st.tabs([
#        "Summary",
#        "Company Officers",
#        "Informations"
#    ])
#    with tabs[0]:
#        st.markdown("# Summary")
#        #This method below was made to avoid the company name to stay apart of the rest of the paragraph
#        try:
#            join_string = False
#            for x in ticker_yf.info["longBusinessSummary"].replace(". ", ".. ").split(". "):
#                if x == long_name:
#                    join_string = True
#                    string_to_be_joined = x
#                    continue
#                if join_string:
#                    st.markdown(f"- {string_to_be_joined} {x}")
#                    join_string = False
#                else:
#                    st.markdown(f"- {x}")
#        except:
#            st.write("No informations.")
#    with tabs[1]:
#        st.markdown("# Company Officers")
#        try:
#            st.dataframe(
#                ticker_yf.info["companyOfficers"],
#                use_container_width = True)
#        except:
#            st.write("No informations.")
#    with tabs[2]:
#        st.markdown("# Informations")
#        informations = {}
#        for x in ticker_yf.info.keys():
#            if (type(ticker_yf.info[x]) in [str]) and (x != "longBusinessSummary"):
#                information = ''.join(map(
#                    lambda y: y 
#                    if y.islower() 
#                    else " " + y, x)).upper()
#                informations[information] = x
#        info = {}, {}
#        items_per_col = len(informations) // 2 
#        for i, (key, value) in enumerate(informations.items()):
#            try:
#                info[(i // items_per_col)][key] = value
#            except:
#                pass
#        subcols = st.columns(2)
#        for i in range(len(subcols)):
#            with subcols[i]:
#                info_markdown = "".join(f"- **{key}:** {ticker_yf.info[value]}\n" for key, value in info[i].items())
#                st.markdown(info_markdown)
#with main_tabs[3]: #INDICATORS TAB
#    subtab_names = [
#        "MAIN INDICATORS",
#        "ESG SCORES",
#        "GRADING HISTORY",
#        "INSTITUTIONAL OWNERSHIP",
#        "KEY STATS",
#        "PRICE",
#        "SEC FILINGS",
#        "SHARE PURCHASE ACTIVITY",
#        "QUOTES",
#        "RECOMMENDATIONS"
#    ]
#    subtabs = st.tabs(subtab_names)
#    with subtabs[0]:
#        indicators = {}
#        for x in ticker_yf.info.keys():
#            if type(ticker_yf.info[x]) in [int, float]:
#                indicator = ''.join(map(
#                    lambda y: y 
#                    if y.islower() 
#                    else " " + y, x)).upper()
#                indicators[indicator] = x
#        st.markdown("# MAIN INDICATORS")
#        #METRIC CARDS
#        patterns = [
#            "GENERAL INDICATORS",
#            "RISK",
#            "MARKET",
#            "DIVIDEND",
#            "VOLUME",
#            "SHARE",
#            "DATE",
#            "EPOCH",
#            "DAY",
#            "PRICE",
#            "RATIO",
#            "AVERAGE",
#            "TRAILING",
#            "FORWARD",
#            "PERCENT",
#            "FISCAL",
#            "QUARTER",
#            "ENTERPRISE"
#        ]
#        subsubtabs = st.tabs(patterns)
#        with subsubtabs[0]:
#            general_indicator_metrics(
#                element,
#                patterns,
#                indicators,
#                ticker_yf,
#                5,
#                "info",
#                "YFinance"
#            )
#        for i, x in enumerate(patterns):
#            if i != 0: #NOT THE GENERAL TAB
#                with subsubtabs[i]:
#                    try:
#                        indicator_metrics(
#                            element,
#                            x, 
#                            indicators, 
#                            ticker_yf, 
#                            5,
#                            "info",
#                            "YFinance")
#                    except:
#                        st.write("No informations.")
#    with subtabs[1]:
#        st.markdown("# ESG Scores")
#        indicators_num, indicators_str = {}, {}
#        try:
#            for x in ticker_yq.esg_scores[element].keys():
#                if type(ticker_yq.esg_scores[element][x]) in [int, float]:
#                    indicator = ''.join(map(
#                        lambda y: y 
#                        if y.islower() 
#                        else " " + y, x)).upper()
#                    indicators_num[indicator] = x
#                elif type(ticker_yq.esg_scores[element][x]) in [str]:
#                    indicator = ''.join(map(
#                        lambda y: y 
#                        if y.islower() 
#                        else " " + y, x)).upper()
#                    indicators_str[indicator] = x
#            #METRIC CARDS
#            patterns = [
#                "GENERAL INDICATORS",
#            ]
#            general_indicator_metrics(
#                element,
#                patterns,
#                indicators_num,
#                ticker_yq,
#                5,
#                "esg_scores",
#                "YahooQuery"
#            )
#        except:
#            st.write("No informations.")
#    with subtabs[2]:
#        st.markdown("# Grading history")
#        try:
#            st.dataframe(
#                ticker_yq.grading_history,
#                hide_index = True,
#                use_container_width = True)
#        except:
#            st.write("No informations.")
#    with subtabs[3]:
#        st.markdown("# Institutional ownership")
#        try:
#            st.dataframe(
#                ticker_yq.institution_ownership.drop("maxAge", axis = 1),
#                hide_index = True,
#                use_container_width = True)
#        except:
#            st.write("No informations.")
#    with subtabs[4]:
#        st.markdown("# Key stats")
#        indicators_num, indicators_str = {}, {}
#        try:
#            for x in ticker_yq.key_stats[element].keys():
#                if type(ticker_yq.key_stats[element][x]) in [int, float]:
#                    indicator = ''.join(map(
#                        lambda y: y 
#                        if y.islower() 
#                        else " " + y, x)).upper()
#                    indicators_num[indicator] = x
#                elif type(ticker_yq.key_stats[element][x]) in [str]:
#                    indicator = ''.join(map(
#                        lambda y: y 
#                        if y.islower() 
#                        else " " + y, x)).upper()
#                    indicators_str[indicator] = x
#            #METRIC CARDS
#            patterns = [
#                "GENERAL INDICATORS",
#            ]
#            subsubtabs = st.tabs([
#                "MAIN INDICATORS",
#                "MAIN INFORMATIONS"
#            ])
#            with subsubtabs[0]:
#                general_indicator_metrics(
#                    element,
#                    patterns,
#                    indicators_num,
#                    ticker_yq,
#                    5,
#                    "key_stats",
#                    "YahooQuery"
#                )
#            with subsubtabs[1]:
#                general_indicator_metrics(
#                    element,
#                    patterns,
#                    indicators_str,
#                    ticker_yq,
#                    5,
#                    "key_stats",
#                    "YahooQuery"
#                )
#        except:
#            st.write("No informations.")
#    with subtabs[5]:
#        indicators_num, indicators_str = {}, {}
#        for x in ticker_yq.price[element].keys():
#            try:
#                if type(ticker_yq.price[element][x]) in [int, float]:
#                    indicator = ''.join(map(
#                        lambda y: y 
#                        if y.islower() 
#                        else " " + y, x)).upper()
#                    indicators_num[indicator] = x
#                elif type(ticker_yq.price[element][x]) in [str]:
#                    indicator = ''.join(map(
#                        lambda y: y 
#                        if y.islower() 
#                        else " " + y, x)).upper()
#                    indicators_str[indicator] = x
#            except:
#                pass
#        #METRIC CARDS
#        patterns = [
#            "GENERAL INDICATORS",
#        ]
#        st.markdown("# Price")
#        subsubtabs = st.tabs([
#            "Main Indicators",
#            "Main Informations"
#        ])
#        with subsubtabs[0]:
#            general_indicator_metrics(
#                element,
#                patterns,
#                indicators_num,
#                ticker_yq,
#                5,
#                "price",
#                "YahooQuery"
#            )
#        with subsubtabs[1]:
#            informations = {}
#            for x in ticker_yq.price[element].keys():
#                information = ''.join(map(
#                    lambda y: str(y) 
#                    if str(y).islower() 
#                    else " " + str(y), str(x))).upper()
#                if type(ticker_yq.price[element][x]) in [str]:
#                    informations[information] = x
#            st.markdown("# Main informations")
#            info = {}, {}
#            items_per_col = len(informations) // 2 
#            for i, (key, value) in enumerate(informations.items()):
#                try:
#                    info[(i // items_per_col)][key] = value
#                except:
#                    pass
#            subcols = st.columns(2)
#            for i in range(len(subcols)):
#                with subcols[i]:
#                    info_markdown = "".join(f"- **{key}:** {ticker_yq.price[element][value]}\n" for key, value in info[i].items())
#                    st.markdown(info_markdown)
#    with subtabs[6]:
#        st.markdown("# SEC Filings")
#        try:
#            sec_filings = ticker_yq.sec_filings.reset_index()
#            sec_filings_exhibits = pd.json_normalize(sec_filings["exhibits"])
#            sec_filings_final = pd.concat([
#                sec_filings.drop("exhibits", axis = 1),
#                sec_filings_exhibits
#            ], axis = 1)
#            st.dataframe(
#                sec_filings_final.drop("maxAge", axis = 1),
#                hide_index = True,
#                use_container_width = True
#            )
#        except:
#            st.write("No informations.")
#    with subtabs[7]:
#        st.markdown("# Share purchase activity")
#        indicators = {}
#        try:
#            for x in ticker_yq.share_purchase_activity[element].keys():
#                if type(ticker_yq.share_purchase_activity[element][x]) in [int, float, str]:
#                    indicator = ''.join(map(
#                        lambda y: y 
#                        if y.islower() 
#                        else " " + y, x)).upper()
#                    indicators[indicator] = x
#            #METRIC CARDS
#            patterns = [
#                "GENERAL INDICATORS",
#            ]
#            general_indicator_metrics(
#                element,
#                patterns,
#                indicators,
#                ticker_yq,
#                5,
#                "share_purchase_activity",
#                "YahooQuery"
#            )
#        except:
#            st.write("No informations.")
#    with subtabs[8]:
#        st.markdown("# Quotes")
#        try:
#            st.write(ticker_yq.quotes)
#        except:
#            st.write("No informations.")
#    with subtabs[9]:
#        try:
#            st.dataframe(
#                ticker_yq.recommendations[element]["recommendedSymbols"],
#                use_container_width = True)
#        except:
#            st.write("No informations.")
#with main_tabs[4]: #NEWS TAB
#    st.title("Latest News")
#    try:
#        get_news(ticker_yf.news)
#    except:
#        st.write("No informations.")
#with main_tabs[5]: #FINANCIAL TAB
#    subtab_names = [
#        "FINANCIALS",
#        "INCOME STATEMENT",
#        "BALANCE SHEET",
#        "CASH FLOW",
#        "HOLDERS",
#        "EARNINGS",
#        "VALUATION MEASURES",
#        "SHARES FULL",
#        "DIVIDENDS & SPLITS",
#        "TREND",
#        "OPTION CHAIN",
#        "EVENTS"
#    ]
#    subtabs_ = st.tabs(subtab_names)
#    with subtabs_[0]:
#        subsubtabs = st.tabs([
#            "Financials",
#            "Quarterly Financials",
#            "Financial Data"
#        ])
#        with subsubtabs[0]:
#            st.markdown("# Financials")
#            information = ticker_yf.financials.transpose()
#            filterbox = st.selectbox(
#                label = "Feature",
#                options = sorted(information.columns),
#                key = "financials_fb"
#            )
#            fig = px.bar(
#                information.reset_index(),
#                x = "index",
#                y = filterbox,
#            )
#            fig.layout.showlegend = False
#            st.plotly_chart(
#                fig,
#                use_container_width = True)
#        with subsubtabs[1]:
#            st.markdown("# Quarterly financials")
#            information = ticker_yf.quarterly_financials.transpose()
#            filterbox = st.selectbox(
#                label = "Feature",
#                options = sorted(information.columns),
#                key = "quarterly_financials_fb"
#            )
#            fig = px.bar(
#                information.reset_index(),
#                x = "index",
#                y = filterbox,
#            )
#            fig.layout.showlegend = False
#            st.plotly_chart(
#                fig,
#                use_container_width = True)
#        with subsubtabs[2]:
#            st.markdown("# Financial data")
#            informations = {}
#            try:
#                for x in ticker_yq.financial_data[element].keys():
#                    information = ''.join(map(
#                        lambda y: str(y) 
#                        if str(y).islower() 
#                        else " " + str(y), str(x))).upper()
#                    informations[information] = x
#                info = {}, {}
#                items_per_col = len(informations) // 2 
#                for i, (key, value) in enumerate(informations.items()):
#                    try:
#                        info[(i // items_per_col)][key] = value
#                    except:
#                        pass
#                subcols = st.columns(2)
#                for i in range(len(subcols)):
#                    with subcols[i]:
#                        info_markdown = "".join(f"- **{key}:** {ticker_yq.financial_data[element][value]}\n" for key, value in info[i].items())
#                        st.markdown(info_markdown)
#            except:
#                st.write("No informations.")
#    with subtabs_[1]:
#        subsubtabs = st.tabs([
#            "Income Statement",
#            "Quarterly Income Statement",
#            "Income Statement Data"
#        ])
#        with subsubtabs[0]:
#            st.markdown("# Income Statement")
#            information = ticker_yf.income_stmt.transpose()
#            filterbox = st.selectbox(
#                label = "Feature",
#                options = sorted(information.columns),
#                key = "income_stmt_fb"
#            )
#            fig = px.bar(
#                information.reset_index(),
#                x = "index",
#                y = filterbox,
#            )
#            fig.layout.showlegend = False
#            st.plotly_chart(
#                fig,
#                use_container_width = True)
#        with subsubtabs[1]:
#            st.markdown("# Quarterly Income Statement")
#            information = ticker_yf.income_stmt.transpose()
#            filterbox = st.selectbox(
#                label = "Feature",
#                options = sorted(information.columns),
#                key = "quarterly_income_stmt_fb"
#            )
#            fig = px.bar(
#                information.reset_index(),
#                x = "index",
#                y = filterbox,
#            )
#            fig.layout.showlegend = False
#            st.plotly_chart(
#                fig,
#                use_container_width = True)
#        with subsubtabs[2]:
#            st.markdown("# Income Statement Data")
#            try:
#                st.dataframe(
#                    ticker_yq.income_statement().reset_index().transpose().reset_index(),
#                    hide_index = True,
#                    use_container_width = True
#                )
#            except:
#                st.write("No informations.")
#    with subtabs_[2]:
#        subsubtabs = st.tabs([
#            "Balance Sheet",
#            "Quarterly Balance Sheet",
#            "Balance Sheet Data"
#        ])
#        with subsubtabs[0]:
#            st.markdown("# Balance Sheet")
#            information = ticker_yf.balance_sheet.transpose()
#            filterbox = st.selectbox(
#                label = "Feature",
#                options = sorted(information.columns),
#                key = "balance_sheet_fb"
#            )
#            fig = px.bar(
#                information.reset_index(),
#                x = "index",
#                y = filterbox,
#            )
#            fig.layout.showlegend = False
#            st.plotly_chart(
#                fig,
#                use_container_width = True)
#        with subsubtabs[1]:
#            st.markdown("# Quarterly financials")
#            information = ticker_yf.quarterly_balance_sheet.transpose()
#            filterbox = st.selectbox(
#                label = "Feature",
#                options = sorted(information.columns),
#                key = "quarterly_balance_sheet_fb"
#            )
#            fig = px.bar(
#                information.reset_index(),
#                x = "index",
#                y = filterbox,
#            )
#            fig.layout.showlegend = False
#            st.plotly_chart(
#                fig,
#                use_container_width = True)
#        with subsubtabs[2]:
#            st.markdown("# Balance Sheet Data")
#            try:
#                st.dataframe(
#                    ticker_yq.balance_sheet().reset_index().transpose().reset_index(),
#                    hide_index = True,
#                    use_container_width = True
#                )
#            except:
#                st.write("No informations.")
#    with subtabs_[3]:
#        subsubtabs = st.tabs([
#            "Cash Flow",
#            "Quarterly Cash Flow",
#            "Cash Flow Data"
#        ])
#        with subsubtabs[0]:
#            st.markdown("# Cash Flow")
#            information = ticker_yf.cash_flow.transpose()
#            filterbox = st.selectbox(
#                label = "Feature",
#                options = sorted(information.columns),
#                key = "cash_flow_fb"
#            )
#            fig = px.bar(
#                information.reset_index(),
#                x = "index",
#                y = filterbox,
#            )
#            fig.layout.showlegend = False
#            st.plotly_chart(
#                fig,
#                use_container_width = True)
#        with subsubtabs[1]:
#            st.markdown("# Quarterly Cash Flow")
#            information = ticker_yf.quarterly_cash_flow.transpose()
#            filterbox = st.selectbox(
#                label = "Feature",
#                options = sorted(information.columns),
#                key = "quarterly_cash_flow_fb"
#            )
#            fig = px.bar(
#                information.reset_index(),
#                x = "index",
#                y = filterbox,
#            )
#            fig.layout.showlegend = False
#            st.plotly_chart(
#                fig,
#                use_container_width = True)
#        with subsubtabs[2]:
#            st.markdown("# Cash Flow Data")
#            try:
#                st.dataframe(
#                    ticker_yq.cash_flow().reset_index().transpose().reset_index(),
#                    hide_index = True,
#                    use_container_width = True
#                )
#            except:
#                pass
#    with subtabs_[4]:
#        subsubtabs = st.tabs([
#            "Major Holders",
#            "Institutional Holders",
#            "Mutual Fund Holders",
#            "Insider Holders",
#            "Insider Transactions",
#            "Major Holders Data"
#        ])
#        with subsubtabs[0]:
#            st.markdown("# Major Holders")
#            st.dataframe(
#                ticker_yf.major_holders,
#                hide_index = True,
#                use_container_width = True)
#        with subsubtabs[1]:
#            st.markdown("# Institutional Holders")
#            st.dataframe(
#                ticker_yf.institutional_holders,
#                hide_index = True,
#                use_container_width = True)
#        with subsubtabs[2]:
#            st.markdown("# Mutual Fund Holders")
#            st.dataframe(
#                ticker_yf.mutualfund_holders,
#                hide_index = True,
#                use_container_width = True)
#        with subsubtabs[3]:
#            st.markdown("# Insider Holders")
#            try:
#                st.dataframe(
#                    ticker_yq.insider_holders.drop("maxAge", axis = 1),
#                    hide_index = True,
#                    use_container_width = True)
#            except:
#                st.write("No informations.")
#        with subsubtabs[4]:
#            st.markdown("# Insider Transactions")
#            try:
#                st.dataframe(
#                    ticker_yq.insider_transactions.drop("maxAge", axis = 1),
#                    hide_index = True,
#                    use_container_width = True)
#            except:
#                st.write("No informations.")
#        with subsubtabs[5]:
#            st.markdown("# Major Holders Data")
#            try:
#                indicators = {}
#                for x in ticker_yq.major_holders[element].keys():
#                    indicator = ''.join(map(
#                        lambda y: str(y) 
#                        if str(y).islower() 
#                        else " " + str(y), x)).upper()
#                    indicators[indicator] = x
#                #METRIC CARDS
#                patterns = [
#                    "GENERAL INDICATORS",
#                ]
#                general_indicator_metrics(
#                    element,
#                    patterns,
#                    indicators,
#                    ticker_yq,
#                    5,
#                    "major_holders",
#                    "YahooQuery"
#                )
#            except:
#                st.write("No informations.")
#    with subtabs_[5]:
#        subsubtabs = st.tabs([
#            "Earnings Dates",
#            "Earning History",
#            "Earnings",
#            "Earnings Trend"
#        ])
#        with subsubtabs[0]:
#            st.markdown(f"# Earnings Dates")
#            try:
#                information = ticker_yf.earnings_dates.reset_index()
#                filterbox = st.selectbox(
#                    label = "Feature",
#                    options = sorted(information.columns.drop("Earnings Date")),
#                    key = "earnings_dates_fb"
#                )
#                fig = px.bar(
#                    information,
#                    x = "Earnings Date",
#                    y = filterbox,
#                )
#                fig.layout.showlegend = False
#                st.plotly_chart(
#                    fig,
#                    use_container_width = True)
#            except:
#                st.write("No informations.")
#        with subsubtabs[1]:
#            st.markdown("# Earning History")
#            try:
#                st.dataframe(
#                    ticker_yq.earning_history.drop("maxAge", axis = 1),
#                    hide_index = True,
#                    use_container_width = True)
#            except:
#                st.write("No informations.")
#        with subsubtabs[2]:
#            st.markdown("# Earning History")
#            try:
#                st.dataframe(
#                    pd.json_normalize(ticker_yq.earnings[element]).transpose(),
#                    #hide_index = True,
#                    use_container_width = True
#                )
#            except:
#                st.write("No informations.")
#        with subsubtabs[3]:
#            st.markdown("# Earnings Trend")
#            try:
#                st.dataframe(
#                    pd.json_normalize(ticker_yq.earnings_trend[element]["trend"]).transpose(),
#                    use_container_width = True
#                )
#            except:
#                st.write("No informations.")
#    with subtabs_[6]:
#        st.markdown("# Valuation Measures")
#        try:
#            st.dataframe(
#                ticker_yq.valuation_measures,
#                hide_index = True,
#                use_container_width = True
#            )
#        except:
#            st.write("No informations.")
#    with subtabs_[7]:
#        st.markdown("# Shares Full")
#        try:
#            information = ticker_yf.get_shares_full().transpose()
#            fig = px.bar(
#                information.reset_index(),
#                x = "index",
#                y = 0,
#            )
#            fig.layout.showlegend = False
#            st.plotly_chart(
#                fig,
#                use_container_width = True)
#        except:
#            st.write("No informations.")
#    with subtabs_[8]:
#        attrs = [
#            "dividends", 
#            "capital_gains", 
#            "splits", 
#            "actions"
#            ]
#        subtabs = st.tabs([
#            x.replace("_", " ").upper() for x in attrs])
#        for i, attr in enumerate(attrs):
#            with subtabs[i]:
#                st.markdown(f"# {attr.replace('_', ' ').capitalize()}")
#                try:
#                    st.dataframe(ticker_yf.__getattribute__(attr)())
#                except:
#                    try:
#                        st.dataframe(ticker_yf.__getattribute__(attr))
#                    except:
#                        st.write("No informations.")
#    with subtabs_[9]:
#        subsubtabs = st.tabs([
#            "Index Trend",
#            "Recommendation Trend"
#        ])
#        with subsubtabs[0]:
#            st.markdown("# Index Trend")
#            indicators = {}
#            try:
#                for x in ticker_yq.index_trend[element].keys():
#                    if x != "estimates":
#                        indicator = ''.join(map(
#                            lambda y: str(y) 
#                            if str(y).islower() 
#                            else " " + str(y), str(x))).upper()
#                        indicators[indicator] = x
#                general_indicator_metrics(
#                    element,
#                    [],
#                    indicators,
#                    ticker_yq,
#                    5,
#                    "index_trend",
#                    "YahooQuery"
#                )
#                st.header("Estimates")
#                st.dataframe(
#                    pd.DataFrame(
#                        ticker_yq.index_trend[element]["estimates"]).transpose().reset_index(),
#                        hide_index = True,
#                        use_container_width = True
#                )
#            except:
#                st.write("No informations.")
#        with subsubtabs[1]:
#            st.markdown("# Recommendations Trend")
#            try:
#                st.dataframe(
#                    ticker_yq.recommendation_trend,
#                    hide_index = True,
#                    use_container_width = True
#                )
#            except:
#                st.write("No informations.")
#    with subtabs_[10]:
#        st.markdown("# Option Chain")
#        try:
#            st.dataframe(
#                ticker_yq.option_chain,
#                hide_index = True,
#                use_container_width = True)
#        except:
#            st.write("No informations.")
#    with subtabs_[11]:
#        subsubtabs = st.tabs([
#            "Calendar Events",
#            "Corporate Events"
#        ])
#        with subsubtabs[0]:
#            st.markdown("# Calendar Events")
#            try:
#                st.dataframe(
#                    pd.json_normalize(ticker_yq.calendar_events[element]).transpose().reset_index(),
#                    hide_index = True,
#                    use_container_width = True
#                )
#            except:
#                st.write("No informations.")
#        with subsubtabs[1]:
#            st.markdown("# Corporate Events")
#            try:
#                st.dataframe(
#                    ticker_yq.corporate_events,
#                    hide_index = True,
#                    use_container_width = True
#                )
#            except:
#                st.write("No informations.")
#with main_tabs[6]: #TECHNICAL INSIGHTS TAB
#    tab_names = [
#        "Instrument Info",
#        "Company Snapshot",
#        "Recommendation",
#        "Upsell",
#        "Upsell Search",
#        "Events",
#        "Reports",
#        "SEC Reports"
#    ]
#    tabs = st.tabs(tab_names)
#    with tabs[0]:
#        st.markdown("# Instrument Info")
#        try:
#            st.write(ticker_yq.technical_insights[element]["instrumentInfo"])
#        except:
#            st.write("No informations.")
#    with tabs[1]:
#        st.markdown("# Company Snapshot")
#        try:
#            st.write(ticker_yq.technical_insights[element]["companySnapshot"])
#        except:
#            st.write("No informations.")
#    with tabs[2]:
#        st.markdown("# Recommendation")
#        try:
#            st.write(ticker_yq.technical_insights[element]["recommendation"])
#        except:
#            st.write("No informations.")
#    with tabs[3]:
#        st.markdown("# Upsell")
#        try:
#            st.write(ticker_yq.technical_insights[element]["upsell"])
#        except:
#            st.write("No informations.")
#    with tabs[4]:
#        st.markdown("# Upsell Search")
#        try:
#            st.write(ticker_yq.technical_insights[element]["upsellSearchDD"])
#        except:
#            st.write("No informations.")
#    with tabs[5]:
#        st.markdown("# Events")
#        try:
#            st.write(ticker_yq.technical_insights[element]["events"])
#        except:
#            st.write("No informations.")
#    with tabs[6]:
#        st.markdown("# Reports")
#        try:
#            get_reports(ticker_yq.technical_insights[element]["reports"])
#        except:
#            st.write("No informations.")
#    with tabs[7]:
#        st.markdown("# SEC Reports")
#        try:
#            get_sec_reports(ticker_yq.technical_insights[element]["secReports"])
#        except:
#            st.write("No informations.")