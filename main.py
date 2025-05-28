import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from io import BytesIO
import urllib.parse
import os
from urllib.parse import urlparse, unquote
import re
import unicodedata

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }
    r = requests.get(url)
    if r.status_code == 200:
        return r.content
    else:
        print(f"Failed to retrieve the page. Status code: {r.status_code}")
        return None

def get_year_urls(html):
    soup = BeautifulSoup(html, "html.parser")
    year_urls = []

    for a in soup.find_all("a", href=True, title=True):
        if a["title"].isdigit():
            full_url = urljoin(base_url, a["href"])
            year_urls.append(full_url)
    return year_urls

def extract_excel_links(html):
    year_urls = get_year_urls(html)
    sorted_year_urls = sorted(year_urls, key=lambda x: int(x.split("/")[-1].split(".")[0]), reverse=True)
    #print(sorted_year_urls)
    latest_year_url = sorted_year_urls[0]
    latest_year_content = fetch_page(latest_year_url)
    soup = BeautifulSoup(latest_year_content, "html.parser")
    
    excel_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".xls" in href or ".xlsx" in href:
            full_url = urljoin(base_url, href)
            excel_links.append(full_url)
    return excel_links

def download_excel_file(href):
    encoded_href = urllib.parse.quote(href, safe=':/?&=')
    response = requests.get(encoded_href, verify=False)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to retrieve {href}, status code: {response.status_code}")
        return None

def normalize_text(text):
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text

### Main execution
base_url = "https://yigm.ktb.gov.tr/"
url = "https://yigm.ktb.gov.tr/TR-249704/aylik-bultenler.html"
html_content = fetch_page(url)

excel_links = extract_excel_links(html_content)
#print(f"Excel links: {excel_links}")

# Turkish month names
months_tr = [
    "ocak", "subat", "mart", "nisan", "mayis", "haziran",
    "temmuz", "agustos", "eylul", "ekim", "kasim", "aralik"
]

# Month mapping
month_mapping = {
    "ocak": "ocak",
    "şubat": "subat", "subat": "subat", "şuba": "subat",
    "mart": "mart",
    "nisan": "nisan",
    "mayıs": "mayis", "mayis": "mayis",
    "haziran": "haziran",
    "temmuz": "temmuz",
    "ağustos": "agustos", "agustos": "agustos",
    "eylül": "eylul", "eylul": "eylul",
    "ekim": "ekim",
    "kasım": "kasim", "kasim": "kasim",
    "aralık": "aralik", "aralik": "aralik"
}

def prepare_all_month_df():
    for href in excel_links:
        excel_content = download_excel_file(href)

        if excel_content:
            path = urlparse(href).path
            filename = unquote(os.path.basename(path))
            extension = os.path.splitext(filename)[1].lower()

            if extension == ".xls":
                engine = "xlrd"
            elif extension == ".xlsx":
                engine = "openpyxl"
            else:
                print(f"Unsupported extension: {extension} in URL: {href}")
                continue

            try:
                with BytesIO(excel_content) as f:
                    xl = pd.ExcelFile(f, engine=engine)
                    #print("Sheet names:", xl.sheet_names)

                df = pd.read_excel(BytesIO(excel_content), sheet_name="Giren Vat.", na_values=True, engine=engine)
                #print(f"Filename: {filename}")
                df.iloc[:, 0] = df.iloc[:, 0].ffill()
                df_city = df[df.iloc[:, 0] == "İstanbul"].copy()
                df_city.fillna(0, inplace=True)

                filename_normalized = normalize_text(filename)
                match = re.search(r"\b(" + "|".join(month_mapping) + r")[\W_]*?(\d{4})\b", filename_normalized)

                if match:
                    raw_month, year_str = match.groups()
                    normalized_month = month_mapping.get(raw_month)

                    if normalized_month:
                        month_index = months_tr.index(normalized_month)
                        selected_months = months_tr[:month_index + 1]
                        selected_columns = [0, 1] + list(range(3, 3 + len(selected_months)))
                        df_city = df_city.iloc[:, selected_columns]
                        df_city.columns = ["City", "Border Gate"] + selected_months

                        df_melted = df_city.melt(
                            id_vars=["City", "Border Gate"], var_name="Month", value_name="Visitor Count"
                        )

                        def create_date(row):
                            month_num = months_tr.index(row["Month"]) + 1
                            return f"01-{month_num:02d}-{year_str}"

                        df_melted["Date"] = df_melted.apply(create_date, axis=1)
                        df_melted = df_melted[["City", "Border Gate", "Date", "Visitor Count"]]

                        print(df_melted.head(20))
                    else:
                        print(f"Unrecognized month in filename: '{raw_month}'")
                else:
                    print("Could not extract month and year info from filename.")

            except Exception as e:
                print(f"Error reading Excel file {href}: {e}")

#prepare_all_month_df()