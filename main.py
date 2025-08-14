import os

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
news_api_key = os.getenv("NEWSAPI_KEY")
email_sender = os.getenv("EMAIL_SENDER")
alpha_api_key = os.getenv("ALPHAVANTAGE_API_KEY")
email_password = os.getenv('EMAIL_PASSWORD')
email_receiver = os.getenv('EMAIL_RECEIVER')


url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSLA&apikey={alpha_api_key}'
r = requests.get(url)
data = r.json()
print(data)



date_list = []
for key, value in data['Time Series (Daily)'].items():
    if len(date_list) < 3:
        date_list.append(key)
    else:
        break
print(date_list)
opening_price = float(data['Time Series (Daily)'][date_list[1]]['1. open'])
closing_price = float(data['Time Series (Daily)'][date_list[2]]['4. close'])

# Calculate percentage change
difference_in_price = float(closing_price) - float(opening_price)
percent_change = (difference_in_price / opening_price) * 100
percent_change = round(percent_change, 2)


if abs(percent_change) >= 5:
    news_parameters = {
        'q': "Tesla",
        "country": "us",
        'from': date_list[0],
        'sortBy': 'popularity',
        'apiKey': NEWSAPI_KEY,
    }

    url = 'https://newsapi.org/v2/top-headlines'
    response = requests.get(url, params=news_parameters)
    data2 = response.json()

    subject = f"{STOCK}: {'🔺' if percent_change > 0 else '🔻'}{abs(percent_change)}%"
    body = ""

    for article in data2["articles"][:3]:  # Get the first 3 articles
        title = article["title"]
        description = article["description"]
        body += f"Headline: {title}\n"
        body += f"Brief: {description}\n\n"

    # Create email message
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_sender, email_password)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
else:
    print("No significant price change to report.")


