from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin
import pickle
import os


def fetch_case_types():
    return [
        ("CS", "Civil Suit"), ("CR", "Criminal Revision"), ("FIR", "First Information Report"),
        ("MACP", "Motor Accident Claim Petition"), ("ARBTN", "Arbitration Case"),
        ("CA", "Civil Appeal"), ("CAVEAT", "Caveat"), ("COMA", "Company Application"),
        ("COMO", "Company Petition"), ("CS-COM", "Civil Suit Commercial"),
        ("CS-EX", "Civil Suit Execution"), ("CS-OS", "Civil Suit Original Side"),
        ("EA", "Execution Application"), ("HMA", "Hindu Marriage Act Case"),
        ("MACT", "Motor Accident Compensation Tribunal"), ("MCA", "Miscellaneous Civil Appeal"),
        ("MISC", "Miscellaneous Application"), ("NIA", "Negotiable Instruments Act Case"),
        ("PA", "Probate Application"), ("PC", "Probate Case"), ("PS", "Partition Suit"),
        ("RA", "Regular Appeal"), ("RC", "Rent Control"), ("RCS", "Regular Civil Suit"),
        ("SC", "Small Cause Case"), ("SS", "Summary Suit"), ("SUCC", "Succession Case")
    ]


def clean_text(text):
    return re.sub(r'[\n\r;:]+', ' ', text).strip()


def safe_get(soup, selector):
    el = soup.select_one(selector)
    return clean_text(el.text) if el else "N/A"


def safe_td(soup, label):
    label_td = soup.find("td", string=lambda t: t and label.lower() in t.lower())
    if label_td and label_td.find_next_sibling("td"):
        return clean_text(label_td.find_next_sibling("td").text)
    return "N/A"


def extract_parties(soup):
    parties = {"petitioner": "N/A", "respondent": "N/A"}

    petitioner_table = soup.find("table", class_="Petitioner_Advocate_table")
    if petitioner_table:
        petitioner_names = [
            cell.get_text(strip=True)
            for row in petitioner_table.find_all("tr")
            for cell in row.find_all("td")
            if cell.get_text(strip=True)
        ]
        if petitioner_names:
            parties["petitioner"] = "; ".join(petitioner_names)

    respondent_table = soup.find("table", class_="Respondent_Advocate_table")
    if respondent_table:
        respondent_names = [
            cell.get_text(strip=True)
            for row in respondent_table.find_all("tr")
            for cell in row.find_all("td")
            if cell.get_text(strip=True)
        ]
        if respondent_names:
            parties["respondent"] = "; ".join(respondent_names)

    return parties

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pickle
import os
import time
import re

BASE_URL = "https://services.ecourts.gov.in/ecourtindia_v6/"

def extract_pdf_url(a_tag):
    """Extract PDF URL from <a> tag, works for direct or onclick links."""
    if a_tag.has_attr("href") and a_tag["href"].endswith(".pdf"):
        # Direct PDF link
        return urljoin(BASE_URL, a_tag["href"])

    onclick = a_tag.get("onclick", "")
    match = re.search(r"filename=([^&'\"]+)", onclick)
    if match:
        pdf_relative = match.group(1)
        return urljoin(BASE_URL, pdf_relative)

    return None

