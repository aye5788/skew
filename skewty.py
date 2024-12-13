import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from datetime import datetime

# Alpha Vantage API Key
API_KEY = "CLP9IN76G4S8OUXN"

# Function to fetch options data from Alpha Vantage
def fetch_options_data(symbol):
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "OPTION_CHAIN",
        "symbol": symbol,
        "apikey": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if "optionChain" in data:
        options_data = data["optionChain"]
        return pd.DataFrame(options_data)
    else:
        st.error("Failed to fetch data. Check the ticker symbol or API key.")
        return None

# Function to preprocess data
def preprocess_data(df):
    # Extract moneyness and days to expiration
    df["moneyness"] = (df["underlyingPrice"] - df["strikePrice"]) / df["underlyingPrice"]
    df["days_to_expiration"] = (
        pd.to_datetime(df["expirationDate"]) - datetime.now()
    ).dt.days
    return df

# Function to plot volatility surface
def plot_volatility_surface(df):
    pivot_data = df.pivot_table(
        index="days_to_expiration",
        columns="moneyness",
        values="impliedVolatility",
    )
    x = pivot_data.columns
    y = pivot_data.index
    z = pivot_data.values

    fig = go.Figure(data=[go.Surface(z=z, x=x, y=y)])
    fig.update_layout(
        title="Volatility Surface",
        scene=dict(
            xaxis_title="Moneyness",
            yaxis_title="Days to Expiration",
            zaxis_title="Implied Volatility",
        ),
    )
    return fig

# Function to plot time skew
def plot_time_skew(df):
    grouped = df.groupby("days_to_expiration")["impliedVolatility"].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grouped.index, y=grouped.values, mode="lines+markers"))
    fig.update_layout(
        title="Time Skew",
        xaxis_title="Days to Expiration",
        yaxis_title="Average Implied Volatility",
    )
    return fig

# Streamlit app
st.title("Volatility Surface and Time Skew Analysis")

# User input for ticker
symbol = st.text_input("Enter the ticker symbol:", value="SPY")

if st.button("Fetch Data"):
    with st.spinner("Fetching data..."):
        data = fetch_options_data(symbol)

    if data is not None:
        st.success("Data fetched successfully!")

        # Preprocess data
        data = preprocess_data(data)

        # Volatility Surface
        st.subheader("Volatility Surface")
        surface_fig = plot_volatility_surface(data)
        st.plotly_chart(surface_fig)

        # Time Skew
        st.subheader("Time Skew")
        skew_fig = plot_time_skew(data)
        st.plotly_chart(skew_fig)