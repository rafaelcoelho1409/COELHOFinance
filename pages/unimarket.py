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
    cryptos_filter_func,
    bonds_filter_func,
    commodities_filter_func,
    split_key_name)

st.set_page_config(
    page_title = "COELHO Finance - UNIMARKET",
    layout = "wide"
)

option_menu()

st.title("$$\\large{\\textbf{COELHO Finance - UNIMARKET}}$$")

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
    elif asset_filter == "Bonds":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name
        ) = bonds_filter_func(periods_and_intervals)
    elif asset_filter == "Commodities":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name
        ) = commodities_filter_func(periods_and_intervals)
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

st.write("$$\\text{" + element_filter.replace("^", "").replace("&", "\\&") + "}$$")

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
            checkboxes_grid = grid(6, vertical_align = True)
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
            for x in ["Open", "High", "Low", "Close", "Volume"]:
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
            fig.layout.title = element_filter
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
        "$$\\textbf{Summary}$$",
        "$$\\textbf{Company Officers}$$",
    ])
    with tabs[0]:
        st.write("$$\\underline{\\huge{\\textbf{Summary}}}$$")
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
        st.write("$$\\underline{\\huge{\\textbf{Company Officers}}}$$")
        try:
            st.dataframe(
                pd.DataFrame(ticker_yf.info["companyOfficers"]).drop("maxAge", axis = 1),
                hide_index = True,
                use_container_width = True)
        except:
            st.write("No informations.")
with main_tabs[2]: #INDICATORS TAB
    subtab_names = [
        "$$\\textbf{Main Indicators}$$",
        "$$\\textbf{ESG Scores}$$",
        "$$\\textbf{Grading History}$$",
        "$$\\textbf{Institutional Ownership}$$",
        "$$\\textbf{Key Stats}$$",
        "$$\\textbf{Price}$$",
        "$$\\textbf{SEC Filings}$$",
        "$$\\textbf{Share Purchase Activity}$$",
        "$$\\textbf{Quotes}$$",
        "$$\\textbf{Recommendations}$$"
    ]
    subtabs = st.tabs(subtab_names)
    with subtabs[0]:
        st.write("$$\\underline{\\huge{\\textbf{Main Indicators}}}$$")
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
        st.write("$$\\underline{\\huge{\\textbf{ESG Scores}}}$$")
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
        st.write("$$\\underline{\\huge{\\textbf{Grading History}}}$$")
        try:
            st.dataframe(
                ticker_yq.grading_history,
                hide_index = True,
                use_container_width = True)
        except:
            st.write("No informations.")
    with subtabs[3]:
        st.write("$$\\underline{\\huge{\\textbf{Institutional Ownership}}}$$")
        try:
            st.dataframe(
                ticker_yq.institution_ownership.drop("maxAge", axis = 1),
                hide_index = True,
                use_container_width = True)
        except:
            st.write("No informations.")
    with subtabs[4]:
        st.write("$$\\underline{\\huge{\\textbf{Key Stats}}}$$")
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
        st.write("$$\\underline{\\huge{\\textbf{Price}}}$$")
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
                        for key, value in info[i].items():
                            info_latex = "$$\\textbf{" + key.capitalize() + ":}$$  " + ticker_yq.price[element][value] + "\n"
                            st.write(info_latex)
            except:
                st.write("No informations.")
    with subtabs[6]:
        st.write("$$\\underline{\\huge{\\textbf{SEC Filings}}}$$")
        try:
            sec_filings = ticker_yq.sec_filings.reset_index()
            sec_filings_exhibits = pd.json_normalize(sec_filings["exhibits"])
            sec_filings_final = pd.concat([
                sec_filings.drop("exhibits", axis = 1),
                sec_filings_exhibits
            ], axis = 1)
            st.dataframe(
                sec_filings_final.drop([
                    "maxAge",
                    "symbol",
                    "row"], axis = 1).reset_index(drop = True),
                hide_index = True,
                use_container_width = True
            )
        except:
            st.write("No informations.")
    with subtabs[7]:
        st.write("$$\\underline{\\huge{\\textbf{Share Purchase Activity}}}$$")
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
        st.write("$$\\underline{\\huge{\\textbf{Quotes}}}$$")
        try:
            st.write(ticker_yq.quotes)
        except:
            st.write("No informations.")
    with subtabs[9]:
        st.write("$$\\underline{\\huge{\\textbf{Recommendations (Score)}}}$$")
        try:
            recommended_symbols = pd.DataFrame(ticker_yq.recommendations[element]["recommendedSymbols"])
            grid1 = grid(recommended_symbols.shape[0], vertical_align = True)
            for x in recommended_symbols.iterrows():
                grid1.metric(
                    label = "$$\\textbf{Symbol:}$$  " + str(x[1]["symbol"]),
                    value = x[1]["score"]
                )
                style_metric_cards(
                    background_color = "#000000"
                )
        except:
            st.write("No informations.")
