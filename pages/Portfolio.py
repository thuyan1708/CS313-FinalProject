import streamlit as st
import pandas as pd
from utils.data_related import load_ticker_generic_info, combine_ticker_name, read_history_data
from utils.ml_model import load_sklearn_model, predict_buy_sell_probability, predict_new_data, predict_3rd_day_open_price, predict_3_consecutive_days_open_price
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Load ticker information
ticker_info = load_ticker_generic_info()
ticker_name_list = [str(i).split("-")[0] for i in list(combine_ticker_name(ticker_info))]
BUY_INDICATOR_MODEL = load_sklearn_model("models/buy_indicator.pkl")
SELL_INDICATOR_MODEL = load_sklearn_model("models/sell_indicator.pkl")


st.title("An's Portfolio")
st.write("This page displays your current portfolio performance")

# Sidebar: User input for total invested money
with st.sidebar:
    st.write("Your Portfolio Settings")
    total_invested_money = st.number_input(
        "Enter your total invested money (VND):",
        min_value=1_000_000,
        step=1_000_000,
        value=10_000_000
    )

    selected_company = st.multiselect(
        "Your current portfolio",
        list(ticker_name_list),
        ["ACB ", "BID ", "CTG "],
        disabled=False
    )

    # Submit button to trigger recalculation
    recalculate = st.button("Submit")

# Initialize variables
portfolio_data = []
total_change_per_day = 0
total_profit_loss = 0
market_value = 0

