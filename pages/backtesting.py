import vectorbt as vbt
import streamlit as st 
import pandas as pd
import numpy as np
import datetime as dt
import pytz
import json
from streamlit_extras.grid import grid
import plotly.graph_objects as go
import plotly.express as px
from functions import (
    binance_filter_func,
    get_binance_data,
    option_menu,
    image_border_radius,
    page_buttons,
)

PAGE_TITLE = "COELHO Finance | Backtesting"
st.set_page_config(
    page_title = PAGE_TITLE,
    layout = "wide",
    initial_sidebar_state = "collapsed"
)

option_menu()

grid_title = grid([5, 1], vertical_align = True)
container1 = grid_title.container()
container1.title("$$\\large{\\textbf{COELHO Finance | Backtesting}}$$")
container1.caption("Author: Rafael Silva Coelho")
image_border_radius("./assets/coelho_finance_logo.png", 15, 60, 60, grid_title)

page_buttons()

time_buffer = dt.timedelta(days = 100)  # buffer before to pre-calculate SMA/EMA, best to set to max window
metric = 'total_return'
with open("./data/periods_and_intervals_binance.json", "r") as f:
    intervals_binance = json.load(f)

layout = grid([1, 0.2, 3], vertical_align = True)
filter_bar = layout.container()
layout.container()
display = layout.container()

filter_bar.latex("\\textbf{Filters}")
data_source_filter = filter_bar.selectbox(
    label = "Data source",
    placeholder = "Data source",
    options = [
        "Binance",
        "CCXT",
        "Yahoo Finance"
    ],
    index = 0,
    key = "data_source_filter")
if data_source_filter == "Binance":
    (
        symbol,
        start_date,
        start_hour,
        end_date,
        end_hour,
        feature,
        interval
    ) = binance_filter_func(filter_bar)
    data_wbuf = get_binance_data(
        symbol,
        start_date - time_buffer,
        start_hour,
        end_date,
        end_hour,
        interval
        ).get()
    # Create a copy of data without time buffer
    start_date_tz = dt.datetime(start_date.year, start_date.month, start_date.day, tzinfo = pytz.utc)
    end_date_tz = dt.datetime(end_date.year, end_date.month, end_date.day, tzinfo = pytz.utc)
    wobuf_mask = (data_wbuf.index >= start_date_tz) & (data_wbuf.index <= end_date_tz) # mask without buffer
    data = data_wbuf.loc[wobuf_mask, :]

display.latex("\\Large{\\text{" + symbol.replace("^", "").replace("&", "\\&") + "}}")
display.divider()

tabs = display.tabs([
    "$$\\textbf{GENERAL}$$",
    "$$\\textbf{STRATEGIES}$$",
])
with tabs[0]: #GENERAL
    st.latex("\\textbf{\\Large{Open, High, Low, Close, Volume (OHLCV) chart}}")
    ohlcv = data[["Open", "High", "Low", "Close", "Volume"]].astype(np.float64)
    st.plotly_chart(
        ohlcv.vbt.ohlcv.plot(),
        use_container_width = True
    )
