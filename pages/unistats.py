import streamlit as st
import json
import numpy as np
import datetime as dt
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import pandas_ta as ta
import ruptures as rpt
from plotly.subplots import make_subplots
#FORECAST MODELS
from sktime.transformations.series.outlier_detection import HampelFilter
from statsmodels.tsa.seasonal import (
    seasonal_decompose,
    STL
)
from statsmodels.tsa.holtwinters import (
    ExponentialSmoothing,
    SimpleExpSmoothing,
    Holt
)
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller, kpss
from sklearn.metrics import mean_absolute_percentage_error
#ANOMALY DETECTION MODEL
from adtk.data import validate_series
from adtk.detector import (
    SeasonalAD,
    ThresholdAD,
    QuantileAD,
    InterQuartileRangeAD,
    GeneralizedESDTestAD,
    PersistAD
    )
#STREAMLIT THIRD-PARTY
from streamlit_extras.grid import grid
#internal functions
from functions import (
    get_unistats,
    option_menu,
    stocks_filter_func,
    indices_filter_func,
    funds_filter_func,
    etfs_filter_func,
    currency_crosses_filter_func,
    cryptos_filter_func,
    bonds_filter_func,
    commodities_filter_func,
    split_key_name)

PAGE_TITLE = "COELHO Finance - UNISTATS"
st.set_page_config(
    page_title = PAGE_TITLE,
    layout = "wide"
)

option_menu()

st.title("$$\\large{\\textbf{COELHO Finance - UNISTATS}}$$")

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
        ) = stocks_filter_func(
            periods_and_intervals,
            PAGE_TITLE)
    elif asset_filter == "Indices":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            long_name,
            currency
        ) = indices_filter_func(
            periods_and_intervals,
            PAGE_TITLE)
    elif asset_filter == "Funds":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            currency
        ) = funds_filter_func(
            periods_and_intervals,
            PAGE_TITLE)
    elif asset_filter == "ETFs":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            exchange,
            long_name,
            currency
        ) = etfs_filter_func(
            periods_and_intervals,
            PAGE_TITLE)
    elif asset_filter == "Currency Crosses":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name,
            currency
        ) = currency_crosses_filter_func(
            periods_and_intervals,
            PAGE_TITLE)
    elif asset_filter == "Crypto":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name,
            currency
        ) = cryptos_filter_func(
            periods_and_intervals,
            PAGE_TITLE)
    elif asset_filter == "Bonds":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name
        ) = bonds_filter_func(
            periods_and_intervals,
            PAGE_TITLE)
    elif asset_filter == "Commodities":
        (
            element,
            period_filter,
            interval_filter,
            element_filter,
            long_name
        ) = commodities_filter_func(
            periods_and_intervals,
            PAGE_TITLE)
    else:
        st.write("$$\\textbf{UNDER CONSTRUCTION}$$")
        st.stop()
            

(
    ticker_yf,
    data_yf) = get_unistats(
        element, 
        periods_and_intervals[0]["period"][period_filter], 
        periods_and_intervals[1]["interval"][interval_filter],
        "YFinance")

data_yf["Simple Return"] = data_yf["Adj Close"].pct_change()
data_yf["Log Return"] = np.log(data_yf["Adj Close"]/data_yf["Adj Close"].shift(1))
data_yf["Return"] = data_yf["Adj Close"].pct_change()

st.write("$$\\text{" + element_filter.replace("^", "").replace("&", "\\&") + "}$$")

main_tabs = st.tabs([
        "$$\\textbf{UNISTATS}$$",
        "$$\\textbf{INDICATORS}$$",
        "$$\\textbf{FORECAST}$$",
        "$$\\textbf{ANOMALY DETECTION}$$"
])

