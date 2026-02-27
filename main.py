"""
📈 India Stock Market Morning Brief
"""

import os
import json
import smtplib
import datetime
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import yfinance as yf
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY    = os.getenv("NEWS_API_KEY")
EMAIL_ADDRESS   = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# Load stocks from config file
with open("stocks.json", "r") as f:
    config = json.load(f)

INDIAN_STOCKS = {**config["indices"], **config["stocks"]}


def get_market_data():
    print("📊 Fetching market data...")
    results = []
    for ticker, name in INDIAN_STOCKS.items():
        try:
            stock = yf.Ticker(ticker)
            hist  = stock.history(period="2d")
            if len(hist) < 2:
                continue
            yesterday  = hist.iloc[-1]
            prev_day   = hist.iloc[-2]
            change_pct = ((yesterday["Close"] - prev_day["Close"]) / prev_day["Close"]) * 100
            results.append(
                f"• {name} ({ticker}): "
                f"Close ₹{yesterday['Close']:.2f} | "
                f"Change: {change_pct:+.2f}% | "
                f"Volume: {int(yesterday['Volume']):,}"
            )
        except Exception as e:
            results.append(f"• {name}: Data unavailable")
    print(f"   ✅ Got data for {len(results)} stocks")
    return "\n".join(results)


def get_market_news():
    print("📰 Fetching news...")
    headlines = []
    if NEWS_API_KEY:
        try:
            url = (
                "https://newsapi.org/v2/everything"
    f"?q=india+stock+market+NSE+BSE&language=en&pageSize=15&apiKey={NEWS_API_KEY}"
            )
            response = requests.get(url, timeout=10)
            data     = response.json()
            if data.get("status") == "ok":
                for article in data.get("articles", []):
                    title = article.get("title", "")
                    desc  = article.get("description", "")
                    src   = article.get("source", {}).get("name", "")
                    if title and "[Removed]" not in title:
                        headlines.append(f"[{src}] {title} — {desc}")
        except Exception as e:
            print(f"   ⚠️  NewsAPI error: {e}")
    if len(headlines) < 5:
        try:
            rss_url  = "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
            rss_resp = requests.get(rss_url, timeout=10)
            titles   = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", rss_resp.text)
            for t in titles[:10]:
                headlines.append(f"[Economic Times] {t}")
        except Exception as e:
            print(f"   ⚠️  RSS error: {e}")
    print(f"   ✅ Found {len(headlines)} headlines")
    return "\n".join(headlines) if headlines else "No news available."


def analyze_with_gemini(market_data, news):
    print("🤖 Asking Groq to analyze...")

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    today  = datetime.datetime.now().strftime("%A, %d %B %Y")

    prompt = f"""
You are a senior Indian stock market analyst writing a morning brief for a retail investor.
Today is {today}. Analyze the data below and provide a structured report in HTML format.

YESTERDAY'S MARKET PERFORMANCE:
{market_data}

TODAY'S NEWS:
{news}

Provide your response in this exact HTML structure:

<h2>1. Market Recap</h2>
<p>How did the market perform yesterday? Key movers and why.</p>

<h2>2. Key News To Watch</h2>
<p>Top 5 news stories that could move the market today and why they matter.</p>

<h2>3. Companies To Watch Today</h2>
<p>3-5 specific stocks likely to move today, whether UP or DOWN, and why.</p>

<h2>4. Today's Strategy</h2>
<p>Overall sentiment (Bullish/Bearish/Neutral) and what a retail investor should consider.</p>

<h2>5. Pre-News Movers</h2>
<p>Any stocks that moved before related news became public — possible smart money signals.</p>

<h2>6. Risk Alerts</h2>
<p>Key risks to watch out for today.</p>

Be specific with company names and numbers. Use Rs for prices.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2500
    )
    print("   ✅ Analysis done!")
    return response.choices[0].message.content

def build_email_html(analysis):
    today = datetime.datetime.now().strftime("%A, %d %B %Y")
    return f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f6f9; padding: 20px; }}
    .container {{ max-width: 700px; margin: auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
    .header {{ background: linear-gradient(135deg, #1a3c5e, #2e7d32); color: white; padding: 30px; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 26px; }}
    .header p {{ margin: 8px 0 0; opacity: 0.85; font-size: 14px; }}
    .content {{ padding: 30px; }}
    h2 {{ color: #1a3c5e; border-left: 4px solid #2e7d32; padding-left: 12px; }}
    p {{ line-height: 1.7; color: #444; }}
    .footer {{ background: #f0f0f0; text-align: center; padding: 15px; font-size: 12px; color: #888; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📈 India Market Morning Brief</h1>
      <p>{today} | NSE &amp; BSE Analysis</p>
    </div>
    <div class="content">{analysis}</div>
    <div class="footer">
      AI generated report. <strong>Not financial advice.</strong> Always do your own research.
    </div>
  </div>
</body>
</html>
"""


def send_email(html_content):
    print(f"📧 Sending email to {RECIPIENT_EMAIL}...")
    today          = datetime.datetime.now().strftime("%d %b %Y")
    msg            = MIMEMultipart("alternative")
    msg["Subject"] = f"📈 India Market Brief — {today}"
    msg["From"]    = EMAIL_ADDRESS
    msg["To"]      = RECIPIENT_EMAIL
    msg.attach(MIMEText(html_content, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
    print("   ✅ Email sent!")


def main():
    print("\n" + "="*50)
    print("  🌅 India Stock Market Morning Brief")
    print("="*50 + "\n")
    market_data = get_market_data()
    news        = get_market_news()
    analysis    = analyze_with_gemini(market_data, news)
    email_html  = build_email_html(analysis)
    send_email(email_html)
    print("\n✅ All done! Check your inbox.\n")


if __name__ == "__main__":
    main()
