import vectorbt as vbt
import pandas as pd
import numpy as np
import datetime as dt
import pytz
import json
import gc
from itertools import combinations, product
import streamlit as st 
from streamlit_extras.grid import grid
from streamlit_extras.metric_cards import style_metric_cards
from stqdm import stqdm
from functions import (
    binance_filter_func,
    ccxt_filter_func,
    binance_symbols,
    ccxt_symbols,
    get_binance_data,
    get_ccxt_data,
    get_expectancy,
    bin_return,
    roll_in_and_out_samples,
    simulate_holding,
    simulate_all_params,
    get_best_index,
    get_best_params,
    simulate_best_params,
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
_binance_symbols = binance_symbols()
_ccxt_symbols = ccxt_symbols()
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
    ) = binance_filter_func(
        filter_bar,
        _binance_symbols)
    data_wbuf = get_binance_data(
        symbol,
        start_date - time_buffer,
        start_hour,
        end_date,
        end_hour,
        ).get()
    # Create a copy of data without time buffer
    start_date_tz = dt.datetime(start_date.year, start_date.month, start_date.day, tzinfo = pytz.utc)
    end_date_tz = dt.datetime(end_date.year, end_date.month, end_date.day, tzinfo = pytz.utc)
    wobuf_mask = (data_wbuf.index >= start_date_tz) & (data_wbuf.index <= end_date_tz) # mask without buffer
    data = data_wbuf.loc[wobuf_mask, :]
    vbt.settings.array_wrapper['freq'] = intervals_binance[0]["interval"]["1 day"]
elif data_source_filter == "CCXT":
    (
        symbol,
        start_date,
        start_hour,
        end_date,
        end_hour,
        feature,
    ) = ccxt_filter_func(
        filter_bar,
        _ccxt_symbols)
    data_wbuf = get_ccxt_data(
        symbol,
        start_date - time_buffer,
        start_hour,
        end_date,
        end_hour,
        ).get()
    # Create a copy of data without time buffer
    start_date_tz = dt.datetime(start_date.year, start_date.month, start_date.day, tzinfo = pytz.utc)
    end_date_tz = dt.datetime(end_date.year, end_date.month, end_date.day, tzinfo = pytz.utc)
    wobuf_mask = (data_wbuf.index >= start_date_tz) & (data_wbuf.index <= end_date_tz) # mask without buffer
    data = data_wbuf.loc[wobuf_mask, :]
    vbt.settings.array_wrapper['freq'] = intervals_binance[0]["interval"]["1 day"]

tabs = display.tabs([
    "$$\\textbf{GENERAL}$$",
    "$$\\textbf{STRATEGIES}$$",
    "$$\\textbf{STOP LOSS}$$",
])

with tabs[0]: #GENERAL
    st.latex("\\Large{\\text{" + symbol.replace("^", "").replace("&", "\\&") + "}}")
    st.latex("\\textbf{\\Large{Open, High, Low, Close, Volume (OHLCV) chart}}")
    ohlcv = data[["Open", "High", "Low", "Close", "Volume"]].astype(np.float64)
    st.plotly_chart(
        ohlcv.vbt.ohlcv.plot(),
        use_container_width = True
    )
