import requests

def fetch_page(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.content
    else:
        print(f"Failed to retrieve the page. Status code: {r.status_code}")
        return None

url = "https://yigm.ktb.gov.tr/TR-249704/aylik-bultenler.html"
html_content = fetch_page(url)
print(html_content)