# Quantitative Algorithmic Trading with Python 📊💻

Welcome to the **Quantitative Algorithmic Trading with Python** repository! This project contains Python scripts for developing and backtesting algorithmic trading strategies. The codebase is built around concepts learned from the Udemy course ["Algorithmic Trading & Quantitative Analysis Using Python"](https://www.udemy.com/course/algorithmic-trading-quantitative-analysis-using-python/).

## Features

- **Automated Trading Systems**: Build and run fully automated strategies using APIs.
- **Backtesting Strategies**: Test strategies like Renko-MACD, breakout, and portfolio rebalancing.
- **Technical Indicators**: Use TA-Lib to implement indicators like MACD, OBV, and more.
- **Web Scraping**: Extract financial data using Selenium for Magic Formula and Piotroski strategies.
- **Performance Metrics**: Calculate KPIs such as Sharpe ratio, Sortino ratio, and maximum drawdown.

## Project Structure

- `fx_macd_renko_automated_trading.py`: Automated Renko-MACD strategy using real-time data.
- `renko_macd_backtest_4.py`: Renko MACD strategy backtester.
- `renko_obv_backtest_3.py`: On-balance volume (OBV) Renko strategy backtester.
- `breakout_backtest_2.py`: Implements a breakout strategy backtest.
- `portfolio_rebalance_backtest_1.py`: Backtests a portfolio rebalancing strategy.
- `magic_formula_selenium_Aug2024.py`: Implements the Magic Formula strategy using Selenium for web scraping.
- `piotroski_f_selenium_Aug2024.py`: Automates Piotroski F-Score calculation using Selenium.
- `max_dd_calmar.py`: Script to calculate maximum drawdown and Calmar ratio.
- `sharpe_sortino.py`: Script to calculate Sharpe and Sortino ratios.
- `talib_intro.py`: Introduction to using TA-Lib for technical indicators.
- `visualization_2.py`: Additional visualizations for strategy performance.
- `visualization_1.py`: Visualizations for backtested trading strategies.
- `rolling_ops.py`: Implements rolling operations on stock prices for trend analysis.
- `yfinance_multiple_tickers.py`: Fetch data for multiple tickers using yFinance.

## Quick Start 🚀

1. Clone the repository:
    ```bash
    git clone https://github.com/shumailsajjad/Quantitative-Algorithmic-Trading-with-Python.git
    cd Quantitative-Algorithmic-Trading-with-Python
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run your first backtest:
    ```bash
    python renko_macd_backtest.py
    ```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve this project.

## License

This project is licensed under the MIT License.