# Trigger calculations when the Submit button is pressed
if recalculate and selected_company:
    # Split the invested money equally among the selected tickers
    per_ticker_invested = total_invested_money / len(selected_company)

    for ticker in selected_company:
        # Retrieve company info
        company_info = ticker_info[ticker_info["ticker"] == ticker.strip()].iloc[0]
        exchange = company_info["exchange"]

        # Read historical data for the ticker
        history_data = read_history_data(ticker.strip(), exchange)

        # Get the latest and previous Close prices
        last_close = history_data["Close"].iloc[-1]
        previous_close = history_data["Close"].iloc[-2]

        # Calculate changes
        change = last_close - previous_close
        change_percent = (change / previous_close) * 100

        # Append data to the portfolio
        portfolio_data.append({
            "ticker": ticker.strip(),
            "invested": per_ticker_invested,
            "change": change,
            "change_percent": change_percent,
            "last_close": last_close
        })

    # Calculate totals
    total_change_per_day = sum(item["change"] for item in portfolio_data)  # Total change
    total_profit_loss = total_change_per_day  # For simplicity, profit/loss = total change
    market_value = total_invested_money + total_profit_loss  # Market value

    # Display Total Summary if calculations are triggered
    if portfolio_data:
        st.header("Portfolio Summary")

        st.markdown(
            f"""
            <div style="width: 350px; margin: 0 auto; border-radius: 10px; padding: 20px; background-color: #222; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid #444; padding-bottom: 5px;">
                    <h3 style="color: white; font-size: 16px;">Today's Change</h3>
                    <p style="color: {'green' if total_change_per_day > 0 else 'red' if total_change_per_day < 0 else 'gray'}; font-size: 16px; font-weight: bold; margin: 0;">
                        {'↑' if total_change_per_day > 0 else '↓' if total_change_per_day < 0 else ''} {total_change_per_day:,.0f} VND
                    </p>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid #444; padding-bottom: 5px;">
                    <h3 style="color: white; font-size: 16px;">Total Profit/Loss</h3>
                    <p style="color: {'green' if total_profit_loss > 0 else 'red' if total_profit_loss < 0 else 'gray'}; font-size: 16px; font-weight: bold; margin: 0;">
                        {'↑' if total_profit_loss > 0 else '↓' if total_profit_loss < 0 else ''} {total_profit_loss:,.0f} VND
                    </p>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid #444; padding-bottom: 5px;">
                    <h3 style="color: white; font-size: 16px;">Market Value</h3>
                    <p style="color: white; font-size: 16px; font-weight: bold; margin: 0;">
                        {market_value:,.0f} VND
                    </p>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid #444; padding-bottom: 5px;">
                    <h3 style="color: white; font-size: 16px;">Total Cost</h3>
                    <p style="color: white; font-size: 16px; font-weight: bold; margin: 0;">
                        {total_invested_money:,.0f} VND
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Create individual portfolio containers
        st.header("Portfolio Performance")
        cols = st.columns(len(portfolio_data))  # Create one column per portfolio item

        for col, data in zip(cols, portfolio_data):
            ticker = data["ticker"]
            invested = data["invested"]
            change = data["change"]
            change_percent = data["change_percent"]
            last_close = data["last_close"]

            # Determine styling for individual portfolio items
            if change > 0:
                color = "green"
                arrow = "↑"
                display_change = f"{arrow} {change:,.0f} VND ({change_percent:+.2f}%)"
                border_color = "rgba(0, 255, 0, 0.8)"  # Light green border
            elif change < 0:
                color = "red"
                arrow = "↓"
                display_change = f"{arrow} {change:,.0f} VND ({change_percent:+.2f}%)"
                border_color = "rgba(255, 0, 0, 0.8)"  # Light red border
            else:
                color = "gray"
                arrow = ""
                display_change = f"{change:,.0f} VND ({change_percent:+.2f}%)"
                border_color = "rgba(128, 128, 128, 0.8)"  # Light gray border

            # Display container content with advanced styling
            with col:
                st.markdown(
                    f"""
                    <div style="
                        display: flex; 
                        flex-direction: column; 
                        align-items: center; 
                        justify-content: center; 
                        padding: 20px; 
                        border: 2px solid {border_color}; 
                        border-radius: 10px; 
                        background-color: #1E1E1E; 
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                        height: 180px;
                        text-align: center;">
                        <h3 style="color: white; font-size: 25px; margin-bottom: 10px; margin-left: 15px; margin-top: 5px;">{ticker}</h3>
                        <p style="color: white; font-size: 14px; margin: 5px 0;">Invested: {invested:,.0f} VND</p>
                        <p style="color: white; font-size: 14px; margin: 5px 0;">Last Close: {last_close:,.0f} VND</p>
                        <p style="color: {color}; font-size: 16px; font-weight: bold; margin: 5px 0;">{display_change}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    if portfolio_data:
        st.header("Stock Performance with Moving Averages")

        # Combine data for all selected tickers
        combined_data = pd.DataFrame()

        for ticker in selected_company:
            # Retrieve company info
            company_info = ticker_info[ticker_info["ticker"] == ticker.strip()].iloc[0]
            exchange = company_info["exchange"]

            # Read historical data
            history_data = read_history_data(ticker.strip(), exchange)
            history_data["Ticker"] = ticker.strip()

            # Add moving averages
            history_data["MA_Close_20"] = history_data["Close"].rolling(window=20).mean()  # 20-day moving average
            history_data["MA_Open_20"] = history_data["Open"].rolling(window=20).mean()  # 20-day moving average for Open

            # Add volume color
            history_data["Volume_Color"] = [
                "green" if close > open_ else "red"
                for close, open_ in zip(history_data["Close"], history_data["Open"])
            ]

            # Combine all data
            combined_data = pd.concat([combined_data, history_data], axis=0)

        # Ensure proper datetime format
        combined_data["TradingDate"] = pd.to_datetime(combined_data["TradingDate"])

        # Create Plotly subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )

        # Add traces for each ticker
        for ticker in selected_company:
            ticker_data = combined_data[combined_data["Ticker"] == ticker.strip()]

            # Dynamically scale bar color intensity based on volume
            max_volume = ticker_data["Volume"].max()
            scaled_colors = [
                f"rgba(50, 255, 50, {0.3 + 0.7 * (volume / max_volume)})" if color == "green"
                else f"rgba(255, 50, 50, {0.3 + 0.7 * (volume / max_volume)})"
                for volume, color in zip(ticker_data["Volume"], ticker_data["Volume_Color"])
            ]

            fig.add_trace(
                go.Bar(
                    x=ticker_data["TradingDate"],
                    y=ticker_data["Volume"],
                    name=f"{ticker.strip()} Volume",
                    marker=dict(
                        color=scaled_colors,
                        line=dict(width=0.5)  # Add an outline to bars
                    ),
                    opacity=1.0  # Increase opacity for better visibility
                ),
                row=2, col=1
            )
            # Add Moving Average for Close Price
            fig.add_trace(
                go.Scatter(
                    x=ticker_data["TradingDate"],
                    y=ticker_data["MA_Close_20"],
                    mode="lines",
                    name=f"{ticker.strip()} MA (20-day) Close",
                    line=dict(width=1.5, dash="dot")
                ),
                row=1, col=1
            )

            # Add Open Price line
            fig.add_trace(
                go.Scatter(
                    x=ticker_data["TradingDate"],
                    y=ticker_data["Open"],
                    mode="lines",
                    name=f"{ticker.strip()} Open Price",
                    line=dict(width=2)
                ),
                row=1, col=1
            )

            # Add Moving Average for Open Price
            fig.add_trace(
                go.Scatter(
                    x=ticker_data["TradingDate"],
                    y=ticker_data["MA_Open_20"],
                    mode="lines",
                    name=f"{ticker.strip()} MA (20-day) Open",
                    line=dict(width=1.5, dash="dot")
                ),
                row=1, col=1
            )

            # Add Volume as Bar Chart
            fig.add_trace(
                go.Bar(
                    x=ticker_data["TradingDate"],
                    y=ticker_data["Volume"],
                    name=f"{ticker.strip()} Volume",
                    marker=dict(color=ticker_data["Volume_Color"]),
                    opacity=0.8
                ),
                row=2, col=1
            )

        # Update layout for better visualization
        fig.update_layout(
            title="Stock Price and Volume Performance with Moving Averages",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Price (VND)", showgrid=True),
            yaxis2=dict(title="Volume", showgrid=True),
            legend_title="Ticker",
            template="plotly_white",  # Optional: Use "plotly_dark" for a dark theme
            height=800,
            showlegend=True
        )
        
        fig.update_yaxes(
            title="Volume",
            type="linear",  # Switch to "log" for better scaling if needed
            row=2, col=1
        )

        fig.update_layout(
            barmode="overlay",  # Avoid stacked bars
            bargap=0.05,  # Minimize gaps between bars
            template="plotly_white"  # Optional: Use a light theme for better contrast
        )

        # Render the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    
    # Buy/Sell Prediction Section
    if recalculate and portfolio_data:
        st.header("Buy / Sell Prediction")

        # Create individual buy/sell prediction containers
        cols = st.columns(len(portfolio_data))  # One column per ticker

        for col, data in zip(cols, portfolio_data):
            ticker = data["ticker"]

            # Load stock data for the ticker
            company_info = ticker_info[ticker_info["ticker"] == ticker].iloc[0]
            exchange = company_info["exchange"]
            stock_data = read_history_data(ticker, exchange)

            # Predict buy and sell probabilities
            is_buy = predict_buy_sell_probability(BUY_INDICATOR_MODEL, stock_data)  # Binary: 1 = Buy, 0 = Don't Buy
            is_sell = predict_buy_sell_probability(SELL_INDICATOR_MODEL, stock_data)  # Binary: 1 = Sell, 0 = Don't Sell

            # Determine visualization details
            buy_label = "✓ Buy" if is_buy >= 1 else "✗ Don't Buy"
            sell_label = "✓ Sell" if is_sell >= 1 else "✗ Don't Sell"

            buy_color = "green" if is_buy >= 1 else "gray"
            sell_color = "red" if is_sell >= 1 else "gray"

            # Determine overall recommendation
            # recommendation = "Hold"  # Default recommendation
            # recommendation_color = "gray"

            if is_buy > is_sell:
                recommendation = "Buy"
                recommendation_color = "green"
                sell_label = "✗ Don't Sell"
                sell_color = "gray"
            elif is_buy < is_sell:
                recommendation = "Sell"
                recommendation_color = "red"
                buy_label = "✗ Don't Buy"
                buy_color = "gray"
            else:
                recommendation = "Hold"  # Default recommendation
                recommendation_color = "gray"


            # Display Buy/Sell prediction container
            with col:
                st.markdown(
                    f"""
                    <div style="
                        display: flex; 
                        flex-direction: column; 
                        align-items: center; 
                        justify-content: center; 
                        padding: 20px; 
                        border-radius: 10px; 
                        background-color: #1E1E1E; 
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                        height: 200px;
                        text-align: center;">
                        <h3 style="color: white; font-size: 25px; margin-bottom: 10px; margin-top: 5px; margin-left: 20px;">{ticker}</h3>
                        <p style="color: {buy_color}; font-size: 18px; font-weight: bold; margin: 5px 0;">{buy_label}</p>
                        <p style="color: {sell_color}; font-size: 18px; font-weight: bold; margin: 5px 0;">{sell_label}</p>
                        <p style="color: {recommendation_color}; font-size: 16px; margin-top: 10px; font-weight: bold;">Recommendation: {recommendation}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    
    # Predict New Data Section
    # Add new section for Next Open Price Prediction
    if portfolio_data:
        st.header("Next Open Price Prediction")
        if portfolio_data:
            try:
                for ticker in selected_company:
                    company_info = ticker_info[ticker_info["ticker"] == ticker.strip()].iloc[0]
                    exchange = company_info["exchange"]

                    # Read historical data for the ticker
                    history_data = read_history_data(ticker.strip(), exchange)
                    last_open_price = history_data["Open"].iloc[-1]

                    # Predict Next Day Open Price
                    next_day_price = predict_new_data(history_data, ["Close", "High", "Low"], 30)[-1]
                    next_day_price = float(next_day_price)  # Ensure it's a scalar value

                    # Predict Next 3rd Day Open Price
                    next_3rd_day_price = predict_3rd_day_open_price(history_data, ["Close", "High", "Low"], 30)[-1]
                    next_3rd_day_price = float(next_3rd_day_price)  # Ensure it's a scalar value

                    # Predict Next 3 Days Consecutive Open Prices
                    next_3_days_prices_raw = predict_3_consecutive_days_open_price(history_data, ["Close", "High", "Low"], 30)
                    next_3_days_prices = [float(price) for price in next_3_days_prices_raw[0]]  # Flatten the array and convert to float

                    # Calculate differences for the first day in the 3 consecutive predictions
                    diff_next_day = next_day_price - last_open_price
                    diff_next_3rd_day = next_3rd_day_price - last_open_price

                    # Define colors for differences
                    def diff_color(value):
                        return "green" if value > 0 else "red" if value < 0 else "gray"

                    # Display prediction container
                    st.markdown(
                        f"""
                        <div style="
                            display: flex; 
                            flex-direction: column; 
                            align-items: center; 
                            justify-content: center; 
                            padding: 20px; 
                            border: 2px solid rgba(0, 123, 255, 0.5); 
                            border-radius: 10px; 
                            background-color: #1E1E1E; 
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); 
                            margin-bottom: 20px;
                            width: 100%;
                            text-align: center;">
                            <h3 style="color: white; font-size: 25px; margin-bottom: 15px;">Ticker: {ticker}</h3>
                            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                                <tr style="background-color: #2C2C2C; color: white;">
                                    <th style="padding: 10px; border: 1px solid #444;">Prediction</th>
                                    <th style="padding: 10px; border: 1px solid #444;">Open Price (VND)</th>
                                    <th style="padding: 10px; border: 1px solid #444;">Difference (VND)</th>
                                </tr>
                                <tr>
                                    <td style="padding: 10px; border: 1px solid #444; color: white;">Last Open Price</td>
                                    <td style="padding: 10px; border: 1px solid #444; color: white;">{last_open_price:,.2f}</td>
                                    <td style="padding: 10px; border: 1px solid #444; color: gray;">N/A</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px; border: 1px solid #444; color: white;">Next Day</td>
                                    <td style="padding: 10px; border: 1px solid #444; color: white;">{next_day_price:,.2f}</td>
                                    <td style="padding: 10px; border: 1px solid #444; color: {diff_color(diff_next_day)};">
                                        {'+' if diff_next_day > 0 else ''}{diff_next_day:,.2f}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px; border: 1px solid #444; color: white;">Next 3rd Day</td>
                                    <td style="padding: 10px; border: 1px solid #444; color: white;">{next_3rd_day_price:,.2f}</td>
                                    <td style="padding: 10px; border: 1px solid #444; color: {diff_color(diff_next_3rd_day)};">
                                        {'+' if diff_next_3rd_day > 0 else ''}{diff_next_3rd_day:,.2f}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px; border: 1px solid #444; color: white;">Next 3 Days Consecutive</td>
                                    <td colspan="2" style="padding: 10px; border: 1px solid #444; color: white;">
                                        {', '.join([f"{price:,.2f}" for price in next_3_days_prices])}
                                    </td>
                                </tr>
                            </table>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            except Exception as e:
                st.write("Please turn on the API server to enable predictions. The API server is currently off. Please allocate to the Google Colab and run the task 5.1 to start the NGROK server.")