with tabs[1]: #STRATEGIES
    st.latex("\\Large{\\text{" + symbol.replace("^", "").replace("&", "\\&") + "}}")
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
    fast_window = ma_windows_filters.slider(
        label = "Fast window",
        value = 10, #int(len(data.index) / 6),
        min_value = 1,
        max_value = len(data.index),
        step = 1
    )
    slow_window = ma_windows_filters.slider(
        label = "Slow window",
        value = 30, #int(len(data.index) / 3),
        min_value = fast_window,
        max_value = len(data.index),
        step = 1
    )
    subtabs = st.tabs([
        "$$\\textbf{DMAC}$$",
        "$$\\textbf{MACD}$$",
        "$$\\textbf{RSI}$$",
        "$$\\textbf{Walk-Forward Optimization}$$",
    ])
    with subtabs[0]:
        st.latex("\\textbf{\\Large{Dual Moving Average Crossover (DMAC)}}")
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
            "$$\\textbf{Results}$$",
            "$$\\textbf{Statistics}$$",
            "$$\\textbf{Strategy}$$",
            "$$\\textbf{Signal}$$",
            "$$\\textbf{Trades}$$",
            "$$\\textbf{Hold strategy}$$",
            "$$\\textbf{Multiple windows}$$",
        ])
        with dmac_tabs[0]:
            st.latex("\\textbf{Results}")
            dmac_metrics = grid(4, vertical_align = True)
            dmac_metrics.metric(
                label = "Start Value",
                value = dmac_pf.stats()["Start Value"],
            )
            dmac_metrics.metric(
                label = "End Value",
                value = f'{dmac_pf.stats()["End Value"]:.2f}',
                delta = f'{(dmac_pf.stats()["End Value"] - dmac_pf.stats()["Start Value"]):.2f}'
            )
            dmac_metrics.metric(
                label = "Total Return",
                value = f'{dmac_pf.stats()["Total Return [%]"]:.2f}%',
            )
            dmac_metrics.metric(
                label = "Total Fees Paid",
                value = f'{dmac_pf.stats()["Total Fees Paid"]:.2f}',
            )
            dmac_metrics2 = grid(5, vertical_align = True)
            for x in [
                "Expectancy",
                "Sharpe Ratio",
                "Calmar Ratio",
                "Omega Ratio",
                "Sortino Ratio"
            ]:
                dmac_metrics2.metric(
                    label = x,
                    value = f'{dmac_pf.stats()[x]:.2f}',
                )
            style_metric_cards(
                background_color = "#000000"
            )
            st.plotly_chart(
                dmac_pf.plot(), 
                use_container_width = True)
        with dmac_tabs[1]:
            st.latex("\\textbf{Statistics}")
            st.write("$$\\textbf{Portfolio statistics}$$")
            # Build partfolio, which internally calculates the equity curve
            st.text(
                dmac_pf.stats())
        with dmac_tabs[2]:
            st.latex("\\textbf{Strategy}")
            fig = data[feature].vbt.plot(trace_kwargs=dict(name=f'Price ({feature})'))
            fig = fast_ma.ma.vbt.plot(trace_kwargs=dict(name='Fast MA'), fig=fig)
            fig = slow_ma.ma.vbt.plot(trace_kwargs=dict(name='Slow MA'), fig=fig)
            fig = dmac_entries.vbt.signals.plot_as_entry_markers(data[feature], fig=fig)
            fig = dmac_exits.vbt.signals.plot_as_exit_markers(data[feature], fig=fig)
            st.plotly_chart(
                fig,
                use_container_width = True)
        with dmac_tabs[3]:
            # Plot signals
            st.latex("\\textbf{Signal}")
            fig2 = dmac_entries.vbt.signals.plot(trace_kwargs=dict(name='Entries'))
            dmac_exits.vbt.signals.plot(trace_kwargs=dict(name='Exits'), fig=fig2)
            st.plotly_chart(
                fig2,
                use_container_width = True
            )
        with dmac_tabs[4]:
            # Plot trades
            st.latex("\\textbf{Trades}")
            st.plotly_chart(
                dmac_pf.trades.plot(),
                use_container_width = True)
        with dmac_tabs[5]:
            # Equity (Hold strategy)
            st.latex("\\textbf{Hold strategy}")
            fig3 = dmac_pf.value().vbt.plot(trace_kwargs=dict(name='Value (DMAC)'))
            hold_pf.value().vbt.plot(trace_kwargs=dict(name='Value (Hold)'), fig=fig3)
            st.plotly_chart(
                fig3,
                use_container_width = True
            )
        with dmac_tabs[6]:
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
    with subtabs[1]:
        st.latex("\\textbf{\\Large{Moving Average Convergence/Divergence (MACD) Volume}}")
        price = data.get("Close")
        price, _ = price.vbt.range_split(n = 3)
        # Define hyper-parameter space
        # 49 fast x 49 slow x 19 signal
        fast_windows, slow_windows, signal_windows = vbt.utils.params.create_param_combs(
            (product, (combinations, np.arange(2, 51, 1), 2), np.arange(2, 21, 1)))
        # Run MACD indicator
        macd_ind = vbt.MACD.run(
            price,
            fast_window=fast_windows,
            slow_window=slow_windows,
            signal_window=signal_windows
        )
        # Long when MACD is above zero AND signal
        entries = macd_ind.macd_above(0) & macd_ind.macd_above(macd_ind.signal)
        # Short when MACD is below zero OR signal
        exits = macd_ind.macd_below(0) | macd_ind.macd_below(macd_ind.signal)
        # Build portfolio
        pf = vbt.Portfolio.from_signals(
            price.vbt.tile(len(fast_windows)), 
            entries, 
            exits, 
            fees = fees, 
            freq = intervals_binance[0]["interval"]["1 day"])
        # Draw all window combinations as a 3D volume
        fig5 = pf.total_return().vbt.volume(
            x_level='macd_fast_window',
            y_level='macd_slow_window',
            z_level='macd_signal_window',
            slider_level='split_idx',
            trace_kwargs=dict(
                colorbar=dict(
                    title='Total return', 
                    tickformat='%'
                )
            )
        )
        st.plotly_chart(
            fig5,
            use_container_width = True
        )
    with subtabs[2]:
        st.latex("\\textbf{\\Large{Relative Strength Index (RSI)}}")
        rsi = vbt.RSI.run(data.get("Close"))
        rsi_filters = grid(2, vertical_align = True)
        rsi_low = rsi_filters.slider(
            label = "RSI (low)",
            value = 50,
            min_value = 0,
            max_value = 100,
            step = 1
        )
        rsi_high = rsi_filters.slider(
            label = "RSI (high)",
            value = 50,
            min_value = rsi_low,
            max_value = 100,
            step = 1
        )
        fast_ma = vbt.MA.run(data.get("Close"), fast_window)
        slow_ma = vbt.MA.run(data.get("Close"), slow_window)
        entries = fast_ma.ma_crossed_above(slow_ma) & rsi.rsi_above(rsi_high)
        exits = slow_ma.ma_crossed_above(fast_ma) & rsi.rsi_below(rsi_low)
        pf = vbt.Portfolio.from_signals(
            data.get("Close"), 
            entries, 
            exits, 
            init_cash = init_cash,
            fees = fees,
            slippage = slippage)
        rsi_tabs = st.tabs([
            "$$\\textbf{Results}$$",
            "$$\\textbf{Statistics}$$",
        ])
        with rsi_tabs[0]:
            st.latex("\\textbf{Results}")
            rsi_metrics = grid(4, vertical_align = True)
            rsi_metrics.metric(
                label = "Start Value",
                value = pf.stats()["Start Value"],
            )
            rsi_metrics.metric(
                label = "End Value",
                value = f'{pf.stats()["End Value"]:.2f}',
                delta = f'{(pf.stats()["End Value"] - pf.stats()["Start Value"]):.2f}'
            )
            rsi_metrics.metric(
                label = "Total Return",
                value = f'{pf.stats()["Total Return [%]"]:.2f}%',
            )
            rsi_metrics.metric(
                label = "Total Fees Paid",
                value = f'{pf.stats()["Total Fees Paid"]:.2f}',
            )
            rsi_metrics2 = grid(5, vertical_align = True)
            for x in [
                "Expectancy",
                "Sharpe Ratio",
                "Calmar Ratio",
                "Omega Ratio",
                "Sortino Ratio"
            ]:
                rsi_metrics2.metric(
                    label = x,
                    value = f'{pf.stats()[x]:.2f}',
                )
            style_metric_cards(
                background_color = "#000000"
            )
            st.plotly_chart(pf.plot(), use_container_width = True)
        with rsi_tabs[1]:
            st.latex("\\textbf{Statistics}")
            st.text(pf.stats())
    with subtabs[3]:
        st.latex("\\textbf{\\Large{Walk-Forward Optimization}}")
        wfo_filters = grid(1, vertical_align = True)
        number_of_windows = wfo_filters.number_input(
            label = "Number of windows",
            value = 30,
            min_value = 1,
            max_value = 30,
            step = 1
        )
        split_kwargs = dict(
            n = number_of_windows, 
            window_len = int((end_date - start_date).days * 0.2881), 
            set_lens = (int((end_date - start_date).days * 0.0710), ), 
            left_to_right = False
        )
        pf_kwargs = dict(
            direction = 'both',  # long and short
            freq = intervals_binance[0]["interval"]["1 day"]
        )
        windows = np.arange(10, 50)
        price = data.get("Close")
        st.plotly_chart(
            roll_in_and_out_samples(
                price, 
                **split_kwargs, 
                plot = True, 
                trace_names = ['in-sample', 'out-sample']),
            use_container_width = True
        )
        (in_price, in_indexes), (out_price, out_indexes) = roll_in_and_out_samples(
            price, 
            **split_kwargs)
        in_hold_sharpe = simulate_holding(in_price, **pf_kwargs)
        # Simulate all params for in-sample ranges
        in_sharpe = simulate_all_params(in_price, windows, **pf_kwargs)
        in_best_index = get_best_index(in_sharpe)
        in_best_fast_windows = get_best_params(in_best_index, 'fast_window')
        in_best_slow_windows = get_best_params(in_best_index, 'slow_window')
        in_best_window_pairs = np.array(list(zip(in_best_fast_windows, in_best_slow_windows)))
        st.plotly_chart(
            pd.DataFrame(
                in_best_window_pairs, 
                columns = ['fast_window', 'slow_window']).vbt.plot(),
            use_container_width = True
        )
        out_hold_sharpe = simulate_holding(out_price, **pf_kwargs)
        # Simulate all params for out-sample ranges
        out_sharpe = simulate_all_params(out_price, windows, **pf_kwargs)
        # Use best params from in-sample ranges and simulate them for out-sample ranges
        out_test_sharpe = simulate_best_params(
            out_price, in_best_fast_windows, in_best_slow_windows, **pf_kwargs)
        cv_results_df = pd.DataFrame({
            'in_sample_hold': in_hold_sharpe.values,
            'in_sample_median': in_sharpe.groupby('split_idx').median().values,
            'in_sample_best': in_sharpe[in_best_index].values,
            'out_sample_hold': out_hold_sharpe.values,
            'out_sample_median': out_sharpe.groupby('split_idx').median().values,
            'out_sample_test': out_test_sharpe.values
        })
        color_schema = vbt.settings['plotting']['color_schema']
        st.plotly_chart(
            cv_results_df.vbt.plot(
                trace_kwargs=[
                    dict(line_color=color_schema['blue']),
                    dict(line_color=color_schema['blue'], line_dash='dash'),
                    dict(line_color=color_schema['blue'], line_dash='dot'),
                    dict(line_color=color_schema['orange']),
                    dict(line_color=color_schema['orange'], line_dash='dash'),
                    dict(line_color=color_schema['orange'], line_dash='dot')
                ]
            ),
        use_container_width = True
        )
