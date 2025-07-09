import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from io import BytesIO
import os
from urllib.parse import urlparse, unquote
import re
import unicodedata
import urllib.parse
from sqlalchemy.orm import sessionmaker
from sqlalchemy import extract
from models import ist_sinir_kapilari_giris_yapan_vatandas
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from models import engine
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.content
    except requests.RequestException as e:
        logger.error(f"Failed to retrieve the page {url}: {e}")
        return None

def get_year_urls(html, start_year=2022):
    soup = BeautifulSoup(html, "html.parser")
    year_urls = []

    for a in soup.find_all("a", href=True, title=True):
        if a["title"].isdigit():
            year = int(a["title"])
            if year >= start_year:
                full_url = urljoin("https://yigm.ktb.gov.tr/", a["href"])
                year_urls.append(full_url)

    return year_urls

def extract_excel_links(html, start_year=2022):
    year_urls = get_year_urls(html, start_year=start_year)
    sorted_year_urls = sorted(year_urls, key=lambda x: int(x.split("/")[-1].split(".")[0]), reverse=True)
    logger.info(f"Year URLs: {sorted_year_urls}")

    excel_links = []
    for year_url in sorted_year_urls:
        year_page_content = fetch_page(year_url)
        if not year_page_content:
            continue

        soup = BeautifulSoup(year_page_content, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if ".xls" in href or ".xlsx" in href:
                full_url = urljoin("https://yigm.ktb.gov.tr/", href)
                logger.info(f"Found excel is: {full_url}")
                excel_links.append(full_url)

    logger.info(f"Total Excel files found: {len(excel_links)}")
    return excel_links

def download_excel_file(href):
    encoded_href = urllib.parse.quote(href, safe=':/?&=')
    try:
        response = requests.get(encoded_href, verify=False)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logger.error(f"Failed to download file {href}: {e}")
        return None

def normalize_text(text):
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text

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

def get_excel_engine(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".xls":
        return "xlrd"
    elif ext == ".xlsx":
        return "openpyxl"
    return None

def load_excel_file(excel_content, engine):
    try:
        with BytesIO(excel_content) as f:
            xl = pd.ExcelFile(f, engine=engine)
        return pd.read_excel(BytesIO(excel_content), sheet_name="Giren Vat.", na_values=True, engine=engine)
    except Exception as e:
        logger.error(f"Error loading Excel: {e}")
        return None

def extract_month_year_from_filename(filename):
    filename_norm = normalize_text(filename)
    match = re.search(r"\b(" + "|".join(month_mapping) + r")[\W_]*?(\d{4})\b", filename_norm)
    if match:
        raw_month, year = match.groups()
        return month_mapping.get(raw_month), year
    return None, None

def clean_istanbul_data(df):
    df.iloc[:, 0] = df.iloc[:, 0].ffill()
    df_city = df[df.iloc[:, 0] == "İstanbul"].copy()
    df_city.fillna(0, inplace=True)
    return df_city

def reshape_city_data(df_city, month_index, year_str):
    selected_months = months_tr[:month_index + 1]
    selected_columns = [0, 1] + list(range(3, 3 + len(selected_months)))
    df_city = df_city.iloc[:, selected_columns]
    df_city.columns = ["sehir", "sinir_kapilari"] + selected_months

    df_melted = df_city.melt(
        id_vars=["sehir", "sinir_kapilari"],
        var_name="ay",
        value_name="vatandas_sayisi"
    )

    def create_date(row):
        month_num = months_tr.index(row["ay"]) + 1
        return datetime(int(year_str), month_num, 1)

    df_melted["tarih"] = df_melted.apply(create_date, axis=1)
    return df_melted[["sehir", "sinir_kapilari", "tarih", "vatandas_sayisi"]]

def process_single_excel(href):
    logger.info(f"Processing file: {href}")
    content = download_excel_file(href)
    if not content:
        return None

    path = urlparse(href).path
    filename = unquote(os.path.basename(path))
    logger.info(f"--- File name: {filename}")
    engine = get_excel_engine(filename)

    if not engine:
        logger.warning(f"Unsupported extension for {filename}")
        return None

    df = load_excel_file(content, engine)
    if df is None:
        return None

    df_city = clean_istanbul_data(df)
    month_str, year_str = extract_month_year_from_filename(filename)

    if not month_str or not year_str:
        logger.warning(f"Month/year not extracted from filename: {filename}")
        return None

    try:
        month_index = months_tr.index(month_str)
        return reshape_city_data(df_city, month_index, year_str)
    except ValueError:
        logger.warning(f"Invalid month string: {month_str}")
        return None

def combine_all_data(excel_links):
    all_data = []

    for href in excel_links:
        df = process_single_excel(href)
        if df is not None:
            all_data.append(df)

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df_drop_duplicate = combined_df.drop_duplicates(subset=["sehir", "sinir_kapilari", "tarih", "vatandas_sayisi"])
        return combined_df_drop_duplicate     
    else:
        logger.warning("No valid data extracted.")
        return None

def check_record_exists(session, month, year, sinir_kapilari):
    exists = (
        session.query(ist_sinir_kapilari_giris_yapan_vatandas)
        .filter(
            extract('month', ist_sinir_kapilari_giris_yapan_vatandas.tarih) == month,
            extract('year', ist_sinir_kapilari_giris_yapan_vatandas.tarih) == year,
            ist_sinir_kapilari_giris_yapan_vatandas.sinir_kapilari == sinir_kapilari
        )
        .first()
    )
    return exists is not None ## Boolean

def save_to_database(df, session):
    for _, row in df.iterrows():
        try:
            vatandas_sayisi = float(str(row["vatandas_sayisi"]).replace(".","").replace(",",""))
            new_record = ist_sinir_kapilari_giris_yapan_vatandas(
                tarih = row["tarih"],
                sehir = row["sehir"],
                sinir_kapilari = row["sinir_kapilari"],
                vatandas_sayisi = vatandas_sayisi,
                erisim_tarihi = datetime.today().strftime("%Y-%m-%d")
            )
            session.add(new_record)
            session.commit()
        except ValueError:
            logger.error(f"ValueError on row: {row}")
            session.rollback()
        except IntegrityError:
            logger.warning(f"Duplicate entry for date {row['tarih']}. Skipping...")
            session.rollback()
    logger.info("Data committed to database.")

def main_02_03_ktb():
    # Main execution
    Session = sessionmaker(bind=engine)
    session = Session()

    base_url = "https://yigm.ktb.gov.tr/"
    url = "https://yigm.ktb.gov.tr/TR-249704/aylik-bultenler.html"
    html_content = fetch_page(url)
    if not html_content:
        logger.error("Main page content couldn't be fetched.")
        return

    excel_links = extract_excel_links(html_content, start_year=2022)

    for href in excel_links:
        df = process_single_excel(href)
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                tarih = row["tarih"]
                year = tarih.year
                month = tarih.month
                sinir_kapilari = row["sinir_kapilari"]

                if check_record_exists(session, month, year, sinir_kapilari):
                    logger.info(f"Already exists: {tarih.month}/{tarih.year} - {row['sinir_kapilari']}")
                else:
                    logger.info(f"Inserting {tarih.month}/{tarih.year} - {row['sinir_kapilari']}")
                    save_to_database(pd.DataFrame([row]), session)
        else:
            logger.warning(f"No data extracted from: {href}")
    session.close()
    logger.info("ETL process completed successfully.")

main_02_03_ktb()