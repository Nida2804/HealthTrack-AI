# HealthTrack AI – Patient Health Management System 🩺

A clean, modern healthcare web application designed for comprehensive patient health record management and AI-assisted educational health assessment. Built with **Streamlit**, **SQLite**, and the official **Google Gemini API (`google-genai`)** SDK, HealthTrack AI combines strict clinical data validation, full CRUD record workflows, and a professional blue-and-white clinical dashboard interface.

---

## 🌟 Key Features

1. **Patient Health Information Management:**
   - **Full Name**
   - **Date of Birth** (in `DD/MM/YYYY` format)
   - **Email Address**
   - **Fasting Glucose** (`mg/dL`)
   - **Haemoglobin** (`g/dL`)
   - **Total Cholesterol** (`mg/dL`)
   - **AI-Generated Remarks**

2. **Full CRUD Operations:**
   - **Add Patient:** Intuitive registration form with instant validation, duplicate checking, and automated Gemini AI health analysis.
   - **View Patients:** Interactive directory with real-time search by patient name or email, tabular view with AI remarks preview, dedicated patient inspection cards, and one-click CSV export.
   - **Edit Patient:** Pre-filled edit form with options to modify personal info or blood test metrics, and an option to regenerate AI remarks.
   - **Delete Patient:** Secure record removal with safety confirmation card and instant UI list refresh (`st.rerun()`).

3. **Strict Validation Engine:**
   - **RFC-compliant Email Validation:** Ensures valid syntax and domain structure.
   - **Calendar Date Validation:** Strictly rejects non-existent dates (e.g., February 31st or invalid leap year dates).
   - **Future Date Prevention:** Rejects any date of birth in the future.
   - **Numeric Blood Test Validation:** Accepts only positive, finite numeric values; non-numeric or negative values are rejected.
   - **Duplicate Record Prevention:** Prevents duplicate entries based on email address or identical Full Name and Date of Birth.
   - **Data Integrity:** Assessment numbers are preserved exactly as submitted without silent modifications or truncation.

4. **Persistent SQLite Storage:**
   - Self-initializing database (`healthtrack.db`) created automatically on first run.
   - Persistent storage across application restarts.
   - Indexed fields for responsive search queries.
   - Starts clean with zero placeholder/dummy records.

5. **Google Gemini AI Integration (`google-genai`):**
   - Powered by the official `google-genai` Python library.
   - Reads the API key strictly from the `GEMINI_API_KEY` environment variable (never hardcoded).
   - Generates cautious, educational observations based on standard clinical reference ranges.
   - Strict safety instructions prevent disease diagnosis claims.
   - Mandatory medical disclaimer appended to all evaluations.
   - **Graceful Fallback:** If the API key is not configured or an API error occurs, the app seamlessly provides educational reference interval analysis without interrupting the user.

6. **Modern Blue-and-White Healthcare Dashboard:**
   - Hospital-grade aesthetic with crisp blues (`#0D47A1`, `#1976D2`, `#0288D1`), white cards, and soft gray borders.
   - Summary statistics cards: Total Patients, Average Glucose, Average Haemoglobin, and Average Cholesterol.
   - AI engine connectivity status indicator.

---

## 📁 Project Structure

```
HealthTrack-AI/
├── app.py              # Main Streamlit user interface and dashboard
├── database.py         # SQLite persistent storage, schema initialization & CRUD functions
├── validation.py       # Comprehensive validation for patient data and blood metrics
├── ai_service.py       # Google Gemini API integration (google-genai) & educational fallback
├── requirements.txt    # Project dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git exclusion rules (venv, .env, *.db, cache)
└── README.md           # Documentation and setup instructions
```

---

## 🛠️ Technology Stack

- **Backend Logic:** Python 3.10+
- **User Interface:** Streamlit (v1.35+)
- **Database:** SQLite 3 (built-in persistent relational storage)
- **AI Engine:** Google Gemini API via official `google-genai` SDK
- **Environment Management:** `python-dotenv`
- **Data Handling:** `pandas`

---

## 🚀 Installation & Setup

### 1. Clone or Navigate to the Repository
```bash
cd HealthTrack-AI
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your Google Gemini API Key

1. Copy `.env.example` to create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   *(On Windows PowerShell: `Copy-Item .env.example .env`)*

2. Open `.env` and insert your Gemini API Key obtained from [Google AI Studio](https://aistudio.google.com/):
   ```env
   GEMINI_API_KEY=AIzaSyYourActualGeminiApiKeyHere
   ```

> **Note:** If `GEMINI_API_KEY` is not set in `.env`, HealthTrack AI will run in **Clinical Educational Reference Mode** and also allows entering an API key directly in the application sidebar for the active session.

---

## 🏃 Running the Application

Launch the Streamlit web server:

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at:
```
http://localhost:8501
```

---

## 📋 Usage Guide

### 1. Register a Patient
- Navigate to the **➕ Add Patient** tab.
- Enter the patient's legal Full Name, Email, and select/type their Date of Birth in `DD/MM/YYYY` format.
- Input the laboratory assessment values:
  - Fasting Glucose (Standard normal: 70 – 99 mg/dL)
  - Haemoglobin (Standard adult: 12.0 – 17.5 g/dL)
  - Total Cholesterol (Desirable: < 200 mg/dL)
- Click **"Save Patient Record & Generate AI Remarks"**.
- HealthTrack AI validates the inputs, checks for duplicates, calls Gemini AI, and saves the record.

### 2. View & Search Directory
- Navigate to the **📋 View Patients** tab.
- Search records dynamically by patient name or email.
- Review the interactive table showing IDs, personal info, blood metrics, and remarks preview.
- Use the **Patient Health Profile & AI Remarks Inspector** to examine an individual patient's metrics cards and full AI assessment.
- Click **"Export Patient Records (CSV)"** to download the dataset.

### 3. Edit Patient Records
- Navigate to the **✏️ Edit Patient** tab.
- Select a patient from the dropdown list.
- Modify the personal details or test metrics.
- Keep **"Regenerate AI remarks with updated assessment values"** checked to update the AI analysis.
- Click **"Update Patient Record"**.

### 4. Delete Patient Records
- Navigate to the **🗑️ Delete Patient** tab.
- Select the patient record you wish to remove.
- Review the summary confirmation card.
- Check the confirmation box and click **"Permanently Delete Record"**.
- The record is purged from SQLite and the dashboard refreshes automatically.

---

## ⚠️ Medical Disclaimer

HealthTrack AI and its underlying AI models are designed exclusively for **educational, administrative, and informational purposes**. 

- The AI remarks generated **do not constitute a medical diagnosis, clinical judgment, prognosis, or treatment plan**.
- The system does not claim to diagnose diseases or replace licensed healthcare practitioners.
- Users and patients must always consult a qualified medical doctor or healthcare provider for interpretation of blood test results and personalized clinical guidance.

---

## 📄 License
This project is developed for educational and healthcare management demonstration purposes.

