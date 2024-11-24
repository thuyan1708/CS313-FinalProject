import pandas as pd
import streamlit as st

from utils.ml_model import predict_new_data, predict_3rd_day_open_price, predict_3_consecutive_days_open_price

def load_ticker_generic_info():
    ticker_info_df = pd.read_csv("data/ticker-overview.csv")
    return ticker_info_df

def combine_ticker_name(ticker_info_df):
    ticker_info_df["ticker_name"] = ticker_info_df['ticker'] + " - " + ticker_info_df['shortName']
    return ticker_info_df["ticker_name"].tolist()

def retrieve_company_info(ticker_info_df, ticker_name):
    ticker_info = ticker_info_df[ticker_info_df["ticker_name"] == ticker_name]
    return ticker_info.reset_index(drop=True).drop(columns=["Unnamed: 0"]).fillna("No Information")

def retrieve_wishlist_info(ticker_info_df, ticker_name):
    ticker_info = ticker_info_df[ticker_info_df["ticker"] == ticker_name]
    return ticker_info.reset_index(drop=True).drop(columns=["Unnamed: 0"]).fillna("No Information")

def read_dividend_data(ticker_name, exchange):
    #print("Ticker Name: ", ticker_name)
    if exchange == "UPCOM":
        index_name = "UpcomIndex"  # Capitalized for consistency
    elif exchange == "HOSE":
        index_name = "VNINDEX"
    elif exchange == "HNX":
        index_name = "HNXIndex"
    else:
        index_name = ""  # Handle cases with unknown exchange
    
    path = f"data/dividend-history/{ticker_name}-{index_name}-Dividend.csv"
    dividend_data = pd.read_csv(path)
    return dividend_data

def read_financial_data(ticker_name, exchange):
    if exchange == "UPCOM":
        index_name = "UpcomIndex"  # Capitalized for consistency
    elif exchange == "HOSE":
        index_name = "VNINDEX"
    elif exchange == "HNX":
        index_name = "HNXIndex"
    else:
        index_name = ""  # Handle cases with unknown exchange
    
    path = f"data/financial-ratio/{ticker_name}-{index_name}-Finance.csv"
    financial_data = pd.read_csv(path)
    return financial_data

def read_analysis_data(ticker_name, exchange):
    if exchange == "UPCOM":
        index_name = "UpcomIndex"  # Capitalized for consistency
    elif exchange == "HOSE":
        index_name = "VNINDEX"
    elif exchange == "HNX":
        index_name = "HNXIndex"
    else:
        index_name = ""  # Handle cases with unknown exchange
    
    path = f"data/industry-analysis/{ticker_name}-{index_name}-Industry.csv"
    analysis_data = pd.read_csv(path)
    analysis_data = analysis_data[analysis_data["ticker"] == ticker_name]
    return analysis_data

def read_history_data(ticker_name, exchange):
    if exchange == "UPCOM":
        index_name = "UpcomIndex"  # Capitalized for consistency
    elif exchange == "HOSE":
        index_name = "VNINDEX"
    elif exchange == "HNX":
        index_name = "HNXIndex"
    else:
        index_name = ""  # Handle cases with unknown exchange
    
    path = f"data/stock-historical-data/{ticker_name}-{index_name}-History.csv"
    history_data = pd.read_csv(path)
    history_data = history_data.sort_values(by="TradingDate")
    return history_data

