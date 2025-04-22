import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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


### main execution
base_url = "https://yigm.ktb.gov.tr/"
url = "https://yigm.ktb.gov.tr/TR-249704/aylik-bultenler.html"
html_content = fetch_page(url)
#print(html_content)
#print(get_year_urls(html_content, url))

excel_links = extract_excel_links(html_content)
print(excel_links)