import streamlit as st
from utils.data_related import load_ticker_generic_info, combine_ticker_name, retrieve_company_info, read_dividend_data, read_financial_data, read_analysis_data, read_history_data

ticker_info = load_ticker_generic_info()
ticker_name_list = combine_ticker_name(ticker_info)
title_name = "{company_name} Information"

with st.sidebar:
    selected_company = st.selectbox(
    "Select a company to show the information",
    options=["Select a Company"] + list(ticker_name_list),  # Add a placeholder
)
# Conditional Rendering
if selected_company == "Select a Company":
    # Show default Company Information heading
    st.title("Company Information")
    st.write("This page will display information about the company you are interested in.")
else:
    # Replace with selected company's information
    st.title(f"{selected_company} Information")
    st.write(f"This page will display information about the {selected_company} company.")

    company_info = retrieve_company_info(ticker_info, selected_company).iloc[0]
    dividend_history = read_dividend_data(company_info["ticker"], company_info["exchange"])
    financial_data = read_financial_data(company_info["ticker"], company_info["exchange"])
    analysis_data = read_analysis_data(company_info["ticker"], company_info["exchange"]).iloc[0]
    history_data = read_history_data(company_info["ticker"], company_info["exchange"])
    #st.write(history_data)
    
    # Basic Information Section
    st.title("Basic Information")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Issuer Name", company_info["shortName"], disabled=True)
        st.text_input("Currency", "VND", disabled=True)
        st.text_input("Number of Employees", company_info["noEmployees"], disabled=True)
        st.text_input("Website", company_info["website"], disabled=True)
    with col2:
        st.text_input("Symbol", company_info["ticker"], disabled=True)
        st.text_input("Exchange", company_info["exchange"], disabled=True)
        st.text_input("Industry", company_info["industry"], disabled=True)
        st.text_input("Year of Establishment", company_info["establishedYear"], disabled=True)


    # Divider
    st.markdown("---")

    # Title for the Market Data section
    st.title("Market Data")

    # Market Data Section
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Current Open Price", history_data["Open"].iloc[-1], disabled=True)
        st.text_input("Average Open", round(history_data["Open"].mean(), 3), disabled=True)
        st.text_input("Regular Market Previous Close", history_data["Close"].median(), disabled=True)
        st.text_input("Regular Market Day High",  history_data["High"].median(), disabled=True)
    with col2:
        st.text_input("Previous Close", history_data["Close"].iloc[-2], disabled=True)
        st.text_input("Minimum Low", history_data["Low"].min(), disabled=True)
        st.text_input("Regular Market Volume", round(history_data["Volume"].mean(), 3), disabled=True)
        st.text_input("Regular Market Day Open", history_data["Open"].median(), disabled=True)
    
    # Divider
    st.markdown("---")

    # Title for the Market Data section
    st.title("Volume and Shares")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Number of Shareholders", company_info["noShareholders"], disabled=True)
        st.text_input("Foreign Percentages", company_info["foreignPercent"], disabled=True)
    
    with col2:
        st.text_input("Outstanding Share", company_info["outstandingShare"], disabled=True)
        st.text_input("Issue Share", company_info["issueShare"], disabled=True)
    
    # Divider
    st.markdown("---")

    # Title for the Market Data section
    st.title("Valuation and Ratios")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Market Cap", analysis_data["marcap"], disabled=True)
        st.text_input("Enterprise Value (in billion)", analysis_data["price"], disabled=True)
        st.text_input("Gross Margins", analysis_data["grossProfitMargin"], disabled=True)
    
    with col2:
        st.text_input("Price to Book", analysis_data["priceToBook"], disabled=True)
        st.text_input("Return on Assets (ROA)", analysis_data["roa"], disabled=True)
        st.text_input("Return on Equity (ROE)", analysis_data["roe"], disabled=True)
    
    # Divider
    st.markdown("---")

    # Title for the Market Data section
    st.title("Financial Performance")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Average Price to Earning", financial_data["priceToEarning"].mean(), disabled=True)
        st.text_input("Average Price to Book", financial_data["priceToBook"].mean(), disabled=True)
    
    with col2:
        st.text_input("Sum Earning Per Share", financial_data["earningPerShare"].sum(), disabled=True)
        st.text_input("Sum Book Value Per Share", financial_data["bookValuePerShare"].sum(), disabled=True)
    
    # Divider
    st.markdown("---")

    # Title for the Market Data section
    st.title("Analyst Targets")