with tabs[1]: #STRATEGIES
    subtabs = st.tabs([
        "$$\\textbf{DMAC}$$",
    ])
    with subtabs[0]:
        st.latex("\\textbf{\\Large{Dual Moving Average Crossover (DMAC)}}")
        dmac_filters = grid(3, vertical_align = True)
        init_cash = dmac_filters.number_input(
            label = "Initial cash",
            value = 100.00,
            min_value = -0.00
        )
        fees = dmac_filters.number_input(
            label = "Fees (%)",
            value = 0.25,
            min_value = -0.00
        )
        slippage = dmac_filters.number_input(
            label = "Slippage (%)",
            value = 0.25,
            min_value = -0.00
        )
        ma_windows_filters = grid(2, vertical_align = True)
        fast_window = ma_windows_filters.number_input(
            label = "Fast window",
            value = int(len(data.index) / 6),
            min_value = 1,
            max_value = len(data.index),
            step = 1
        )
        slow_window = ma_windows_filters.number_input(
            label = "Slow window",
            value = int(len(data.index) / 3),
            min_value = fast_window,
            max_value = len(data.index),
            step = 1
        )
        #SETTINGS
        vbt.settings.portfolio["init_cash"] = init_cash
        vbt.settings.portfolio["fees"] = fees / 100
        vbt.settings.portfolio["slippage"] = slippage / 100
        fast_ma = vbt.MA.run(data_wbuf["Open"], fast_window)
        slow_ma = vbt.MA.run(data_wbuf["Open"], slow_window)
        # Remove time buffer
        fast_ma = fast_ma[wobuf_mask]
        slow_ma = slow_ma[wobuf_mask]
        # Generate crossover signals
        dmac_entries = fast_ma.ma_crossed_above(slow_ma)
        dmac_exits = fast_ma.ma_crossed_below(slow_ma)
        dmac_pf = vbt.Portfolio.from_signals(data["Close"], dmac_entries, dmac_exits)
        # Now build portfolio for a "Hold" strategy
        # Here we buy once at the beginning and sell at the end
        hold_entries = pd.Series.vbt.signals.empty_like(dmac_entries)
        hold_entries.iloc[0] = True
        hold_exits = pd.Series.vbt.signals.empty_like(hold_entries)
        hold_exits.iloc[-1] = True
        hold_pf = vbt.Portfolio.from_signals(ohlcv['Close'], hold_entries, hold_exits)
        dmac_tabs = st.tabs([
            "$$\\textbf{Strategy}$$",
            "$$\\textbf{Signal}$$",
            "$$\\textbf{Trades}$$",
            "$$\\textbf{Hold strategy}$$",
            "$$\\textbf{Statistics}$$",
            "$$\\textbf{Multiple windows}$$",
        ])
        with dmac_tabs[0]:
            st.latex("\\textbf{Strategy}")
            fig = data[feature].vbt.plot(trace_kwargs=dict(name=f'Price (Open)'))
            fig = fast_ma.ma.vbt.plot(trace_kwargs=dict(name='Fast MA'), fig=fig)
            fig = slow_ma.ma.vbt.plot(trace_kwargs=dict(name='Slow MA'), fig=fig)
            fig = dmac_entries.vbt.signals.plot_as_entry_markers(data[feature], fig=fig)
            fig = dmac_exits.vbt.signals.plot_as_exit_markers(data[feature], fig=fig)
            st.plotly_chart(
                fig,
                use_container_width = True)
        with dmac_tabs[1]:
            # Plot signals
            st.latex("\\textbf{Signal}")
            fig2 = dmac_entries.vbt.signals.plot(trace_kwargs=dict(name='Entries'))
            dmac_exits.vbt.signals.plot(trace_kwargs=dict(name='Exits'), fig=fig2)
            st.plotly_chart(
                fig2,
                use_container_width = True
            )
        with dmac_tabs[2]:
            # Plot trades
            st.latex("\\textbf{Trades}")
            st.plotly_chart(
                dmac_pf.trades.plot(),
                use_container_width = True)
        with dmac_tabs[3]:
            # Equity (Hold strategy)
            st.latex("\\textbf{Hold strategy}")
            fig3 = dmac_pf.value().vbt.plot(trace_kwargs=dict(name='Value (DMAC)'))
            hold_pf.value().vbt.plot(trace_kwargs=dict(name='Value (Hold)'), fig=fig3)
            st.plotly_chart(
                fig3,
                use_container_width = True
            )
        with dmac_tabs[4]:
            st.latex("\\textbf{Statistics}")
            statistics = grid(2, vertical_align = True)
            statistics.write("$$\\textbf{Signal statistics}$$")
            statistics.write("$$\\textbf{Portfolio statistics}$$")
            statistics.text(dmac_entries.vbt.signals.stats(
                settings = dict(other = dmac_exits)))
            # Build partfolio, which internally calculates the equity curve
            statistics.text(dmac_pf.stats())
        with dmac_tabs[5]:
            st.latex("\\textbf{Multiple windows}")
            max_window = st.slider(
                label = " Windows maximum number",
                min_value = 2,
                max_value = 100,
                value = 100,
                step = 1
            )
            # Pre-calculate running windows on data with time buffer
            fast_ma, slow_ma = vbt.MA.run_combs(
                data_wbuf["Open"], 
                np.arange(2, max_window + 1), 
                r = 2, 
                short_names = ['fast_ma', 'slow_ma'])
            # Remove time buffer
            fast_ma = fast_ma[wobuf_mask]
            slow_ma = slow_ma[wobuf_mask]
            # Each column corresponds to a pair of fast and slow windows
            # Generate crossover signals
            dmac_entries = fast_ma.ma_crossed_above(slow_ma)
            dmac_exits = fast_ma.ma_crossed_below(slow_ma)
            # Build portfolio
            dmac_pf = vbt.Portfolio.from_signals(ohlcv['Close'], dmac_entries, dmac_exits)
            # Calculate performance of each window combination
            dmac_perf = dmac_pf.deep_getattr(metric)
            # Convert this array into a matrix of shape (99, 99): 99 fast windows x 99 slow windows
            dmac_perf_matrix = dmac_perf.vbt.unstack_to_df(
                symmetric = True, 
                index_levels = 'fast_ma_window', 
                column_levels = 'slow_ma_window')
            fig4 = dmac_perf_matrix.vbt.heatmap(
                    xaxis_title='Slow window', 
                    yaxis_title='Fast window')
            fig4.update_layout(width = 800, height = 600)
            st.plotly_chart(fig4)