with main_tabs[0]: #UNIMARKET TAB
    st.write("$$\\textbf{\\underline{UNISTATS - " + asset_filter + "}}$$")
    try:
        checkboxes_grid = grid(9, vertical_align = True)
        checkboxes_grid.markdown("**OHLC filters**")
        fig = go.Figure()
        if checkboxes_grid.checkbox("OHLC", value = True):
            fig.add_trace(
                go.Candlestick(
                    x = data_yf.index,
                    open = data_yf["Open"],
                    high = data_yf["High"],
                    low = data_yf["Low"],
                    close = data_yf["Close"],
                )
            )
        for x in ["Open", "High", "Low", "Close", "Volume", "Adj Close"]:
            if checkboxes_grid.checkbox(x):
                fig.add_trace(
                    go.Scatter(
                        x = data_yf.index,
                        y = data_yf[x],
                        mode = "lines",
                        name = x
                    )
                )
        st.divider()
        ma_grid = grid(4, vertical_align = True)
        ma_grid.markdown("**Moving Average filters**")
        ma_window = ma_grid.number_input(
            label = "Moving Average window",
            min_value = 1,
            value = 5,
            step = 1,
            key = "ma_window_1"
        )
        data_yf["SMA"] = data_yf["Close"].rolling(window = ma_window).mean()
        data_yf["EMA"] = data_yf["Close"].ewm(span = ma_window, adjust = False).mean()
        for x in ["SMA", "EMA"]:
            if ma_grid.checkbox(x):
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
            height = 500,
            xaxis_rangeslider_visible = False,
            legend = {
                "orientation": "h"
            },
        )
        fig2.update_layout(
            height = 200,
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
with main_tabs[1]: #INDICATORS TAB
    tabs = st.tabs([
        "$$\\textbf{Outliers}$$",
        "$$\\textbf{RSI}$$",
        "$$\\textbf{MACD}$$"
    ])
    with tabs[0]:
        subtabs = st.tabs([
            "Rolling statistics",
            "Hampel filter",
            "Changepoints",
        ])
        with subtabs[0]:
            st.write("$$\\underline{\\huge{\\textbf{Outliers - Rolling Statistics}}}$$")
            ma_grid = grid(3, vertical_align = True)
            feature_options = data_yf.columns
            features_to_remove = [
                "mean", 
                "std", 
                "outlier", 
                "outlier_hampel",
                "upper",
                "lower"]
            for x in features_to_remove:
                try:
                    feature_options = feature_options.drop(x)
                except:
                    pass
            ma_feature = ma_grid.selectbox(
                label = "Feature",
                options = feature_options,
                index = 10,
                key = "ma_feature_1"
            )
            ma_window = ma_grid.number_input(
                label = "Rolling window size",
                min_value = 1,
                value = 5,
                step = 1,
                key = "ma_window_2"
            )
            N_SIGMAS = ma_grid.number_input(
                label = "Sigmas (Std)",
                min_value = 1.0,
                value = 1.0,
                step = 0.25,
                key = "sigmas"
            )
            try:
                aggs = data_yf["Return"]\
                    .rolling(window = ma_window)\
                    .agg(["mean", "std"])
                data_yf = data_yf.join(aggs)
                data_yf["upper"] = data_yf["mean"] + N_SIGMAS * data_yf["std"]
                data_yf["lower"] = data_yf["mean"] - N_SIGMAS * data_yf["std"]
                data_yf["outlier"] = (
                    (data_yf["Return"] > data_yf["upper"]) | (data_yf["Return"] < data_yf["lower"])
                )
                fig = go.Figure()
                #BOUNDARIES - UPPER
                fig.add_trace(
                    go.Scatter(
                        x = data_yf.index,
                        y = data_yf["upper"],
                        mode = "lines",
                        line = {
                            "width": 0
                        },
                        showlegend = False,
                        name = "Upper bound"
                    )
                )
                #BOUNDARIES - LOWER
                fig.add_trace(
                    go.Scatter(
                        x = data_yf.index,
                        y = data_yf["lower"],
                        mode = "lines",
                        line = {
                            "width": 0
                        },
                        fillcolor = "rgba(0,0,255,0.3)",
                        fill = "tonexty",
                        showlegend = False,
                        name = "Lower bound"
                    )
                )
                #RETURNS
                fig.add_trace(
                    go.Scatter(
                        x = data_yf.index,
                        y = data_yf["Return"],
                        mode = "lines",
                        name = "Returns"
                    )
                )
                #OUTLIERS
                outliers_data = data_yf[
                    data_yf["outlier"] == True
                ]
                fig.add_trace(
                    go.Scatter(
                        x = outliers_data.index,
                        y = outliers_data["Return"],
                        mode = "markers",
                        marker = {
                            "size": 10
                        },
                        name = "Outlier"
                    )
                )
                st.plotly_chart(
                    fig,
                    use_container_width = True
                )
            except:
                st.error("Not enough data to process. Choose another financial asset.")
        with subtabs[1]:
            st.write("$$\\underline{\\huge{\\textbf{Outliers - Hampel Filter}}}$$")
            ma_grid = grid(2, vertical_align = True)
            feature_options = data_yf.columns
            features_to_remove = [
                "mean", 
                "std", 
                "outlier", 
                "outlier_hampel",
                "upper",
                "lower"]
            for x in features_to_remove:
                try:
                    feature_options = feature_options.drop(x)
                except:
                    pass
            ma_feature = ma_grid.selectbox(
                label = "Feature",
                options = feature_options,
                index = 4,
                key = "ma_feature_2"
            )
            ma_window = ma_grid.number_input(
                label = "Rolling window size",
                min_value = 1,
                value = 5,
                step = 1,
                key = "ma_window_3"
            )
            try:
                hampel_detector = HampelFilter(
                    window_length = ma_window,
                    return_bool = True
                )
                outlier_hampel = hampel_detector.fit_transform(data_yf[ma_feature])
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x = data_yf.index,
                        y = data_yf[ma_feature],
                        mode = "lines",
                        name = ma_feature
                    )
                )
                outliers_data = data_yf[
                    outlier_hampel == True
                ]
                fig.add_trace(
                    go.Scatter(
                        x = outliers_data.index,
                        y = outliers_data[ma_feature],
                        mode = "markers",
                        name = "Outlier",
                        marker = {
                            "color": "red",
                            "size": 10
                        }
                    )
                )
                st.plotly_chart(
                    fig,
                    use_container_width = True
                )
            except:
                st.error("Not enough data to process. Choose another financial asset.")
        with subtabs[2]:
            st.write("$$\\underline{\\huge{\\textbf{Outliers - Changepoints}}}$$")
            ma_grid = grid(3, vertical_align = True)
            ma_model = ma_grid.selectbox(
                label = "Changepoint Model",
                options = [
                    "Dynamic Programming",
                    "Binary Segmentation",
                    "Window"
                ]
            )
            feature_options = data_yf.columns
            features_to_remove = [
                "mean", 
                "std", 
                "outlier", 
                "outlier_hampel",
                "upper",
                "lower"]
            for x in features_to_remove:
                try:
                    feature_options = feature_options.drop(x)
                except:
                    pass
            ma_feature = ma_grid.selectbox(
                label = "Feature",
                options = feature_options,
                index = 4,
                key = "ma_feature_4"
            )
            breakpoints = ma_grid.number_input(
                label = "Breakpoints",
                min_value = 1,
                step = 1,
                key = "bkp")
            try:
                if ma_model == "Dynamic Programming":
                    try:
                        algo = rpt.Dynp(model = "l2", min_size = 30)
                        algo.fit(data_yf[ma_feature].values.reshape(-1, 1))
                        result = algo.predict(n_bkps = breakpoints)
                        st.pyplot(rpt.display(
                            data_yf[ma_feature].values.reshape(-1, 1),
                            [],
                            result)[0])
                    except rpt.exceptions.BadSegmentationParameters:
                        st.error("Increase the period to get results.")
                elif ma_model == "Binary Segmentation":
                    try:
                        algo = rpt.Binseg(model = "l2", min_size = 30)
                        algo.fit(data_yf[ma_feature].values.reshape(-1, 1))
                        result = algo.predict(n_bkps = breakpoints)
                        st.pyplot(rpt.display(
                            data_yf[ma_feature].values.reshape(-1, 1),
                            [],
                            result)[0])
                    except rpt.exceptions.BadSegmentationParameters:
                        st.error("Increase the period to get results.")
                elif ma_model == "Window":
                    try:
                        algo = rpt.Window(model = "l2", min_size = 30)
                        algo.fit(data_yf[ma_feature].values.reshape(-1, 1))
                        result = algo.predict(n_bkps = breakpoints)
                        st.pyplot(rpt.display(
                            data_yf[ma_feature].values.reshape(-1, 1),
                            [],
                            result)[0])
                    except rpt.exceptions.BadSegmentationParameters:
                        st.error("Increase the period to get results.")
            except:
                st.error("Not enough data to process. Choose another financial asset.")
    with tabs[1]:
        st.write("$$\\underline{\\huge{\\textbf{RSI - Relative Strength Index}}}$$")
        RSI = ta.rsi(data_yf["Close"])
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x = data_yf.index,
                y = RSI,
                mode = "lines",
                name = "RSI (Close)"
            )
        )
        fig.add_trace(
            go.Scatter(
                x = data_yf.index,
                y = [30] * len(data_yf.index),
                mode = "lines",
                line = {
                    "dash": "dash",
                    "color": "red"
                }
            )
        )
        fig.add_trace(
            go.Scatter(
                x = data_yf.index,
                y = [70] * len(data_yf.index),
                mode = "lines",
                line = {
                    "dash": "dash",
                    "color": "red"
                }
            )
        )
        st.plotly_chart(
            fig,
            use_container_width = True)
    with tabs[2]:
        st.write("$$\\underline{\\huge{\\textbf{MACD - Moving Average Convergence/Divergence}}}$$")
        try:
            data_yf.ta.macd(
                close = "Close",
                fast = 12,
                slow = 26,
                signal = 9,
                append = True)
            fig = make_subplots(
                rows = 2,
                cols = 1
            )
            #Price Line
            fig.append_trace(
                go.Scatter(
                    x = data_yf.index,
                    y = data_yf["Open"],
                    line = {
                        "color": "#000000",
                        "width": 1
                    },
                    name = "Open",
                    legendgroup = 1
                ),
                row = 1,
                col = 1
            )
            #Candlestick chart
            fig.append_trace(
                go.Candlestick(
                    x = data_yf.index,
                    open = data_yf['Open'],
                    high = data_yf['High'],
                    low = data_yf['Low'],
                    close = data_yf['Close'],
                    increasing_line_color = '#00FF00',
                    decreasing_line_color = '#FF0000',
                    showlegend=False
                ), 
                row = 1, 
                col = 1
            )
            # Fast Signal (%k)
            fig.append_trace(
                go.Scatter(
                    x = data_yf.index,
                    y = data_yf['MACD_12_26_9'],
                    line = dict(
                        color = '#0000FF', 
                        width = 2),
                    name = 'MACD',
                    # showlegend=False,
                    legendgroup = '2',
                ), 
                row = 2, 
                col = 1
            )
            # Slow signal (%d)
            fig.append_trace(
                go.Scatter(
                    x = data_yf.index,
                    y = data_yf['MACDs_12_26_9'],
                    line = dict(
                        color = '#000000', 
                        width = 2),
                    # showlegend=False,
                    legendgroup = '2',
                    name = 'signal'
                ), 
                row = 2, 
                col = 1
            )
            # Colorize the histogram values
            colors = np.where(data_yf['MACDh_12_26_9'] < 0, '#FF0000', '#00FF00')
            # Plot the histogram
            fig.append_trace(
                go.Bar(
                    x = data_yf.index,
                    y = data_yf['MACDh_12_26_9'],
                    name = 'histogram',
                    marker_color = colors,
                ), 
                row = 2, 
                col = 1
            )
            # Make it pretty
            layout = go.Layout(
                plot_bgcolor =' #EFEFEF',
                height = 800,
                # Font Families
                font_family = 'Monospace',
                font_color = '#000000',
                font_size = 20,
                xaxis = dict(
                    rangeslider = dict(
                        visible = False
                    )
                )
            )
            # Update options and show plot
            fig.update_layout(layout)
            st.plotly_chart(
                fig,
                use_container_width = True)
        except:
            st.error("Not enough data to process. Choose another financial asset.")
