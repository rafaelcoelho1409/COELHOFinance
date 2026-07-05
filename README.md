<p align="center"><img src="assets/coelho_finance_logo.png" alt="COELHO Finance" width="200"></p>

<p align="center"><strong>Stocks, indices, bonds, funds, ETFs, currency crosses, and crypto across 40+ countries — with a real econometrics and quant-research toolkit behind every one of them.</strong></p>

<p align="center">
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white"></a>
  <a href="https://streamlit.io/"><img alt="Streamlit" src="https://img.shields.io/badge/streamlit-app-FF4B4B?logo=streamlit&logoColor=white"></a>
  <a href="https://www.cvxpy.org/"><img alt="cvxpy" src="https://img.shields.io/badge/cvxpy-portfolio%20optimization-6929c4"></a>
  <a href="https://arch.readthedocs.io/"><img alt="ARCH" src="https://img.shields.io/badge/ARCH-GARCH%20volatility-orange"></a>
  <a href="https://vectorbt.dev/"><img alt="vectorbt" src="https://img.shields.io/badge/vectorbt-backtesting-0f9d58"></a>
  <a href="https://github.com/ccxt/ccxt"><img alt="CCXT" src="https://img.shields.io/badge/CCXT-crypto%20exchanges-f7931a"></a>
</p>

<p align="center">
  <a href="https://coelhofinance.streamlit.app/">Live Demo</a> ·
  <a href="https://rafaelcoelho.pages.dev/work/coelho-finance">Portfolio Page</a> ·
  <a href="./COELHOFinance.pdf">PDF Presentation</a>
</p>

---

## Table of Contents

