# Court Data Fetcher & Mini-Dashboard

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/github/license/Shrishti1701/court-data-fetcher-mini-dashboard)
![Repo Size](https://img.shields.io/github/repo-size/Shrishti1701/court-data-fetcher-mini-dashboard)

A **Flask-based web application** that fetches live case data, orders, and judgments from the **Faridabad District Court eCourts portal**.  
It provides a searchable dashboard to view case metadata, order history, and download PDF copies of orders/judgments — even when they are embedded in JavaScript-based PDF viewers.

---

## 📍 Court Chosen
This project currently scrapes data from the **Faridabad District Court eCourts Services portal** (`https://services.ecourts.gov.in/`).  

It supports:
- Fetching case metadata (case type, filing date, status, etc.)
- Displaying **orders/judgments** in multiple categories (Interim, Final, History, etc.)
- **Downloading result page as a PDF**

---

## 📂 Project Structure
```
court-data-fetcher/
│
├── app.py                # Flask entry point
├── scraper.py            # Main scraping & PDF proxy logic
├── models.py             # Data models / helper classes
├── templates/            # HTML templates (form, result, pdf_templates)
├── requirements.txt      # Dependencies
├── .gitignore            # Git ignore file
└── README.md             # Documentation
```

---

## ⚙️ Setup Steps

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/court-data-fetcher-mini-dashboard.git
cd court-data-fetcher-mini-dashboard
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Flask app
```bash
python app.py
```

### 5️⃣ Access in browser
```
http://127.0.0.1:5000
```

---

## 🛠️ Environment Variables
Create a `.env` file in the project root with:

```env
# Flask settings
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Selenium / ChromeDriver settings
CHROMEDRIVER_PATH=/absolute/path/to/chromedriver
SELENIUM_HEADLESS=True
```

**Note:**  
If using Selenium in headless mode, ensure you have Google Chrome and the matching ChromeDriver installed.

---

## 🔍 CAPTCHA Strategy
The Faridabad District Court eCourts portal uses CAPTCHA challenges for human verification.  
This app uses **manual CAPTCHA entry**:

- When a search request triggers a CAPTCHA, it will be displayed in the form.
- The user must manually enter the text to proceed.
- Automated CAPTCHA solving is **avoided** to comply with legal and ethical standards.

---

## 🖥️ How It Works
1. **Search Form (`form.html`)** – Enter case details and CAPTCHA (if prompted).
2. **Backend Scraper (`scraper.py`)** – Uses `requests` + `BeautifulSoup` to fetch and parse court data.
3. **Results Dashboard (`result.html`)** – Displays metadata and order/judgment links in categorized tables.

---

## ⚠️ Important – Selenium Step
1. When you perform a search, Selenium will open a browser window to load the court case details.
2. Wait until the case data is **fully loaded** in the Selenium window.
3. Return to the terminal and press **Enter** — this will trigger the script to parse the loaded data and redirect you to the results page where the dashboard is generated.

---

## 📸 Screenshots

**Example Case 1:**
- Case Type: CS - Civil Suit
- Case Number: 121
- Filing Year: 2021

**Example Case 2:**
- Case Type: CA - Civil Appeal
- Case Number: 121
- Filing Year: 2021

<img width="919" height="834" alt="image" src="https://github.com/user-attachments/assets/8e10b960-a161-4c47-8d92-88973bdf59d6" />  
<img width="843" height="875" alt="image" src="https://github.com/user-attachments/assets/f495e681-3228-4074-822e-57301863a1c1" />  
<img width="837" height="805" alt="image" src="https://github.com/user-attachments/assets/3e3aaa9b-3de5-4ad4-ab51-591b9effd3b5" />  
<img width="738" height="797" alt="image" src="https://github.com/user-attachments/assets/0ec2e197-dd25-47fe-b5da-1a0ceb2e08ce" />  

---

## 📜 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🐍 Requirements
- Python **3.9+**
- Google Chrome & ChromeDriver
- Flask
- BeautifulSoup4
- Requests
- Selenium
