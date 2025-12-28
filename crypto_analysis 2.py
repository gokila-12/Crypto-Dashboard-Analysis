import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def clean_percent(text):
    """
    Safely convert percentage text to float.
    Handles '', '—', and missing values.
    """
    text = text.replace("%", "").replace(",", "").strip()
    if text == "" or text == "—":
        return 0.0
    return float(text)

url = "https://coinmarketcap.com/"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

rows = soup.find("tbody").find_all("tr")

data = []

for row in rows[:200]:
    cols = row.find_all("td")
    
    if len(cols) < 7:
        continue

    name = cols[2].text.strip()
    

    price_text = cols[3].text.replace("$", "").replace(",", "").strip()
    if price_text == "":
        continue
    price = float(price_text)

    pct_1h = clean_percent(cols[4].text)                 # increase %
    pct_24h = abs(clean_percent(cols[5].text))           # decrease %
    pct_7d = clean_percent(cols[6].text)                 # increase %

    data.append([name, price, pct_1h, pct_24h, pct_7d])

df = pd.DataFrame(
    data,
    columns=["Coin", "Price", "Pct_1h", "Pct_24h_Decrease", "Pct_7d"]
)

print("Raw Data:")
print(df.head())
print("Total rows:", df.shape[0])

df["Price_1h_before"] = df["Price"] / (1 + df["Pct_1h"] / 100)
df["Price_24h_before"] = df["Price"] / (1 - df["Pct_24h_Decrease"] / 100)
df["Price_7d_before"] = df["Price"] / (1 + df["Pct_7d"] / 100)

filtered_df = df[(df["Price"] >= 0) & (df["Price"] <= 5)]

print("Filtered rows (0–5 USD):", filtered_df.shape[0])

top10 = filtered_df.sort_values(
    by="Price_1h_before",
    ascending=False
).head(10)

print("\nTop 10 Coins:")
print(top10[["Coin", "Price_1h_before"]])

x = np.arange(len(top10))
width = 0.35

plt.figure(figsize=(12, 6))

plt.bar(x - width/2, top10["Price_7d_before"], width, label="7 Days Before")
plt.bar(x + width/2, top10["Price_24h_before"], width, label="24 Hours Before")

plt.xticks(x, top10["Coin"], rotation=45, ha="right")
plt.ylabel("Price (USD)")
plt.title("Top 10 Crypto Coins (0–5 USD Range)")
plt.legend()
plt.tight_layout()

plt.savefig("Top10_Crypto_BarChart.png", dpi=300, bbox_inches="tight")
plt.show()



top10.to_csv("Top10_Crypto_Analysis.csv", index=False)

print("\n✔ Analysis completed successfully!")
print("✔ File saved: Top10_Crypto_Analysis.csv")
