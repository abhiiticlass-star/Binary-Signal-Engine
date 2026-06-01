from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Helper function for Analysis
def calculate_metrics(df):
    # Calculate SMA
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    
    # Calculate RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df.iloc[-1]

@app.route('/api/signals/<asset>')
def get_signal(asset):
    # Weekend Logic
    if datetime.now().weekday() >= 5:
        return jsonify({"signal": "MARKET CLOSED", "status": "CLOSED"})
    
    try:
        # Fetching data
        ticker = yf.Ticker(f"{asset}=X")
        df = ticker.history(period="1d", interval="1m")
        
        if df.empty:
            return jsonify({"signal": "SERVER ISSUE", "status": "ERROR"})
        
        last = calculate_metrics(df)
        
        # Confluence Logic
        if last['Close'] > last['SMA_20'] and last['RSI'] < 65:
            return jsonify({"signal": "UP", "confluence": "Bullish Trend"})
        elif last['Close'] < last['SMA_20'] and last['RSI'] > 35:
            return jsonify({"signal": "DOWN", "confluence": "Bearish Trend"})
        else:
            return jsonify({"signal": "AVOID", "confluence": "Neutral Market"})
            
    except:
        return jsonify({"signal": "SERVER ISSUE", "status": "ERROR"})

if __name__ == '__main__':
    app.run()
