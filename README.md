# India Stock Market Morning Brief

An automated stock market analysis tool that delivers a personalized daily briefing 
to your inbox every morning at 7:30 AM IST, covering NSE and BSE markets.

## Overview

This project fetches real-time stock data and financial news, analyzes it using 
Google Gemini AI, and sends a structured HTML email report with actionable insights 
for retail investors.

## What the Report Covers

- Market recap of previous day performance across NIFTY 50, SENSEX, and top stocks
- Key news stories likely to impact the market that day
- Specific companies to watch with directional outlook
- Overall market sentiment and suggested strategy for the day
- Pre-news mover detection to identify unusual price activity
- Risk alerts for the trading session

## Tech Stack

- Python 3.10
- Google Gemini AI API for market analysis
- yfinance for real-time NSE/BSE stock data
- NewsAPI and Economic Times RSS for financial news
- Gmail SMTP for email delivery
- GitHub Actions for automated daily scheduling

## Project Structure
india-market-brief/
├── main.py              # Core script handling data fetch, analysis, and email
├── stocks.json          # Configurable list of stocks and indices to track
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── .gitignore           # Ignored files including secrets
└── .github/
└── workflows/
└── morning-brief.yml   # GitHub Actions scheduler
## Setup Instructions

### 1. Clone the repository

git clone https://github.com/KJProg/india-market-brief.git
cd india-market-brief

### 2. Install dependencies

pip install -r requirements.txt

### 3. Configure environment variables

Copy .env.example to .env and fill in your credentials:

cp .env.example .env

Required variables:

- GEMINI_API_KEY — Google Gemini API key from aistudio.google.com
- NEWS_API_KEY — Free API key from newsapi.org
- EMAIL_ADDRESS — Gmail address used to send the report
- EMAIL_PASSWORD — Gmail App Password (not your regular password)
- RECIPIENT_EMAIL — Email address where the report is delivered

### 4. Run manually

python3 main.py

## Automated Scheduling

The project uses GitHub Actions to run automatically every weekday at 7:30 AM IST.
To enable this, add your environment variables as repository secrets:

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add each variable from your .env file as a repository secret

## Customizing Stocks

To add or remove stocks, edit stocks.json directly. No changes to main.py are needed.

Example:

{
  "stocks": {
    "ZOMATO.NS": "Zomato",
    "NYKAA.NS": "Nykaa"
  }
}

## Cost

- Google Gemini API: Free tier (sufficient for one request per day)
- NewsAPI: Free tier (100 requests per day)
- GitHub Actions: Free tier
- Gmail SMTP: Free

## Disclaimer

This tool is for educational and personal use only. The analysis generated is 
AI-powered and does not constitute financial advice. Always conduct your own 
research before making investment decisions.

## Author

Keshav — github.com/KJProg