with main_tabs[2]: #FORECAST TAB
    tabs = st.tabs([
        "$$\\textbf{Seasonality}$$",
        "$$\\textbf{Stationarity}$$",
        "$$\\textbf{Exponential Smoothing}$$",
        "$$\\textbf{ARIMA}$$",
    ])
    with tabs[0]:
        st.write("$$\\underline{\\huge{\\textbf{Seasonal Decomposition}}}$$")
        grid1 = grid(4, vertical_align = True)
        model_filter = grid1.selectbox(
            label = "Model",
            options = [
                "Seasonal Decompose",
                "STL"
            ]
        )
        feature = grid1.selectbox(
            label = "Feature",
            options = [
                "Open", 
                "High", 
                "Low", 
                "Close", 
                "Adj Close", 
                "Volume"
                ],
            index = 4,
            key = "feature1"
        )
        ts_type = grid1.selectbox(
            label = "Time Series type",
            options = [
                "additive",
                "multiplicative"
            ]
        )
        window_size = grid1.number_input(
            label = "Rolling window size",
            min_value = 1,
            value = 10,
            step = 1
        )
        rolling_mean = data_yf[feature].rolling(window = window_size).mean()
        rolling_std = data_yf[feature].rolling(window = window_size).std()
        fig = go.Figure()
        for data in [
            (data_yf[feature], feature), 
            (rolling_mean, "Mean"), 
            (rolling_std, "Std")]:
            fig.add_trace(
                go.Scatter(
                    x = data_yf.index,
                    y = data[0],
                    mode = "lines",
                    name = data[1]
                )
            )
        fig.layout.title = "Statistics - " + feature
        st.plotly_chart(
            fig,
            use_container_width = True
        )
        try:
            if model_filter == "Seasonal Decompose":
                try:
                    decomposition_results = seasonal_decompose(
                        data_yf[feature],
                        model = ts_type,
                        period = 21 #21 business days
                    )
                    st.pyplot(
                        decomposition_results.plot()
                    )
                except:
                    st.error("Increase the period of the data.")
            elif model_filter == "STL":
                try:
                    stl_decomposition = STL(
                        data_yf[feature],
                        period = 21
                    ).fit()
                    st.pyplot(
                        stl_decomposition.plot()
                    )
                except: 
                    st.error("Increase the period of the data.")
        except:
            st.error("Not enough data to process. Choose another financial asset.")
    with tabs[1]:
        st.write("$$\\underline{\\huge{\\textbf{Stationarity}}}$$")
        feature = st.selectbox(
            label = "Feature",
            options = [
                "Open", 
                "High", 
                "Low", 
                "Close", 
                "Adj Close", 
                "Volume"
                ],
            index = 4,
            key = "feature2"
        )
        try:
            cols = st.columns(2)
            with cols[0]:
                st.write("$$\\huge{\\textbf{ADF Test}}$$")
                indices = [
                    "Test Statistic",
                    "p-value",
                    "# of Lags Used",
                    "# of Observations Used"
                ]
                adf_test = adfuller(data_yf[feature], autolag = "AIC")
                results = pd.Series(adf_test[0:4], index = indices)
                for key, value in adf_test[4].items():
                    results[f"Critical Value ({key})"] = value
                st.text(results)
            with cols[1]:
                st.write("$$\\huge{\\textbf{KPSS Test}}$$")
                indices = [
                    "Test Statistic",
                    "p-value",
                    "# of Lags"
                ]
                kpss_test = kpss(data_yf[feature], regression = "c")
                results = pd.Series(kpss_test[0:3], index = indices)
                for key, value in kpss_test[3].items():
                    results[f"Critical Value ({key})"] = value
                st.text(results)
            cols2 = st.columns(2)
            N_LAGS = 30
            SIGNIFICANCE_LEVEL = 0.05
            with cols2[0]:
                st.pyplot(plot_acf(data_yf[feature], lags = N_LAGS, alpha = SIGNIFICANCE_LEVEL))
            with cols2[1]:
                st.pyplot(plot_pacf(data_yf[feature], lags = N_LAGS, alpha = SIGNIFICANCE_LEVEL))
        except:
            st.error("Not enough data to process. Choose another financial asset.")
    with tabs[2]:
        st.write("$$\\underline{\\huge{\\textbf{Exponential Smoothing}}}$$")
        TEST_LENGTH = 15
        data_yf2 = data_yf.copy()
        data_train = data_yf2.iloc[:-TEST_LENGTH]
        data_test = data_yf2.iloc[-TEST_LENGTH:]
        grid1 = grid(2, vertical_align = True)
        model_filter = grid1.selectbox(
            label = "Model",
            options = [
                "Simple Exponential Smoothing",
                "Holt's model",
                "Holt-Winters' Triple Exponential Smoothing"
            ]
        )
        feature = grid1.selectbox(
            label = "Feature",
            options = [
                "Open", 
                "High", 
                "Low", 
                "Close", 
                "Adj Close", 
                "Volume"
                ],
            index = 4,
            key = "feature3"
        )
        try:
            if model_filter == "Simple Exponential Smoothing":
                ses_1 = SimpleExpSmoothing(data_train[feature]).fit(smoothing_level = 0.5)
                ses_forecast_1 = ses_1.forecast(TEST_LENGTH)
                ses_2 = SimpleExpSmoothing(data_train[feature]).fit()
                ses_forecast_2 = ses_2.forecast(TEST_LENGTH)
                ses_data = pd.DataFrame()
                ses_data["ses_1"] = ses_1.fittedvalues.tolist() + ses_forecast_1.tolist()
                ses_data["ses_2"] = ses_2.fittedvalues.tolist() + ses_forecast_2.tolist()
                ses_data.index = data_yf2.index
                opt_alpha = ses_2.model.params["smoothing_level"]
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x = data_yf2.index,
                        y = data_yf2[feature],
                        mode = "lines",
                        name = feature
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x = ses_data.index,
                        y = ses_data["ses_1"],
                        mode = "lines",
                        name = "SES",
                        line = {
                                "dash": "dash",
                                "color": "blue"
                            }
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x = ses_data.index,
                        y = ses_data["ses_1"],
                        mode = "lines",
                        name = "SES (smoothing level = 0.5)",
                        line = {
                                "dash": "dash",
                                "color": "red"
                            }
                    )
                )
                st.plotly_chart(
                    fig,
                    use_container_width = True
                )
            elif model_filter == "Holt's model":
                #Holt's model with linear trend
                hs_1 = Holt(data_train[feature]).fit()
                hs_forecast_1 = hs_1.forecast(TEST_LENGTH)
                #Holt's model with exponential trend
                hs_2 = Holt(data_train[feature], exponential = True).fit()
                hs_forecast_2 = hs_2.forecast(TEST_LENGTH)
                #Holt's model with exponential trend and damping
                hs_3 = Holt(data_train[feature], exponential = False, damped_trend = True).fit()
                hs_forecast_3 = hs_3.forecast(TEST_LENGTH)
                holt_data = pd.DataFrame()
                holt_data["hs_1"] = hs_1.fittedvalues.tolist() + hs_forecast_1.tolist()
                holt_data["hs_2"] = hs_2.fittedvalues.tolist() + hs_forecast_2.tolist()
                holt_data["hs_3"] = hs_3.fittedvalues.tolist() + hs_forecast_3.tolist()
                holt_data.index = data_yf2.index
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x = data_yf2.index,
                        y = data_yf2[feature],
                        mode = "lines",
                        name = feature
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x = holt_data.index,
                        y = holt_data["hs_1"],
                        mode = "lines",
                        name = "Holt's model with linear trend",
                        line = {
                                "dash": "dash",
                                "color": "blue"
                            }
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x = holt_data.index,
                        y = holt_data["hs_2"],
                        mode = "lines",
                        name = "Holt's model with exponential trend",
                        line = {
                                "dash": "dash",
                                "color": "red"
                            }
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x = holt_data.index,
                        y = holt_data["hs_2"],
                        mode = "lines",
                        name = "Holt's model with exponential trend and damping",
                        line = {
                                "dash": "dash",
                                "color": "green"
                            }
                    )
                )
                st.plotly_chart(
                    fig,
                    use_container_width = True
                )
            elif model_filter == "Holt-Winters' Triple Exponential Smoothing":
                SEASONAL_PERIODS = 12
                #Holt-Winters' model with exponential trend
                hw_1 = ExponentialSmoothing(
                    data_train[feature],
                    trend = "mul",
                    seasonal = "add",
                    seasonal_periods = SEASONAL_PERIODS
                ).fit()
                hw_forecast_1 = hw_1.forecast(TEST_LENGTH)
                #Holt-Winters' model with exponential trend and damping
                hw_2 = ExponentialSmoothing(
                    data_train[feature],
                    trend = "mul",
                    seasonal = "add",
                    seasonal_periods = SEASONAL_PERIODS,
                    damped_trend = True
                ).fit()
                hw_forecast_2 = hw_2.forecast(TEST_LENGTH)
                hw_data = pd.DataFrame()
                hw_data["hw_1"] = hw_1.fittedvalues.tolist() + hw_forecast_1.tolist()
                hw_data["hw_2"] = hw_2.fittedvalues.tolist() + hw_forecast_2.tolist()
                hw_data.index = data_yf2.index
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x = data_yf2.index,
                        y = data_yf2[feature],
                        mode = "lines",
                        name = feature
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x = hw_data.index,
                        y = hw_data["hw_1"],
                        mode = "lines",
                        name = "Holt-Winters' model with exponential trend",
                        line = {
                                "dash": "dash",
                                "color": "blue"
                            }
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x = hw_data.index,
                        y = hw_data["hw_2"],
                        mode = "lines",
                        name = "Holt-Winters' model with exponential trend and damping",
                        line = {
                                "dash": "dash",
                                "color": "red"
                            }
                    )
                )
                st.plotly_chart(
                    fig,
                    use_container_width = True
                )
        except:
            st.error("Not enough data to process. Choose another financial asset.")
    with tabs[3]:
        st.write("$$\\underline{\\huge{\\textbf{ARIMA}}}$$")
        grid1 = grid(1, vertical_align = True)
        feature = grid1.selectbox(
            label = "Feature",
            options = [
                "Open", 
                "High", 
                "Low", 
                "Close", 
                "Adj Close", 
                "Volume"
                ],
            index = 4,
            key = "feature4"
        )
        try:
            with st.expander(
                label = "Stationary feature"
            ):
                grid2 = grid([4, 1], vertical_align = True)
                container = grid2.container()
                #transforming time series to stationarity
                data_train[f"{feature} log"] = np.log(data_train[feature])
                data_train[f"{feature} diff"] = data_train[f"{feature} log"].diff()
                fig = make_subplots(
                    rows = 3, 
                    cols = 1,
                    subplot_titles = (
                        feature,
                        f"{feature} log",
                        f"{feature} diff"
                    ))
                fig.append_trace(
                    go.Scatter(
                        x = data_train.index,
                        y = data_train[feature],
                        mode = "lines",
                        name = feature
                    ),
                    row = 1,
                    col = 1
                )
                fig.append_trace(
                    go.Scatter(
                        x = data_train.index,
                        y = data_train[f"{feature} log"],
                        mode = "lines",
                        name = f"{feature} log"
                    ),
                    row = 2,
                    col = 1
                )
                fig.append_trace(
                    go.Scatter(
                        x = data_train.index,
                        y = data_train[f"{feature} diff"],
                        mode = "lines",
                        name = f"{feature} diff"
                    ),
                    row = 3,
                    col = 1
                )
                fig.update_layout(
                    height = 800
                )
                container.plotly_chart(
                    fig,
                    use_container_width = True
                )
                container2 = grid2.container()
                container2.text("Feature: " + f"{feature} diff")
                container2.write("$$\\huge{\\textbf{ADF Test}}$$")
                indices = [
                    "Test Statistic",
                    "p-value",
                    "# of Lags Used",
                    "# of Observations Used"
                ]
                adf_test = adfuller(data_train[f"{feature} diff"].dropna(), autolag = "AIC")
                results = pd.Series(adf_test[0:4], index = indices)
                for key, value in adf_test[4].items():
                    results[f"Critical Value ({key})"] = value
                container2.text(results)
                container2.write("$$\\huge{\\textbf{KPSS Test}}$$")
                indices = [
                    "Test Statistic",
                    "p-value",
                    "# of Lags"
                ]
                kpss_test = kpss(data_train[f"{feature} diff"].dropna(), regression = "c")
                results = pd.Series(kpss_test[0:3], index = indices)
                for key, value in kpss_test[3].items():
                    results[f"Critical Value ({key})"] = value
                container2.text(results)
            #ARIMA MODELS TRAINING
            arima_111 = ARIMA(
                data_train[f"{feature} log"],
                order = (1, 1, 1)
            ).fit()
            arima_212 = ARIMA(
                data_train[f"{feature} log"],
                order = (2, 1, 2)
            ).fit()
            #DATA FOR PLOTTING
            arima_data = pd.DataFrame()
            arima_data["pred_111_log"] = arima_111.fittedvalues.tolist() + arima_111.forecast(TEST_LENGTH).tolist()
            arima_data["pred_111"] = np.exp(arima_data["pred_111_log"])
            arima_data["pred_212_log"] = arima_212.fittedvalues.tolist() + arima_212.forecast(TEST_LENGTH).tolist()
            arima_data["pred_212"] = np.exp(arima_data["pred_212_log"])
            arima_data.index = data_yf2.index
            with st.expander(
                label = "ARIMA - Summary"
            ):
                cols = st.columns(2)
                with cols[0]:
                    st.write("#### **ARIMA(1,1,1)**")
                    st.text(arima_111.summary())
                with cols[1]:
                    st.write("#### **ARIMA(2,1,2)**")
                    st.text(arima_212.summary())
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x = data_yf2.index,
                    y = data_yf2[feature],
                    mode = "lines",
                    name = feature
                )
            )
            fig.add_trace(
                go.Scatter(
                    x = arima_data.index,
                    y = arima_data["pred_111"],
                    mode = "lines",
                    name = "ARIMA(1,1,1)"
                )
            )
            fig.add_trace(
                go.Scatter(
                    x = arima_data.index,
                    y = arima_data["pred_212"],
                    mode = "lines",
                    name = "ARIMA(2,1,2)"
                )
            )
            grid3 = grid([4, 1], vertical_align = True)
            container4 = grid3.container()
            container4.plotly_chart(
                fig,
                use_container_width = True
            )
            container5 = grid3.container()
            mape_111 = mean_absolute_percentage_error(
                data_yf[feature].iloc[-TEST_LENGTH:],
                arima_data["pred_111"].iloc[-TEST_LENGTH:]
            )
            mape_212 = mean_absolute_percentage_error(
                data_yf[feature].iloc[-TEST_LENGTH:],
                arima_data["pred_212"].iloc[-TEST_LENGTH:]
            )
            container5.write("### **Mean Absolute Percentage Error (MAPE)**")
            container5.metric(
                label = "MAPE of ARIMA(1,1,1)",
                value = f"{100 * mape_111:.2f}%"
            )
            container5.metric(
                label = "MAPE of ARIMA(2,1,2)",
                value = f"{100 * mape_212:.2f}%"
            )
        except:
            st.error("Not enough data to process. Choose another financial asset.")
