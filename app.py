from flask import Flask, render_template, request, redirect, url_for, send_file, session, Response
from scraper import fetch_case_data, fetch_case_types
import os
import pdfkit
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime 
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import re
from urllib.parse import urljoin
import pickle
import time

# Configure wkhtmltopdf path
PDFKIT_CONFIG = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/", methods=["GET", "POST"])
def home():
    case_types = fetch_case_types()
    error = None

    if request.method == "POST":
        case_type = request.form.get("case_type")
        case_number = request.form.get("case_number")
        filing_year = request.form.get("filing_year")

        try:
            case_data, _ = fetch_case_data(case_type, case_number, filing_year)
            if not case_data:
                raise ValueError("❌ No data parsed from court portal.")

            session["case_data"] = case_data
            return redirect(url_for("result"))

        except Exception as e:
            error = f"⚠️ Error: {str(e)}"

    return render_template("form.html", case_types=case_types, error=error)

@app.route("/result")
def result():
    case_data = session.get("case_data")
    if not case_data:
        return redirect(url_for("home"))

    return render_template(
        "result.html",
        case_data=case_data,
        attribute=getattr,
        interim_orders=case_data.get("interim_orders", []),
        final_orders=case_data.get("final_orders", [])
    )

COOKIES_FILE = "session_cookies.pkl"

BASE_URL = "https://services.ecourts.gov.in"

@app.route("/view_pdf")
def view_pdf():
    viewer_url = request.args.get("url")
    if not viewer_url:
        return "No URL provided", 400

    # Ensure full URL
    viewer_url = urljoin(BASE_URL, viewer_url)

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Load cookies
    try:
        with open(COOKIES_FILE, "rb") as f:
            cookies = pickle.load(f)
        driver.get(BASE_URL)
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("✅ Cookies loaded.")
    except FileNotFoundError:
        driver.quit()
        return "No cookies found. Please fetch a case first.", 400

    # Open viewer
    driver.get(viewer_url)
    time.sleep(3)

    # Extract PDF URL
    pdf_url = None
    try:
        iframe = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        pdf_url = iframe.get_attribute("src")
    except:
        try:
            embed = driver.find_element(By.TAG_NAME, "embed")
            pdf_url = embed.get_attribute("src")
        except:
            driver.quit()
            return "Failed to locate PDF source", 500

    driver.quit()

    # Download PDF
    pdf_response = requests.get(pdf_url, stream=True)
    if pdf_response.status_code != 200:
        return "Failed to fetch PDF", 500

    return Response(
        pdf_response.content,
        mimetype="application/pdf",
        headers={"Content-Disposition": "inline; filename=order.pdf"}
    )
             
@app.route("/generate_pdf")
def generate_pdf():
    case_data = session.get("case_data")
    if not case_data:
        return redirect(url_for("home"))

    now = datetime.now().strftime("%d-%m-%Y %H:%M")

    rendered = render_template("pdf_template.html", case_data=case_data, generated_on=now)

    pdf = pdfkit.from_string(rendered, False, configuration=PDFKIT_CONFIG)

    return send_file(BytesIO(pdf),
                     download_name="Case_Summary.pdf",
                     as_attachment=True,
                     mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)