def construct_wishlist_table(ticker_name_list, ticker_info_df):
    wishlist_data = []  # Use a list to collect row data
    try:
        for ticker_name in ticker_name_list:
            # Retrieve company info and historical data
            company_info = retrieve_wishlist_info(ticker_info_df, ticker_name.strip()).iloc[0]
            history_data = read_history_data(company_info["ticker"], company_info["exchange"])

            # Calculate changes
            last_close = history_data["Close"].iloc[-1]
            previous_close = history_data["Close"].iloc[-2]
            change = last_close - previous_close
            change_percent = (change / previous_close) * 100

            current_open = history_data["Open"].iloc[-1]

            # Predict values using the API
            try:
                # Predict Next Day Open Price
                next_day_open = predict_new_data(history_data, ["Close", "High", "Low"], 30)[-1]
                next_day_open = float(next_day_open)  # Ensure it's a scalar value
                next_day_open_diff = next_day_open - current_open

                # Predict Day 3 After Open
                day_3_open = predict_3rd_day_open_price(history_data, ["Close", "High", "Low"], 30)[-1]
                day_3_open = float(day_3_open)  # Ensure it's a scalar value
                day_3_open_diff = day_3_open - current_open

                # Predict Average of Next 3 Days Open Prices
                next_3_days_prices_raw = predict_3_consecutive_days_open_price(
                    history_data, ["Close", "High", "Low"], 30
                )[-3:]
                next_3_days_prices = [float(price) for price in next_3_days_prices_raw[0]]
                avg_3_days_open = sum(next_3_days_prices) / len(next_3_days_prices)
                avg_3_days_open_diff = avg_3_days_open - current_open

            except Exception as e:
                # If API calls fail, set predictions to N/A
                next_day_open = "N/A"
                day_3_open = "N/A"
                avg_3_days_open = "N/A"
                next_day_open_diff = day_3_open_diff = avg_3_days_open_diff = None

            # Create a dictionary for the row
            row = {
                "Name": company_info["shortName"],
                "Exchange": company_info["exchange"],
                "Currency": "VND",
                "Last Close": last_close,
                "Change": change,
                "Change %": change_percent,
                "Open": current_open,
                "High": history_data["High"].iloc[-1],
                "Low": history_data["Low"].iloc[-1],
                "Volume": history_data["Volume"].iloc[-1],
                "Predict Next Day Open": next_day_open,
                "Predict Day 3 After Open": day_3_open,
                "Predict Average 3 Days Later Open": avg_3_days_open,
                # Store differences for styling
                "Next Day Diff": next_day_open_diff if next_day_open_diff is not None else "N/A",
                "Day 3 Diff": day_3_open_diff if day_3_open_diff is not None else "N/A",
                "Avg 3 Days Diff": avg_3_days_open_diff if avg_3_days_open_diff is not None else "N/A"
            }

            # Append the row to the list
            wishlist_data.append(row)

        # Convert the list of rows into a DataFrame
        wishlist_df = pd.DataFrame(wishlist_data)

        # **Create Formatted Columns with Arrows**
        def format_predicted_price(row, pred_col, diff_col):
            val = row[pred_col]
            diff = row[diff_col]
            if isinstance(val, (int, float)):
                if diff > 0:
                    return f'↑ {val:.2f}'
                elif diff < 0:
                    return f'↓ {val:.2f}'
                else:
                    return f'{val:.2f}'
            else:
                return val

        # Apply formatting to create new columns
        wishlist_df['Predict Next Day Open Formatted'] = wishlist_df.apply(
            lambda row: format_predicted_price(row, 'Predict Next Day Open', 'Next Day Diff'), axis=1)
        wishlist_df['Predict Day 3 After Open Formatted'] = wishlist_df.apply(
            lambda row: format_predicted_price(row, 'Predict Day 3 After Open', 'Day 3 Diff'), axis=1)
        wishlist_df['Predict Average 3 Days Later Open Formatted'] = wishlist_df.apply(
            lambda row: format_predicted_price(row, 'Predict Average 3 Days Later Open', 'Avg 3 Days Diff'), axis=1)

        # **Select columns to display (exclude 'Diff' columns)**
        display_columns = [
            "Name", "Exchange", "Currency", "Last Close", "Change", "Change %", "Open", "High", "Low", "Volume",
            "Predict Next Day Open Formatted", "Predict Day 3 After Open Formatted", "Predict Average 3 Days Later Open Formatted"
        ]

        # **Create display DataFrame**
        display_df = wishlist_df[display_columns].copy()

        # **Rename columns for display**
        display_df = display_df.rename(columns={
            "Predict Next Day Open Formatted": "Predict Next Day Open",
            "Predict Day 3 After Open Formatted": "Predict Day 3 After Open",
            "Predict Average 3 Days Later Open Formatted": "Predict Average 3 Days Later Open"
        })

        # **Define helper functions for styling**

        # Function to apply conditional formatting for 'Change' and 'Change %' columns
        def highlight_positive_negative(val):
            if isinstance(val, (int, float)) and val > 0:
                color = 'lightgreen'
            elif isinstance(val, (int, float)) and val < 0:
                color = 'salmon'
            else:
                color = 'white'
            return f'background-color: {color}; color: black;'

        # Function to format change values to include arrows and signs
        def format_change(val):
            if isinstance(val, (int, float)):
                if val > 0:
                    return f'↑ {val:+.2f}'
                elif val < 0:
                    return f'↓ {val:+.2f}'
                else:
                    return f'{val:+.2f}'
            return val  # Return as is if not a number

        # **Function to apply conditional formatting to predicted prices**
        def highlight_predicted_prices(row):
            styles = []
            index = row.name  # Get the index of the current row
            for col, diff_col in [
                ("Predict Next Day Open", "Next Day Diff"),
                ("Predict Day 3 After Open", "Day 3 Diff"),
                ("Predict Average 3 Days Later Open", "Avg 3 Days Diff")
            ]:
                diff = wishlist_df.loc[index, diff_col]  # Access 'Diff' columns from wishlist_df
                if pd.isnull(diff) or diff == "N/A":
                    styles.append('')
                elif diff > 0:
                    styles.append('background-color: lightgreen; color: black;')
                elif diff < 0:
                    styles.append('background-color: salmon; color: black;')
                else:
                    styles.append('background-color: white; color: black;')
            return styles

        # **Apply conditional formatting**
        styled_display_df = display_df.style

        # Apply conditional formatting to 'Change' and 'Change %' columns
        styled_display_df = styled_display_df.applymap(
            highlight_positive_negative, subset=['Change', 'Change %']
        )

        # Apply conditional formatting to predicted price columns
        styled_display_df = styled_display_df.apply(
            highlight_predicted_prices, axis=1, subset=[
                "Predict Next Day Open",
                "Predict Day 3 After Open",
                "Predict Average 3 Days Later Open"
            ]
        )

        # Format numeric columns
        styled_display_df = styled_display_df.format({
            'Change': format_change,
            'Change %': lambda x: format_change(x) + '%',
            'Last Close': '{:.2f}',
            'Open': '{:.2f}',
            'High': '{:.2f}',
            'Low': '{:.2f}',
            'Volume': '{:,.0f}',
            # Predicted columns are already formatted
            'Predict Next Day Open': '{}',
            'Predict Day 3 After Open': '{}',
            'Predict Average 3 Days Later Open': '{}'
        })

        # Update the CSS styles to adjust column and cell sizes
        styled_display_df = styled_display_df.set_table_styles([
            {'selector': 'th', 'props': [('font-size', '14px'), ('text-align', 'center')]},  # Header styling
            {'selector': 'td', 'props': [('font-size', '12px'), ('padding', '8px 10px')]},  # Cell padding
            {'selector': 'td:nth-child(1)', 'props': [('min-width', '200px'), ('max-width', '200px')]},  # Expand "Name" column
            {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]}  # Table layout
        ])

        return styled_display_df
    
    except Exception as e:
        st.write("Please turn on the API server to enable predictions. The API server is currently off. Please allocate to the Google Colab and run the task 5.1 to start the NGROK server.")
        return None



# Create color coding for price changes
def get_trend_color(next_3_days_prices, last_open_price, index):
    if index == 0:
        return "green" if next_3_days_prices[index] > last_open_price else "red"
    else:
        return (
            "green" if next_3_days_prices[index] > next_3_days_prices[index - 1] else "red"
        )