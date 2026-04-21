import os, requests
from bs4 import BeautifulSoup
HEADERS = {"User-Agent": os.environ["SEC_USER_AGENT"]}

def ticker_to_cik(ticker: str) -> str:
    r = requests.get("https://www.sec.gov/files/company_tickers.json",
                     headers=HEADERS, timeout=15).json()
    for row in r.values():
        if row["ticker"].upper() == ticker.upper():
            return str(row["cik_str"]).zfill(10)
    raise ValueError(f"CIK not found for {ticker}")

def latest_10k_text(ticker: str) -> str:
    cik = ticker_to_cik(ticker)
    subs = requests.get(
        f"https://data.sec.gov/submissions/CIK{cik}.json",
        headers=HEADERS, timeout=15).json()
    forms = subs["filings"]["recent"]
    for i, form in enumerate(forms["form"]):
        if form in ("10-K", "10-Q"):
            acc = forms["accessionNumber"][i].replace("-", "")
            doc = forms["primaryDocument"][i]
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}"
            html = requests.get(url, headers=HEADERS, timeout=30).text
            return BeautifulSoup(html, "html.parser").get_t