with main_tabs[3]: #NEWS TAB
    st.write("$$\\underline{\\huge{\\textbf{Latest News}}}$$")
    try:
        get_news(ticker_yf.news)
    except:
        st.write("No informations.")
with main_tabs[4]: #FINANCIAL TAB
    subtab_names = [
        "$$\\textbf{Financials}$$",
        "$$\\textbf{Income Statement}$$",
        "$$\\textbf{Balance Sheet}$$",
        "$$\\textbf{Cash Flow}$$",
        "$$\\textbf{Holders}$$",
        "$$\\textbf{Earnings}$$",
        "$$\\textbf{Valuation Measures}$$",
        "$$\\textbf{Shares Full}$$",
        "$$\\textbf{Dividends \& Splits}$$",
        "$$\\textbf{Trend}$$",
        "$$\\textbf{Option Chain}$$",
        "$$\\textbf{Events}$$"
    ]
    subtabs_ = st.tabs(subtab_names)
    with subtabs_[0]:
        subsubtabs = st.tabs([
            "Financials",
            "Quarterly Financials",
            "Financial Data"
        ])
        with subsubtabs[0]:
            st.write("$$\\underline{\\huge{\\textbf{Financials}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Quarterly Financials}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Financial Data}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Income Statement}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Quarterly Income Statement}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Income Statement Data}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Balance Sheet}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Quarterly Balance Sheet}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Balance Sheet Data}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Cash Flow}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Quarterly Cash Flow}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Cash Flow Data}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Major Holders}}}$$")
            major_holders = ticker_yf.major_holders
            st.dataframe(
                major_holders,
                hide_index = True)
        with subsubtabs[1]:
            st.write("$$\\underline{\\huge{\\textbf{Institutional Holders}}}$$")
            st.dataframe(
                ticker_yf.institutional_holders,
                hide_index = True,
                use_container_width = True)
        with subsubtabs[2]:
            st.write("$$\\underline{\\huge{\\textbf{Mutual Fund Holders}}}$$")
            st.dataframe(
                ticker_yf.mutualfund_holders,
                hide_index = True,
                use_container_width = True)
        with subsubtabs[3]:
            st.write("$$\\underline{\\huge{\\textbf{Insider Holders}}}$$")
            try:
                st.dataframe(
                    ticker_yq.insider_holders.drop("maxAge", axis = 1),
                    hide_index = True,
                    use_container_width = True)
            except:
                st.write("No informations.")
        with subsubtabs[4]:
            st.write("$$\\underline{\\huge{\\textbf{Insider Transactions}}}$$")
            try:
                st.dataframe(
                    ticker_yq.insider_transactions.drop("maxAge", axis = 1),
                    hide_index = True,
                    use_container_width = True)
            except:
                st.write("No informations.")
        with subsubtabs[5]:
            st.write("$$\\underline{\\huge{\\textbf{Major Holders Data}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Earnings Dates}}}$$")
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
        st.write("$$\\underline{\\huge{\\textbf{Valuation Measures}}}$$")
        try:
            st.dataframe(
                ticker_yq.valuation_measures,
                hide_index = True,
                use_container_width = True
            )
        except:
            st.write("No informations.")
    with subtabs_[7]:
        st.write("$$\\underline{\\huge{\\textbf{Shares Full}}}$$")
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
                st.write("$$\\underline{\\huge{\\textbf{" + attr.replace('_', ' ').capitalize() + "}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Index Trend}}}$$")
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
                st.header("Estimates (growth)")
                estimates = pd.DataFrame(
                        ticker_yq.index_trend[element]["estimates"]).reset_index(drop = True)
                grid1 = grid(estimates.shape[0], vertical_align = True)
                for x in estimates.iterrows():
                    grid1.metric(
                        label = "$$\\textbf{Period}: $$" + str(x[1]["period"]),
                        value = str(x[1]["growth"])
                    )
                style_metric_cards(
                    background_color = "#000000"
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
        st.write("$$\\underline{\\huge{\\textbf{Option Chain}}}$$")
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
            st.write("$$\\underline{\\huge{\\textbf{Calendar Events}}}$$")
            try:
                st.dataframe(
                    pd.json_normalize(ticker_yq.calendar_events[element]).transpose().reset_index(),
                    hide_index = True,
                    use_container_width = True
                )
            except:
                st.write("No informations.")
        with subsubtabs[1]:
            st.write("$$\\underline{\\huge{\\textbf{Corporate Events}}}$$")
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
        "$$\\textbf{Instrument Info}$$",
        "$$\\textbf{Company Snapshot}$$",
        "$$\\textbf{Recommendation}$$",
        "$$\\textbf{Upsell}$$",
        "$$\\textbf{Upsell Search}$$",
        "$$\\textbf{Events}$$",
        "$$\\textbf{Reports}$$",
        "$$\\textbf{SEC Reports}$$"
    ]
    tabs = st.tabs(tab_names)
    with tabs[0]:
        st.write("$$\\underline{\\huge{\\textbf{Instrument Info}}}$$")
        try:
            instrument_info = ticker_yq.technical_insights[element]["instrumentInfo"]
            st.write("   ")
            st.write("   ")
            cols1 = grid(3, vertical_align = True)
            with cols1.expander(
                    label = "Technical Events",
                    expanded = True
                ):
                st.latex("\\Large{\\textbf{Technical Events}}")
                st.write("$$\\large{\\textbf{Provider:  }}$$" + instrument_info["technicalEvents"]["provider"])
                st.write("$$\\large{\\textbf{Sector:  }}$$" + instrument_info["technicalEvents"]["sector"])
            with cols1.expander(
                    label = "Key Technicals",
                    expanded = True
                ):
                st.latex("\\Large{\\textbf{Key Technicals}}")
                for key, value in instrument_info["keyTechnicals"].items():
                    st.write("$$\\large{\\textbf{" + split_key_name(str(key)) + ":  }}$$" + str(value))
            with cols1.expander(
                    label = "Valuation",
                    expanded = True
                ):
                st.latex("\\Large{\\textbf{Valuation}}")
                for key, value in instrument_info["valuation"].items():
                    st.write("$$\\large{\\textbf{" + split_key_name(str(key)) + ":  }}$$" + str(value))
            st.divider()
            cols2 = grid(3, vertical_align = True)
            with cols2.expander(
                    label = "Short Term Outlook",
                    expanded = True
                ):
                st.latex("\\large{\\textbf{Short Term Outlook}}")
                for key, value in instrument_info["technicalEvents"]["shortTermOutlook"].items():
                    st.write("$$\\large{\\textbf{" + split_key_name(str(key)) + ":  }}$$" + str(value))
            with cols2.expander(
                label = "Intermediate Term Outlook",
                expanded = True
            ):
                st.latex("\\large{\\textbf{Intermediate Term Outlook}}")
                for key, value in instrument_info["technicalEvents"]["intermediateTermOutlook"].items():
                    st.write("$$\\large{\\textbf{" + split_key_name(str(key)) + ":  }}$$" + str(value))
            with cols2.expander(
                label = "Long Term Outlook",
                expanded = True
            ):
                st.latex("\\large{\\textbf{Long Term Outlook}}")
                for key, value in instrument_info["technicalEvents"]["longTermOutlook"].items():
                    st.write("$$\\large{\\textbf{" + split_key_name(str(key)) + ":  }}$$" + str(value))
        except:
            st.write("No informations.")
    with tabs[1]:
        st.write("$$\\underline{\\huge{\\textbf{Company Snapshot}}}$$")
        try:
            company_snapshot = ticker_yq.technical_insights[element]["companySnapshot"]
            st.write("   ")
            st.write("   ")
            st.write("$$\\large{\\textbf{Sector Info:  }}$$" + company_snapshot["sectorInfo"])
            cols = grid(2, vertical_align = True)
            with cols.expander(
                label = "Company",
                expanded = True
            ):
                st.latex("\\large{\\textbf{Company}}")
                for key, value in company_snapshot["company"].items():
                    st.write("$$\\large{\\textbf{" + split_key_name(str(key)) + ":  }}$$" + str(value))
            with cols.expander(
                label = "Sector",
                expanded = True
            ):
                st.latex("\\large{\\textbf{Sector}}")
                for key, value in company_snapshot["sector"].items():
                    st.write("$$\\large{\\textbf{" + split_key_name(str(key)) + ":  }}$$" + str(value))
        except:
            st.write("No informations.")
    with tabs[2]:
        st.write("$$\\underline{\\huge{\\textbf{Recommendation}}}$$")
        try:
            recommendation = ticker_yq.technical_insights[element]["recommendation"]
            st.write("   ")
            st.write("   ")
            for key, value in recommendation.items():
                st.write("$$\\large{\\textbf{" + split_key_name(str(key)) + ":  }}$$" + str(value))
        except:
            st.write("No informations.")
    with tabs[3]:
        st.write("$$\\underline{\\huge{\\textbf{Upsell}}}$$")
        try:
            upsell = ticker_yq.technical_insights[element]["upsell"]
            for x in [
                "companyName", 
                "msBullishBearishSummariesPublishDate",
                "upsellReportType"]:
                if type(upsell[x]) == int:
                    upsell[x] = dt.datetime.fromtimestamp(upsell[x]/1000)
                    st.write("$$\\large{\\textbf{" + split_key_name(str(x)).replace("Ms ", "").capitalize() + ":  }}$$" + str(upsell[x]))
                else:
                    st.write("$$\\large{\\textbf{" + split_key_name(str(x)).replace("Ms ", "").capitalize() + ":  }}$$" + str(upsell[x]))
            st.write("$$\\large{\\textbf{Bullish Summary}}$$")
            for i, x in enumerate(upsell["msBullishSummary"]):
                st.write(f"**{i+1}) {x}**")
            st.write("$$\\large{\\textbf{Bearish Summary}}$$")
            for i, x in enumerate(upsell["msBearishSummary"]):
                st.write(f"**{i+1}) {x}**")
        except:
            st.write("No informations.")
    with tabs[4]:
        st.write("$$\\underline{\\huge{\\textbf{Upsell Search}}}$$")
        try:
            upsell_search = ticker_yq.technical_insights[element]["upsellSearchDD"]
            st.write("$$\\large{\\textbf{Research Reports}}$$")
            for key, value in upsell_search["researchReports"].items():
                st.write("$$\\large{\\textbf{" + split_key_name(str(key)) + ":  }}$$" + str(value))
        except:
            st.write("No informations.")
    with tabs[5]:
        st.write("$$\\underline{\\huge{\\textbf{Events}}}$$")
        try:
            events = ticker_yq.technical_insights[element]["events"]
            for event in events:
                event_keys = [x for x in event.keys() if x != "imageUrl"]
                for key in event_keys:
                    if type(event[key]) == int:
                        event[key] = dt.datetime.fromtimestamp(event[key]/1000)
                        st.write("$$\\large{\\textbf{" + split_key_name(str(key)).replace("Ms ", "").capitalize() + ":  }}$$" + str(event[key]))
                    else:
                        st.write("$$\\large{\\textbf{" + split_key_name(str(key)).replace("Ms ", "").capitalize() + ":  }}$$" + str(event[key]))
                st.divider()
        except:
            st.write("No informations.")
    with tabs[6]:
        st.write("$$\\underline{\\huge{\\textbf{Reports}}}$$")
        try:
            get_reports(ticker_yq.technical_insights[element]["reports"])
        except:
            st.write("No informations.")
    with tabs[7]:
        st.write("$$\\underline{\\huge{\\textbf{SEC Reports}}}$$")
        try:
            get_sec_reports(ticker_yq.technical_insights[element]["secReports"])
        except:
            st.write("No informations.")