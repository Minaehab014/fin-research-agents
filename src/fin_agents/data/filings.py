import os, requests
from dataclasses import dataclass
from bs4 import BeautifulSoup


def _headers() -> dict:
    return {"User-Agent": os.environ["SEC_USER_AGENT"]}


@dataclass
class Filing:
    ticker: str
    filing_type: str
    filing_date: str
    text: str


def ticker_to_cik(ticker: str) -> str:
    r = requests.get("https://www.sec.gov/files/company_tickers.json",
                     headers=_headers(), timeout=15).json()
    for row in r.values():
        if row["ticker"].upper() == ticker.upper():
            return str(row["cik_str"]).zfill(10)
    raise ValueError(f"CIK not found for {ticker}")


def latest_filing(ticker: str) -> Filing:
    cik = ticker_to_cik(ticker)
    subs = requests.get(
        f"https://data.sec.gov/submissions/CIK{cik}.json",
        headers=_headers(), timeout=15).json()
    forms = subs["filings"]["recent"]
    for i, form in enumerate(forms["form"]):
        if form in ("10-K", "10-Q"):
            acc = forms["accessionNumber"][i].replace("-", "")
            doc = forms["primaryDocument"][i]
            filing_date = forms["filingDate"][i]
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}"
            html = requests.get(url, headers=_headers(), timeout=30).text
            text = BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)
            return Filing(
                ticker=ticker.upper(),
                filing_type=form,
                filing_date=filing_date,
                text=text,
            )
    raise ValueError(f"No 10-K or 10-Q found for {ticker}")
