import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from io import BytesIO
import urllib.parse
import os
from urllib.parse import urlparse, unquote

def fetch_page(url):
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
    print(sorted_year_urls)
    latest_year_url = sorted_year_urls[0] #### First html url
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
    """
    Downloads the Excel file from the given href.
    Returns the content of the file if successful, else None.
    """
    encoded_href = urllib.parse.quote(href, safe=':/?&=')
    response = requests.get(encoded_href, verify=False)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to retrieve {href}, status code: {response.status_code}")
        return None


### main execution
base_url = "https://yigm.ktb.gov.tr/"
url = "https://yigm.ktb.gov.tr/TR-249704/aylik-bultenler.html"
html_content = fetch_page(url)
#print(html_content)
#print(get_year_urls(html_content, url))

excel_links = extract_excel_links(html_content)
print(excel_links)

for href in excel_links:
    excel_content = download_excel_file(href)
    
    if excel_content:
        # Query string'i temizle ve dosya adını al
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
            df = pd.read_excel(BytesIO(excel_content), sheet_name="Giren Vat.", engine=engine)
            print(df.head())
        except Exception as e:
            print(f"Error reading Excel file {href}: {e}")