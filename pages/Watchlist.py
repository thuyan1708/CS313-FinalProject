import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils.data_related import load_ticker_generic_info, combine_ticker_name, construct_wishlist_table, read_history_data

st.title("Your Watchlist")
st.write("Choose the stocks you want to keep an eye on.")

ticker_info = load_ticker_generic_info()
ticker_name_list = [str(i).split("-")[0] for i in list(combine_ticker_name(ticker_info))]
title_name = "{company_name} Information"

with st.sidebar:
    selected_company = st.multiselect(
    "Choose the ticker to add to your watchlist",
    list(ticker_name_list),
    ["ACB ", "BID ", "CTG ", "VCB ", "EIB "]
)

if selected_company:
    wishlist_df = construct_wishlist_table(selected_company, ticker_info)
    
    # Apply conditional formatting
    st.dataframe(construct_wishlist_table(selected_company, ticker_info))
    
    # Line chart for stock performance
    st.header("Stock Price Performance (Open / Close Price and Volume)")

    # Prepare combined data
    combined_data = pd.DataFrame()
    line_colors = {}  # Store line colors for tickers

    for ticker in selected_company:
        # Retrieve company info
        company_info = ticker_info[ticker_info["ticker"] == ticker.strip()].iloc[0]
        exchange = company_info["exchange"]

        # Read historical data
        history_data = read_history_data(ticker.strip(), exchange)
        history_data["Ticker"] = ticker  # Add a column for the ticker
        history_data["Color"] = [
            "green" if close > open_ else "red"
            for close, open_ in zip(history_data["Close"], history_data["Open"])
        ]  # Color based on price movement
        combined_data = pd.concat([combined_data, history_data], axis=0)

    # Ensure proper datetime format
    combined_data["TradingDate"] = pd.to_datetime(combined_data["TradingDate"])

    # Create a Plotly figure with subplots for Close Price and Volume
    fig_close_volume = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True,  # Share the x-axis between price and volume
        vertical_spacing=0.1,  # Space between subplots
        row_heights=[0.7, 0.3]  # Adjust heights (70% for price, 30% for volume)
    )

    # Add stock price traces (Close Price)
    for ticker in selected_company:
        ticker_data = combined_data[combined_data["Ticker"] == ticker]
        # Assign a unique color for each ticker line
        line_color = f"hsl({hash(ticker) % 150}, 70%, 50%)"
        line_colors[ticker] = line_color

        fig_close_volume.add_trace(
            go.Scatter(
                x=ticker_data["TradingDate"],
                y=ticker_data["Close"],
                mode="lines",
                name=f"{ticker} Close Price",
                line=dict(color=line_color)  # Use the dynamically assigned color
            ),
            row=1, col=1
        )

    # Add volume traces and Volume_MA traces
    for ticker in selected_company:
        ticker_data = combined_data[combined_data["Ticker"] == ticker]
        # Add volume bars
        fig_close_volume.add_trace(
            go.Bar(
                x=ticker_data["TradingDate"],
                y=ticker_data["Volume"],
                name=f"{ticker} Volume",
                marker=dict(color=ticker_data["Color"]),  # Dynamic bar colors
                opacity=0.8  # Slight transparency for better visualization
            ),
            row=2, col=1
        )
        
        # Calculate the 20-day moving average of volume
        ticker_data["Volume_MA"] = ticker_data["Volume"].rolling(window=20).mean()
        
        # Add Volume_MA line using the same color as the Close Price line
        fig_close_volume.add_trace(
            go.Scatter(
                x=ticker_data["TradingDate"],
                y=ticker_data["Volume_MA"],
                mode="lines",
                name=f"{ticker} Volume (20-day MA)",
                line=dict(color=line_colors[ticker], dash="dot")  # Match the color
            ),
            row=2, col=1
        )

    # Update layout for Close Price and Volume chart
    fig_close_volume.update_layout(
        title="Stock Close Price and Volume Performance",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Close Price (VND)", showgrid=True),
        yaxis2=dict(title="Volume", showgrid=True),
        legend_title="Ticker",
        template="plotly_dark",  # Optional: Change to "plotly" for light theme
        height=800,  # Adjust overall height
        showlegend=True,
        barmode="relative"  # Prevent bars from overlapping
    )

    # Render the Close Price and Volume Plotly chart in Streamlit
    st.plotly_chart(fig_close_volume, use_container_width=True)

    # Line chart for stock performance Open
    fig_open_price = go.Figure()

    # Add Open Price traces
    for ticker in selected_company:
        ticker_data = combined_data[combined_data["Ticker"] == ticker]
        fig_open_price.add_trace(
            go.Scatter(
                x=ticker_data["TradingDate"],
                y=ticker_data["Open"],
                mode="lines",
                name=f"{ticker} Open Price",
                line=dict(color=line_colors[ticker])  # Use the same color as the Close Price
            )
        )

    # Update layout for Open Price chart
    fig_open_price.update_layout(
        title="Stock Open Price Performance",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Open Price (VND)", showgrid=True),
        legend_title="Ticker",
        template="plotly_dark",  # Optional: Change to "plotly" for light theme
        height=600,  # Adjust overall height
        showlegend=True
    )

    # Render the Open Price Plotly chart in Streamlit
    st.plotly_chart(fig_open_price, use_container_width=True)
