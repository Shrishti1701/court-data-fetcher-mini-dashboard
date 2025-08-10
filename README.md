### Court Data Fetcher & Mini-Dashboard

A **Flask-based web application** that fetches live case data, orders, and judgments from the **Faridabad District Court eCourts portal**.  
It provides a searchable dashboard to view case metadata, order history, and download PDF copies of orders/judgments — even when they are embedded in JavaScript-based PDF viewers.

---

### Court Chosen
This project currently scrapes data from the **Faridabad District Court eCourts Services portal** (`https://services.ecourts.gov.in/`).  
It supports:
- Fetching case metadata (case type, filing date, status, etc.)
- Displaying **orders/judgments** in multiple categories (Interim, Final, History, etc.)
- **Downloading Result page as a PDF** 

---

## 🛠️ Setup Steps

### 1️⃣ Clone the repository
```
git clone https://github.com/<your-username>/court-data-fetcher-mini-dashboard.git
cd court-data-fetcher-mini-dashboard
```

2️⃣ Create a virtual environment
```
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

3️⃣ Install dependencies
```
pip install -r requirements.txt
```

4️⃣ Set up environment variables
Create a .env file in the project root with:
# Flask settings
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

### Selenium / ChromeDriver settings
CHROMEDRIVER_PATH=/absolute/path/to/chromedriver
SELENIUM_HEADLESS=True

Note: If you use Selenium in headless mode, ensure you have Google Chrome and the matching ChromeDriver installed.

### 🔍 CAPTCHA Strategy
The Faridabad District Court eCourts portal uses CAPTCHA challenges for human verification.
This app uses manual CAPTCHA entry:

When a search request triggers a CAPTCHA, it will be displayed in the form.

The user must manually enter the text to proceed.
(Automated CAPTCHA solving is avoided to comply with legal and ethical standards.)

🖥️ How It Works
Search Form (form.html) – Enter case details and CAPTCHA (if prompted).
Backend Scraper (scraper.py) – Uses requests + BeautifulSoup to fetch and parse court data
Results Dashboard (result.html) – Displays metadata and order/judgment links in categorized tables.

### Project Structure
court-data-fetcher/
│
├── app.py                # Flask entry point
├── scraper.py            # Main scraping & PDF proxy logic
├── models.py             # Data models / helper classes
├── templates/            # HTML templates (form, result, pdf_templates)
├── requirements.txt      # Dependencies
├── .gitignore            # Git ignore file
└── README.md             # Documentation