with tabs[2]:
    st.latex("\\textbf{\\Large{Stop Loss}}")
    if data_source_filter == "Binance":
        symbols = st.multiselect(
            label = "Symbols",
            options = sorted(_binance_symbols),
            default = [
                'BTCUSDT', 
                'ETHUSDT', 
                'XRPUSDT', 
                'BCHUSDT', 
                'LTCUSDT', 
                'BNBUSDT', 
                'EOSUSDT', 
                'XLMUSDT', 
                'XMRUSDT', 
                'ADAUSDT'
            ],
            key = "symbols1")
    elif data_source_filter == "CCXT":
        symbols = st.multiselect(
            label = "Symbols",
            options = sorted(_ccxt_symbols),
            default = [
                'BTC/USDT:USDT', 
                'ETH/USDT:USDT', 
                'XRP/USDT:USDT', 
                'BCH/USDT:USDT', 
                'LTC/USDT:USDT', 
                'BNB/USDT:USDT', 
                'EOS/USDT:USDT', 
                'XLM/USDT:USDT', 
                'XMR/USDT:USDT', 
                'ADA/USDT:USDT'
            ],
            key = "symbols1")
    time_delta = end_date_tz - start_date_tz
    window_len = dt.timedelta(days = int((end_date_tz - start_date_tz).days * 0.1644))
    window_count = int((end_date_tz - start_date_tz).days * 0.3653)
    exit_types = ['SL', 'TS', 'TP', 'Random', 'Holding']
    sl_filters = grid(4, vertical_align = True)
    init_cash = sl_filters.number_input(
        label = "Initial cash",
        value = 100.00,
        min_value = -0.00,
        key = "init_cash2"
    )
    fees = sl_filters.number_input(
        label = "Fees (%)",
        value = 0.25,
        min_value = -0.00,
        key = "fees2"
    )
    slippage = sl_filters.number_input(
        label = "Slippage (%)",
        value = 0.25,
        min_value = -0.00,
        key = "slippage2"
    )
    step = sl_filters.number_input(
        label = "Step",
        value = 0.01,
        min_value = -0.00,
        max_value = 1.00,
        key = "step2"
    )
    stops = np.arange(step, 1 + step, step)
    ma_windows_filters = grid(2, vertical_align = True)
    fast_window = ma_windows_filters.slider(
        label = "Fast window",
        value = 10, #int(len(data.index) / 6),
        min_value = 1,
        max_value = len(data.index),
        step = 1,
        key = "maf2"
    )
    slow_window = ma_windows_filters.slider(
        label = "Slow window",
        value = 30, #int(len(data.index) / 3),
        min_value = fast_window,
        max_value = len(data.index),
        step = 1,
        key = "mas2"
    )
    vbt.settings.array_wrapper['freq'] = intervals_binance[0]["interval"]["1 day"]
    vbt.settings.plotting['layout']['template'] = 'vbt_dark'
    vbt.settings.portfolio['init_cash'] = init_cash  # 100$
    vbt.settings.portfolio['fees'] = fees  # 0.25%
    vbt.settings.portfolio['slippage'] = slippage  # 0.25%
    data_sl = get_ccxt_data(
        symbols,
        start_date,
        start_hour,
        end_date,
        end_hour,
    )
    stop_loss_tabs = st.tabs([
        "$$\\textbf{Stop Loss / Trailing Stop / Take Profit}$$",
        "$$\\textbf{Total Return}$$",
        "$$\\textbf{Expectancy}$$",
        "$$\\textbf{Statistics}$$",
    ])
    with stop_loss_tabs[0]:
        st.latex("\\textbf{Stop Loss / Trailing Stop / Take Profit}")
        ohlcv = data_sl.concat()
        split_ohlcv = {}
        for k, v in ohlcv.items():
            split_df, split_indexes = v.vbt.range_split(
                range_len = window_len.days, 
                n = window_count) 
            split_ohlcv[k] = split_df
        ohlcv = split_ohlcv
        entries = pd.DataFrame.vbt.signals.empty_like(ohlcv['Open'])
        entries.iloc[0, :] = True
        # We use OHLCSTX instead of built-in stop-loss in Portfolio.from_signals
        # because we want to analyze signals before simulation + it's easier to construct param grids
        # For reality check, run the same setup using Portfolio.from_signals alone
        sl_exits = vbt.OHLCSTX.run(
            entries, 
            ohlcv['Open'], 
            ohlcv['High'], 
            ohlcv['Low'], 
            ohlcv['Close'], 
            sl_stop=list(stops),
            stop_type=None, 
            stop_price=None
        ).exits
        ts_exits = vbt.OHLCSTX.run(
            entries, 
            ohlcv['Open'], 
            ohlcv['High'], 
            ohlcv['Low'], 
            ohlcv['Close'], 
            sl_stop=list(stops),
            sl_trail=True,
            stop_type=None, 
            stop_price=None
        ).exits
        tp_exits = vbt.OHLCSTX.run(
            entries, 
            ohlcv['Open'], 
            ohlcv['High'], 
            ohlcv['Low'], 
            ohlcv['Close'], 
            tp_stop=list(stops),
            stop_type=None, 
            stop_price=None
        ).exits
        sl_exits.vbt.rename_levels({'ohlcstx_sl_stop': 'stop_value'}, inplace=True)
        ts_exits.vbt.rename_levels({'ohlcstx_sl_stop': 'stop_value'}, inplace=True)
        tp_exits.vbt.rename_levels({'ohlcstx_tp_stop': 'stop_value'}, inplace=True)
        ts_exits.vbt.drop_levels('ohlcstx_sl_trail', inplace=True)
        sl_exits.iloc[-1, :] = True
        ts_exits.iloc[-1, :] = True
        tp_exits.iloc[-1, :] = True
        # Select one exit between two entries
        sl_exits = sl_exits.vbt.signals.first(reset_by=entries, allow_gaps=True)
        ts_exits = ts_exits.vbt.signals.first(reset_by=entries, allow_gaps=True)
        tp_exits = tp_exits.vbt.signals.first(reset_by=entries, allow_gaps=True)
        hold_exits = pd.DataFrame.vbt.signals.empty_like(sl_exits)
        hold_exits.iloc[-1, :] = True
        rand_exits = hold_exits.vbt.shuffle(seed = 42)
        exits = pd.DataFrame.vbt.concat(
            sl_exits, 
            ts_exits, 
            tp_exits, 
            rand_exits, 
            hold_exits, 
            keys=pd.Index(exit_types, name='exit_type')
        )
        avg_distance = entries.vbt.signals.between_ranges(other=exits)\
            .duration.mean()\
            .groupby(['exit_type', 'stop_value'])\
            .mean()\
            .unstack(level='exit_type')
        st.plotly_chart(
            avg_distance[exit_types].vbt.plot(
                xaxis_title='Stop value', 
                yaxis_title='Avg distance to entry'
            ),
            use_container_width = True)
    with stop_loss_tabs[1]:
        st.latex("\\textbf{Total Return}")
        total_returns = []
        for i in stqdm(range(len(exit_types))):
            chunk_mask = exits.columns.get_level_values('exit_type') == exit_types[i]
            chunk_exits = exits.loc[:, chunk_mask]
            chunk_pf = vbt.Portfolio.from_signals(ohlcv['Close'], entries, chunk_exits)
            total_returns.append(chunk_pf.total_return())
            del chunk_pf
            gc.collect()
        total_return = pd.concat(total_returns)
        total_return_by_type = total_return.unstack(level='exit_type')[exit_types]
        st.plotly_chart(
            total_return_by_type['Holding'].vbt.histplot(
                xaxis_title='Total return',
                xaxis_tickformat='%',
                yaxis_title='Count',
                trace_kwargs=dict(marker_color=vbt.settings['plotting']['color_schema']['purple'])
            ),
            use_container_width = True)
        cols = st.columns(2)
        with cols[0]:
            st.plotly_chart(
                total_return_by_type.vbt.boxplot(
                    yaxis_title='Total return',
                    yaxis_tickformat='%'
                ),
                use_container_width = True)
        with cols[1]:
            st.latex("\\textbf{Total Return Statistics}")
            st.dataframe(
                pd.DataFrame({
                    'Mean': total_return_by_type.mean(),
                    'Median': total_return_by_type.median(),
                    'Std': total_return_by_type.std(),
                }),
                use_container_width = True)
    with stop_loss_tabs[2]:
        st.latex("\\textbf{Expectancy}")
        init_cash = vbt.settings.portfolio['init_cash']
        expectancy_by_stop = get_expectancy(total_return_by_type, 'stop_value', init_cash)
        st.plotly_chart(
            expectancy_by_stop.vbt.plot(
                xaxis_title='Stop value', 
                yaxis_title='Expectancy'
            ),
            use_container_width = True
        )
        st.latex("\\textbf{Expectancy by bins}")
        return_values = np.sort(total_return_by_type['Holding'].values)
        idxs = np.ceil(np.linspace(0, len(return_values) - 1, 21)).astype(int)
        bins = np.unique(return_values[idxs][:-1])
        binned_total_return_by_type = bin_return(total_return_by_type, bins)
        expectancy_by_bin = get_expectancy(binned_total_return_by_type, 'bin_right', init_cash)
        st.plotly_chart(
            expectancy_by_bin.vbt.plot(
                trace_kwargs=dict(mode='lines'),
                xaxis_title='Total return of holding',
                xaxis_tickformat='%',
                yaxis_title='Expectancy'
            ),
            use_container_width = True
        )
        win_rate = (total_return_by_type > 0).mean().rename('win_rate')
        st.text(win_rate)
    with stop_loss_tabs[3]:
        st.latex("\\textbf{Statistics}")
        cols = st.columns(3)
        with cols[0]:
            st.write("$$\\textbf{General statistics}$$")
            statistics1 = pd.Series({
                'Start date': start_date,
                'End date': end_date,
                'Time period (days)': time_delta.days,
                'Assets': len(symbols),
                'Window length': window_len,
                'Windows': window_count,
                'Exit types': len(exit_types),
                'Stop values': len(stops),
                'Tests per asset': window_count * len(stops) * len(exit_types),
                'Tests per window': len(symbols) * len(stops) * len(exit_types),
                'Tests per exit type': len(symbols) * window_count * len(stops),
                'Tests per stop type and value': len(symbols) * window_count,
                'Tests total': len(symbols) * window_count * len(stops) * len(exit_types)
            })
            st.text(statistics1)
        with cols[1]:
            st.write("$$\\textbf{Stop Loss, Trailing Stop, Take Profit}$$")
            statistics2 = pd.Series({
                'SL': sl_exits.vbt.signals.total().mean(),
                'TS': ts_exits.vbt.signals.total().mean(),
                'TP': tp_exits.vbt.signals.total().mean()
            }, name='avg_num_signals')
            st.text(statistics2)
        with cols[2]:
            st.write("$$\\textbf{Average distance to entry}$$")
            st.text(avg_distance.mean())