import os
import io
import base64
import logging
import requests
import pandas as pd
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.conf import settings
from .forms import IndicatorForm
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def index(request):
    if request.method == 'POST':
        form = IndicatorForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            function = form.cleaned_data['function']
            interval = form.cleaned_data['interval']
            series_type = form.cleaned_data['series_type']

            # Fetch data
            data = fetch_indicator_data(symbol, function, interval, series_type)
            if data is None:
                return render(request, 'alpha_vantage_app/index.html', {
                    'form': form,
                    'error': 'Failed to fetch data. Please try again.'
                })

            # Process data
            df = process_indicator_data(data, function)
            if df is None or df.empty:
                return render(request, 'alpha_vantage_app/index.html', {
                    'form': form,
                    'error': 'No data available for the given parameters.'
                })

            # Generate plot
            chart = plot_data(df, symbol, function)

            return render(request, 'alpha_vantage_app/plot.html', {
                'chart': chart,
                'symbol': symbol,
                'function': function
            })
    else:
        form = IndicatorForm()

    return render(request, 'alpha_vantage_app/index.html', {'form': form})

def fetch_indicator_data(symbol, function, interval, series_type):
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    base_url = 'https://www.alphavantage.co/query'

    params = {
        'function': function,
        'symbol': symbol,
        'interval': interval,
        'series_type': series_type,
        'apikey': api_key
    }

    try:
        logger.info(f"Requesting data for {symbol}...")
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Check for API errors
        if 'Error Message' in data:
            logger.error(f"API Error: {data['Error Message']}")
            return None
        elif f'Technical Analysis: {function}' in data:
            logger.info("Data retrieval successful.")
            return data
        else:
            logger.error("Unexpected API response format.")
            return None

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logger.error(f"An error occurred: {err}")

    return None

def process_indicator_data(data, function):
    key = f'Technical Analysis: {function}'
    if key not in data:
        logger.error("Expected data key not found in response.")
        return None

    try:
        df = pd.DataFrame.from_dict(data[key], orient='index')
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        logger.info("Data processing successful.")
        return df
    except Exception as e:
        logger.error(f"Data processing error: {e}")
        return None

def plot_data(df, symbol, function):
    try:
        plt.switch_backend('AGG')  # Use Anti-Grain Geometry backend for PNG output
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df['InPhase'], label='InPhase')
        plt.plot(df.index, df['Quadrature'], label='Quadrature')
        plt.title(f'{function} for {symbol}')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # Save plot to a PNG in memory
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        # Encode PNG image to base64 string
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
        plt.close()
        logger.info("Plotting successful.")
        return graphic
    except Exception as e:
        logger.error(f"Plotting error: {e}")
        return None