def fetch_case_data(case_type, case_number, filing_year, soup=None):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get("https://services.ecourts.gov.in/ecourtindia_v6/")
    print("\n🔐 Please manually select: State = HARYANA, District = FARIDABAD")
    print("➡️ Fill in Court Complex, Case Type, Case No, Year → Solve CAPTCHA → Click Go → View")
    input("\n⏳ Press ENTER once the full case detail page has loaded...\n")

    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    base_url = "https://services.ecourts.gov.in"
    parties = extract_parties(soup)

    case_data = {
        "case_type": case_type,
        "case_number": case_number,
        "filing_year": filing_year,
        "filing_date": safe_td(soup, "Filing Date"),
        "petitioner": parties.get("petitioner", "N/A"),
        "respondent": parties.get("respondent", "N/A"),
        "order_links": [],
        "acts": [],
        "history": [],
        "interim_orders": [],
        "final_orders": [],
        "ia_applications": [],
        "transfers": []
    }

    # --- MAIN ORDERS TABLE ---
    orders_table = soup.find('table', class_='table table-bordered')
    if orders_table:
        rows = orders_table.find_all('tr')[1:]
        for i, row in enumerate(rows, 1):
            cols = row.find_all('td')
            if len(cols) >= 2:
                order_date = cols[0].get_text(strip=True)
                link_tag = cols[1].find('a')
                pdf_url = extract_pdf_url(link_tag) if link_tag else None
                if pdf_url:
                    order_info = {
                        'order_number': str(i),
                        'order_date': order_date,
                        'order_link': f"/view_pdf?url={pdf_url}"
                    }
                    link_text = link_tag.get_text(strip=True).lower()
                    if 'final' in link_text or 'judgment' in link_text:
                        case_data['final_orders'].append(order_info)
                    else:
                        case_data['interim_orders'].append(order_info)

    # --- DETAILED TABLES (INTERIM + FINAL) ---
    detailed_tables = soup.select("table.order_table")
    for idx, table in enumerate(detailed_tables):
        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3 and cols[2].find('a'):
                pdf_url = extract_pdf_url(cols[2].a)
                if pdf_url:
                    order = {
                        "order_number": cols[0].text.strip(),
                        "order_date": cols[1].text.strip(),
                        "order_link": f"/view_pdf?url={pdf_url}"
                    }
                    if idx == 0:
                        case_data["interim_orders"].append(order)
                    elif idx == 1:
                        case_data["final_orders"].append(order)

    # --- ADDITIONAL FINAL ORDERS TABLE ---
    order_table = soup.find("table", class_="table_borderless")
    if order_table:
        rows = order_table.find_all("tr")[1:]
        for i, row in enumerate(rows, 1):
            cells = row.find_all("td")
            if len(cells) >= 2:
                order_date = cells[1].text.strip()
                link_tag = cells[1].find("a")
                pdf_url = extract_pdf_url(link_tag) if link_tag else None
                if pdf_url:
                    case_data["final_orders"].append({
                        "order_number": f"{i}",
                        "order_date": order_date,
                        "order_link": f"/view_pdf?url={pdf_url}"
                    })

    # --- JUDGMENT LINKS FROM HISTORY TABLE ---
    history_table = soup.find("table", class_="history_table")
    if history_table:
        rows = history_table.find_all("tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                link_tag = cols[2].find("a")
                pdf_url = extract_pdf_url(link_tag) if link_tag else None
                if pdf_url:
                    case_data["final_orders"].append({
                        "order_number": cols[0].text.strip(),
                        "order_date": cols[1].text.strip(),
                        "order_link": f"/view_pdf?url={pdf_url}"
                    })

    # --- ACTS INVOLVED (Improved) ---
    case_data["acts"] = []
    act_cells = soup.find_all("td", string=lambda t: t and "Act" in t)
    for cell in act_cells:
        val_cell = cell.find_next_sibling("td")
        if val_cell:
            acts_text = clean_text(val_cell.get_text())
            for act in acts_text.replace("\n", ",").split(","):
                act = act.strip()
                if act and act not in case_data["acts"]:
                    case_data["acts"].append(act)

    # --- IA APPLICATIONS ---
    ia_header = soup.find("td", string=lambda t: t and "Interlocutory" in t)
    if ia_header:
        ia_table = ia_header.find_parent("table")
        rows = ia_table.find_all("tr")[1:] if ia_table else []
        for row in rows:
            cols = [clean_text(td.text) for td in row.find_all("td")]
            if cols:
                case_data["ia_applications"].append(" | ".join(cols))

    # --- HISTORY ENTRIES ---
    history_header = soup.find("td", string=lambda t: t and "Business on Date" in t)
    if history_header:
        history_table = history_header.find_parent("table")
        rows = history_table.find_all("tr")[1:] if history_table else []
        for row in rows:
            cols = [clean_text(td.text) for td in row.find_all("td")]
            if cols:
                case_data["history"].append(" → ".join(cols))

    # --- TRANSFER DETAILS ---
    transfer_header = soup.find("td", string=lambda t: t and "Transfer Details" in t)
    if transfer_header:
        transfer_table = transfer_header.find_parent("table")
        rows = transfer_table.find_all("tr")[1:] if transfer_table else []
        for row in rows:
            cols = [clean_text(td.text) for td in row.find_all("td")]
            if cols:
                case_data["transfers"].append(" | ".join(cols))

    # --- SAVE SELENIUM COOKIES ---
    COOKIES_FILE = "session_cookies.pkl"
    try:
        cookies = driver.get_cookies()
        with open(COOKIES_FILE, "wb") as f:
            pickle.dump(cookies, f)
        print(f"✅ Session cookies saved to {os.path.abspath(COOKIES_FILE)}")
    except Exception as e:
        print(f"⚠ Could not save cookies: {e}")

    driver.quit()
    return case_data, soup.prettify()
