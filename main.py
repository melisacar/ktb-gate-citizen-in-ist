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


def get_latest_year_url(html, url):
    soup = BeautifulSoup(html, "html.parser")
    year_urls = []

    for a in soup.find_all("a", href=True, title=True):
        if a["title"].isdigit():
            full_url = urljoin(base_url, a["href"])
            year_urls.append(full_url)
    return year_urls
    
### main execution
base_url = "https://yigm.ktb.gov.tr/"
url = "https://yigm.ktb.gov.tr/TR-249704/aylik-bultenler.html"
html_content = fetch_page(url)
#print(html_content)
print(get_latest_year_url(html_content, url))