- [What is this?](#what-is-this)
- [The three live sections](#the-three-live-sections)
- [UNIMARKET: single-asset deep dive](#unimarket-single-asset-deep-dive)
- [UNISTATS: the econometrics toolkit](#unistats-the-econometrics-toolkit)
- [MULTIMARKET: comparison and portfolio theory](#multimarket-comparison-and-portfolio-theory)
- [Asset class and data source coverage](#asset-class-and-data-source-coverage)
- [Shipped but hidden: a full backtesting engine](#shipped-but-hidden-a-full-backtesting-engine)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Author](#author)

---

## What is this?

COELHO Finance is a financial market analytics platform — and, in Rafael's own words from the deck, a tool "to help you make informed investment decisions, track your investments and identify opportunities." It's **publicly live** at [coelhofinance.streamlit.app](https://coelhofinance.streamlit.app/), free, no signup.

It was also a deliberate sandbox: every time-series technique, volatility model, or optimization method here was tried against real market data before being considered for other work — this is the largest and most methodologically diverse project in the portfolio, spanning classical technical analysis, econometrics (ARCH/GARCH, ARIMA, exponential smoothing), anomaly and changepoint detection, Monte Carlo simulation, and convex portfolio optimization.

## The three live sections

| Section | What it covers | Scope |
|---|---|---|
| **UNIMARKET** | Deep dive into one instrument | Chart, analyst recommendations, 12 categories of financial statements, technical insights |
| **UNISTATS** | Statistical/ML modeling on one instrument | Outlier & changepoint detection, RSI/MACD, forecasting, anomaly detection, GARCH volatility, Monte Carlo |
| **MULTIMARKET** | Compare 2+ instruments | Correlation, multivariate GARCH, portfolio optimization, cross-asset news |

All three share the same filter bar: pick an **asset class** (Stocks, Indices, Crypto, Currency Crosses, Funds, ETFs, Commodities, Bonds), then a **market/country**, then the specific instrument.

## UNIMARKET: single-asset deep dive

| Tab | What's in it |
|---|---|
| **UNIMARKET** | Candlestick + OHLC line overlays, volume bars, trading-day gap removal |
| **Indicators** | Analyst recommendation scores (Yahoo Finance peer comparisons) |
| **News** | Latest news for the instrument |
| **Financial** | 12 sub-tabs: Financials, Income Statement, Balance Sheet, Cash Flow, Holders, Earnings, Valuation Measures, Shares Full, Dividends & Splits, Trend, Option Chain, Events — each rendered as an interactive bar chart or table, sourced from both yfinance and YahooQuery |
| **Technical Insights** | Yahoo Finance's own analyst-style data: instrument support/resistance/stop-loss levels, bullish/bearish scoring across short/intermediate/long-term horizons, company snapshot, research reports, and SEC filings |

## UNISTATS: the econometrics toolkit

This is the deepest section — six tabs, each a different statistical lens on the same instrument:

| Tab | Techniques |
|---|---|
| **Indicators** | Outlier detection (rolling-window ±N-sigma bands, Hampel filter), **changepoint detection** (Dynamic Programming, Binary Segmentation, Window search via `ruptures`), RSI, MACD |
| **Forecast** | Seasonal decomposition (classical + STL), stationarity testing (ADF + KPSS with ACF/PACF plots), exponential smoothing (Simple, Holt's, Holt-Winters triple), **ARIMA** with log-transform/differencing workflow and MAPE-scored model comparison |
| **Anomaly Detection** | Six ADTK algorithms: Seasonal, Threshold, Quantile, Inter-Quartile Range, Generalized ESD, Persist |
| **Volatility** | ARCH and GARCH model fitting with full statistical summaries, plus GARCH-t forecasting via three distinct methods (Analytical, Simulation, Bootstrap) across four horizons |
| **Simulations** | Monte Carlo Geometric Brownian Motion price paths (up to 10,000 simulated paths), compared against realized prices over the same held-out window |

## MULTIMARKET: comparison and portfolio theory

| Tab | What's in it |
|---|---|
| **Multimarket** | Overlaid comparison chart + correlation matrix across every selected instrument |
| **Volatility** | Per-asset GARCH(1,1) fitting, then a **DCC-style conditional correlation matrix**: standardized residuals from each asset's GARCH model combined into a forecasted conditional covariance matrix |
| **Asset Allocation** | Three sub-tabs: an equally-weighted portfolio with a full **QuantStats** HTML tearsheet (downloadable) and snapshot chart; an Efficient Frontier via 100,000-portfolio Monte Carlo simulation; and a true **convex-optimized** Efficient Frontier (`cvxpy`, Markowitz mean-variance with a risk-aversion sweep across `gamma`) showing how optimal weights shift with risk tolerance |
| **News** | Per-instrument news, one sub-tab each |

## Asset class and data source coverage

| Asset class | Source |
|---|---|
| **Stocks** | Static per-country symbol lists (`data/symbols/*.json`, 50 countries) + yfinance/YahooQuery |
| **Indices, Bonds, Commodities, Funds, ETFs, Currency Crosses** | investpy (live catalog) + yfinance |
| **Crypto** | investpy catalog for UNIMARKET/UNISTATS/MULTIMARKET; direct **Binance API** and **CCXT** (unified multi-exchange) for the backtesting engine below |

Every asset class is fetched through both `yfinance` and `yahooquery` in parallel — the two libraries expose different subsets of Yahoo Finance's data, and the app pulls from whichever has the field it needs.

## Shipped but hidden: a full backtesting engine

`pages/backtesting.py` (785 lines) is a complete **vectorbt**-powered systematic strategy research tool — but it's commented out of the navigation in `app.py`, `functions.py`'s `option_menu()`, and `page_buttons()`, so it isn't reachable from the live app. It includes:

- Dual Moving Average Crossover backtesting with a full results/statistics/trades breakdown, and a 99×99 fast-window × slow-window Sharpe ratio heatmap
- MACD strategy search across a 49-fast × 49-slow × 19-signal parameter grid, visualized as a 3D volume
- RSI-filtered MA crossover
- **Walk-forward optimization**: rolling in-sample/out-of-sample windows, best-parameter selection by in-sample Sharpe, and honest out-of-sample validation against those selected parameters
- A stop-loss/trailing-stop/take-profit sweep across 10 major crypto pairs and 100 stop-value levels, with expectancy, win-rate, and total-return distributions

This is real, working walk-forward-CV strategy research — just not currently exposed to end users. Re-enabling it is uncommenting three call sites, not a rewrite.

Also disabled: most of UNIMARKET's original **Indicators** tab (18 categorized metric-card groups — ESG scores, institutional ownership, key stats, SEC filings, share purchase activity, and a general-indicators catch-all) and its **Informations** tab (company summary + officers) are commented out, leaving only the Recommendations sub-tab active. The metric-card infrastructure (`indicator_metrics`, `general_indicator_metrics` in `functions.py`) that powered them is intact and unused.

## Tech Stack

| Technology | Role |
|---|---|
| **Streamlit** | UI shell across 5 pages |
| **yfinance / YahooQuery / investpy** | Stock, index, fund, ETF, bond, commodity, currency-cross, and crypto data |
| **python-binance / CCXT / vectorbt** | Crypto OHLCV data and the backtesting engine |
| **pandas / NumPy** | Data wrangling, returns, rolling statistics |
| **statsmodels / sktime** | ARIMA, exponential smoothing, seasonal decomposition, stationarity tests, Hampel filter |
| **arch** | ARCH/GARCH volatility modeling and forecasting |
| **ruptures** | Changepoint detection (Dynamic Programming, Binary Segmentation, Window) |
| **adtk** | Six-algorithm anomaly detection toolkit |
| **cvxpy** | Convex mean-variance portfolio optimization |
| **QuantStats** | Portfolio tearsheets and performance snapshots |
| **pandas-ta** | RSI, MACD |
| **Plotly / Matplotlib** | Interactive and static charting |

## Prerequisites

| Requirement | Notes |
|---|---|
| **Python** 3.10+ | |
| No API keys required | Every data source (yfinance, YahooQuery, investpy, Binance, CCXT) is used unauthenticated/public |

## Installation

```bash
git clone https://github.com/rafaelcoelho1409/COELHOFinance
cd COELHOFinance

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

streamlit run app.py
```

## Project Structure

```
COELHOFinance/
├── app.py                       # Home page — feature carousel, navigation
├── functions.py                   # Shared library: 8 asset-class filters (×2 variants each),
│                                   # data fetchers, portfolio optimization, GARCH correlation,
│                                   # GBM simulation, backtesting helpers (1773 lines)
├── pages/
│   ├── unimarket.py               # Single-asset deep dive (1273 lines)
│   ├── unistats.py                # Econometrics toolkit (1854 lines)
│   ├── multimarket.py             # Comparison + portfolio theory (352 lines)
│   ├── backtesting.py             # vectorbt engine — built, not linked in nav (785 lines)
│   └── about.py                   # Author info
│
├── data/
│   ├── symbols/                  # Per-country stock symbol catalogs (50 countries)
│   ├── bonds.json, commodities.json, market_list.json, ...
│   └── binance_symbols.json, ccxt_symbols.json
│
├── assets/                      # Logo, screenshots
├── COELHOFinance.pdf              # Deployment record / demo deck
└── requirements.txt
```

## Author

**Rafael Coelho** — [rafaelcoelho.pages.dev](https://rafaelcoelho.pages.dev/)