with main_tabs[3]:
    st.write("$$\\underline{\\huge{\\textbf{ANOMALY DETECTION}}}$$")
    grid1 = grid(2, vertical_align = True)
    feature = grid1.selectbox(
        label = "Feature",
        options = [
            "Open", 
            "High", 
            "Low", 
            "Close", 
            "Adj Close", 
            "Volume"
            ],
        index = 4,
        key = "feature5"
    )
    ad_model = grid1.selectbox(
        label = "Anomaly Detection Model",
        options = [
            "Seasonal",
            "Threshold",
            "Quantile",
            "Inter Quartile Range",
            "Generalized Extreme Studentized Deviate (ESD)",
            "Persist"
            ]
    )
    try:
        idx = pd.date_range(data_yf.index[0], data_yf.index[-1])
        data = data_yf[feature].reindex(idx)
        data = data.fillna(method = "ffill")
        ad_data = validate_series(data)
        if ad_model == "Seasonal":
            try:
                seasonal_ad = SeasonalAD()
                anomalies = seasonal_ad.fit_detect(ad_data)
                anomalies = anomalies[anomalies == True]
                anomalies = data_yf[data_yf.index.isin(anomalies.index)][feature]
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x = data_yf.index,
                        y = data_yf[feature],
                        mode = "lines",
                        name = feature
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x = anomalies.index,
                        y = anomalies,
                        mode = "markers",
                        marker = {
                            "color": "red"
                        },
                        name = "Anomalies"
                    )
                )
                st.plotly_chart(
                    fig,
                    use_container_width = True
                )
            except:
                st.error("No seasonality pattern found. Choose another model.")
        elif ad_model == "Threshold":
            grid2 = grid(2, vertical_align = True)
            low_threshold = grid2.slider(
                label = "Low (Threshold)",
                min_value = float(data_yf[feature].min()),
                max_value = float(data_yf[feature].max()),
                value = data_yf[feature].min() + (data_yf[feature].max() - data_yf[feature].min())*0.25
            )
            high_threshold = grid2.slider(
                label = "High (Threshold)",
                min_value = float(data_yf[feature].min()),
                max_value = float(data_yf[feature].max()),
                value = data_yf[feature].min() + (data_yf[feature].max() - data_yf[feature].min())*0.75
            )
            threshold_ad = ThresholdAD(
                high = high_threshold,
                low = low_threshold
            )
            anomalies = threshold_ad.detect(ad_data)
            anomalies = anomalies[anomalies == True]
            anomalies = data_yf[data_yf.index.isin(anomalies.index)][feature]
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x = data_yf.index,
                    y = data_yf[feature],
                    mode = "lines",
                    name = feature
                )
            )
            fig.add_trace(
                go.Scatter(
                    x = anomalies.index,
                    y = anomalies,
                    mode = "markers",
                    marker = {
                        "color": "red"
                    },
                    name = "Anomalies"
                )
            )
            st.plotly_chart(
                fig,
                use_container_width = True
            )
        elif ad_model == "Quantile":
            grid2 = grid(2, vertical_align = True)
            low_threshold = grid2.slider(
                label = "Low (Quantile)",
                min_value = 0.0,
                max_value = 1.0,
                value = 0.01
            )
            high_threshold = grid2.slider(
                label = "High (Quantile)",
                min_value = 0.0,
                max_value = 1.0,
                value = 0.99
            )
            quantile_ad = QuantileAD(
                high = high_threshold,
                low = low_threshold
            )
            anomalies = quantile_ad.fit_detect(ad_data)
            anomalies = anomalies[anomalies == True]
            anomalies = data_yf[data_yf.index.isin(anomalies.index)][feature]
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x = data_yf.index,
                    y = data_yf[feature],
                    mode = "lines",
                    name = feature
                )
            )
            fig.add_trace(
                go.Scatter(
                    x = anomalies.index,
                    y = anomalies,
                    mode = "markers",
                    marker = {
                        "color": "red"
                    },
                    name = "Anomalies"
                )
            )
            st.plotly_chart(
                fig,
                use_container_width = True
            )
        elif ad_model == "Inter Quartile Range":
            grid2 = grid(1, vertical_align = True)
            IQR = grid2.slider(
                label = "Inter Quartile Range",
                min_value = 0.0,
                max_value = 3.0,
                value = 0.0
            )
            interquartile_ad = InterQuartileRangeAD(
                c = IQR
            )
            anomalies = interquartile_ad.fit_detect(ad_data)
            anomalies = anomalies[anomalies == True]
            anomalies = data_yf[data_yf.index.isin(anomalies.index)][feature]
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x = data_yf.index,
                    y = data_yf[feature],
                    mode = "lines",
                    name = feature
                )
            )
            fig.add_trace(
                go.Scatter(
                    x = anomalies.index,
                    y = anomalies,
                    mode = "markers",
                    marker = {
                        "color": "red"
                    },
                    name = "Anomalies"
                )
            )
            st.plotly_chart(
                fig,
                use_container_width = True
            )
        elif ad_model == "Generalized Extreme Studentized Deviate (ESD)":
            grid2 = grid(1, vertical_align = True)
            alpha = grid2.slider(
                label = "Alpha",
                min_value = 0.0,
                max_value = 1.0,
                value = 0.3,
                step = 0.1
            )
            gesd_ad = GeneralizedESDTestAD(
                alpha = alpha
            )
            anomalies = gesd_ad.fit_detect(ad_data)
            anomalies = anomalies[anomalies == True]
            anomalies = data_yf[data_yf.index.isin(anomalies.index)][feature]
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x = data_yf.index,
                    y = data_yf[feature],
                    mode = "lines",
                    name = feature
                )
            )
            fig.add_trace(
                go.Scatter(
                    x = anomalies.index,
                    y = anomalies,
                    mode = "markers",
                    marker = {
                        "color": "red"
                    },
                    name = "Anomalies"
                )
            )
            st.plotly_chart(
                fig,
                use_container_width = True
            )
        elif ad_model == "Persist":
            grid2 = grid(2, vertical_align = True)
            c = grid2.slider(
                label = "C",
                min_value = 0.0,
                max_value = 5.0,
                value = 3.0
            )
            side = grid2.selectbox(
                label = "Side",
                options = [
                    "positive",
                    "negative"
                ]
            )
            persist_ad = PersistAD(c = c, side = side)
            anomalies = persist_ad.fit_detect(ad_data)
            anomalies = anomalies[anomalies == True]
            anomalies = data_yf[data_yf.index.isin(anomalies.index)][feature]
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x = data_yf.index,
                    y = data_yf[feature],
                    mode = "lines",
                    name = feature
                )
            )
            fig.add_trace(
                go.Scatter(
                    x = anomalies.index,
                    y = anomalies,
                    mode = "markers",
                    marker = {
                        "color": "red"
                    },
                    name = "Anomalies"
                )
            )
            st.plotly_chart(
                fig,
                use_container_width = True
            )
    except:
        st.error("Not enough data to process. Choose another financial asset.")  