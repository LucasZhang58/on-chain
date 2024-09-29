import os

import streamlit as st
import requests
from web3 import Web3
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

# Only import and use dotenv if we're not on Streamlit Cloud
if not os.getenv('STREAMLIT_CLOUD'):
    from dotenv import load_dotenv
    load_dotenv()

# Function to get Infura project ID
def get_infura_project_id():
    # First, try to get the project ID from environment variables
    project_id = os.getenv("INFURA_PROJECT_ID")
    
    if project_id:
        return project_id
    
    # If not found in environment variables, check Streamlit secrets
    # This part will only run when deployed on Streamlit Cloud
    if 'infura' in st.secrets:
        return st.secrets.infura.project_id
    
    # If project ID is not found anywhere, show an error and stop the app
    st.error("Infura Project ID not found. Please set it in .env file or Streamlit secrets.")
    st.stop()

# Use the function to get the project ID
infura_project_id = get_infura_project_id()
infura_url = f"https://mainnet.infura.io/v3/{infura_project_id}"
w3 = Web3(Web3.HTTPProvider(infura_url))

st.title("Ethereum On-Chain Analytics")

# Function to get latest blocks
def get_latest_blocks(num_blocks):
    latest = w3.eth.block_number
    blocks = []
    for i in range(num_blocks):
        block = w3.eth.get_block(latest - i)
        blocks.append({
            'number': block['number'],
            'timestamp': block['timestamp'],
            'transactions': len(block['transactions']),
            'gas_used': block['gasUsed'],
            'gas_limit': block['gasLimit']
        })
    return blocks

# Function to get ETH price
def get_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data['ethereum']['usd']

# Sidebar
st.sidebar.header("Configuration")
num_blocks = st.sidebar.slider("Number of blocks to analyze", 10, 100, 50)

st.image("https://cryptonary.com/cdn-cgi/image/width=1080/https://cryptonary.s3.eu-west-2.amazonaws.com/wp-content/uploads/2022/06/On-Chain.png")

# Main content
if st.button("Refresh Data"):
    with st.spinner("Fetching on-chain data..."):
        blocks = get_latest_blocks(num_blocks)
        eth_price = get_eth_price()

    st.subheader(f"Latest {num_blocks} Blocks")
    df = pd.DataFrame(blocks)
    st.dataframe(df)

    # Visualizations
    st.subheader("Transactions per Block")
    fig1 = px.line(df, x='number', y='transactions', title='Transactions per Block')
    st.plotly_chart(fig1)

    st.subheader("Gas Usage")
    fig2 = px.line(df, x='number', y=['gas_used', 'gas_limit'], title='Gas Usage and Limit per Block')
    st.plotly_chart(fig2)

    st.subheader("Ethereum Price")
    st.metric("Current ETH Price", f"${eth_price:.2f}")

st.sidebar.info("This app provides basic on-chain analytics for Ethereum. Refresh the data to get the latest information.")