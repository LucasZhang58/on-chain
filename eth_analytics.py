import streamlit as st
import requests
from web3 import Web3
import pandas as pd
import plotly.express as px

# Connect to Ethereum network (using Infura, you'll need to sign up for a free account)
# infura_url = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
# infura_url = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
infura_url = "https://mainnet.infura.io/v3/f45ab216c8fc4577a66c4a3e7b3d091a"
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