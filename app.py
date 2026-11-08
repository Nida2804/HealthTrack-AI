"""
HealthTrack AI – Patient Health Management System
Main Streamlit Application

A clean, modern healthcare dashboard with blue-and-white theme, SQLite persistent storage,
strict data validation, full CRUD operations, and Google Gemini AI health assessment.
"""

import calendar
import os
from datetime import date, datetime
import pandas as pd
import streamlit as st

# Local modules
import ai_service
import database
import validation

# Month choices (January - December) and Year range (1960 through 2030, inclusive)
MONTH_OPTIONS = [
    (1, "January"),
    (2, "February"),
    (3, "March"),
    (4, "April"),
    (5, "May"),
    (6, "June"),
    (7, "July"),
    (8, "August"),
    (9, "September"),
    (10, "October"),
    (11, "November"),
    (12, "December"),
]
YEAR_OPTIONS = list(range(1960, 2031))  # 1960 through 2030, inclusive

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="HealthTrack AI – Patient Health Management System",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database on app startup
database.init_db()


# -----------------------------------------------------------------------------
# Custom Blue & White Healthcare Theme CSS
# -----------------------------------------------------------------------------
def apply_healthcare_theme():
    st.markdown(
        """
        <style>
        /* Base page font and background accents */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Top Hero Header */
        .healthtrack-hero {
            background: linear-gradient(135deg, #0d47a1 0%, #1976d2 50%, #0288d1 100%);
            color: #ffffff;
            padding: 1.8rem 2.2rem;
            border-radius: 14px;
            margin-bottom: 1.8rem;
            box-shadow: 0 4px 16px rgba(13, 71, 161, 0.15);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .healthtrack-hero h1 {
            color: #ffffff;
            font-size: 1.9rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .healthtrack-hero p {
            color: #e3f2fd;
            font-size: 0.95rem;
            margin-top: 0.35rem;
            margin-bottom: 0;
        }

        /* Metric Cards */
        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-top: 4px solid #1976d2;
            border-radius: 10px;
            padding: 1.1rem 1.2rem;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 14px rgba(25, 118, 210, 0.1);
        }
        .metric-title {
            color: #64748b;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-bottom: 0.3rem;
        }
        .metric-value {
            color: #0f172a;
            font-size: 1.7rem;
            font-weight: 700;
            line-height: 1.2;
        }
        .metric-subtitle {
            color: #94a3b8;
            font-size: 0.78rem;
            margin-top: 0.2rem;
        }

        /* Disclaimer Box */
        .disclaimer-box {
            background: #eff6ff;
            border-left: 4px solid #2563eb;
            padding: 0.85rem 1.1rem;
            border-radius: 6px;
            margin: 1rem 0;
            color: #1e3a8a;
            font-size: 0.86rem;
            line-height: 1.45;
        }

        /* AI Remarks Container */
        .ai-remarks-container {
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 1.2rem;
            margin-top: 0.75rem;
            color: #1e293b;
        }

        /* Status Pills */
        .status-pill {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .status-pill-green {
            background: #dcfce7;
            color: #166534;
            border: 1px solid #bbf7d0;
        }
        .status-pill-blue {
            background: #dbeafe;
            color: #1e40af;
            border: 1px solid #bfdbfe;
        }
        .status-pill-amber {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
        }

        /* Streamlit Button Tweaks */
        .stButton button[kind="primary"] {
            background-color: #1976d2 !important;
            border-color: #1976d2 !important;
            color: #ffffff !important;
            font-weight: 600;
            border-radius: 6px;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #1565c0 !important;
            border-color: #1565c0 !important;
        }

        /* Tab headers */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            border-bottom: 2px solid #e2e8f0;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 18px;
            font-weight: 600;
            color: #475569;
        }
        .stTabs [aria-selected="true"] {
            color: #1976d2 !important;
            border-bottom: 2px solid #1976d2 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_healthcare_theme()


# -----------------------------------------------------------------------------
# Sidebar: Engine Status & Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🩺 HealthTrack AI")
    st.caption("Patient Health Management System")
    st.markdown("---")

    # Session-level API Key override (optional runtime configuration)
    if "api_key_override" not in st.session_state:
        st.session_state["api_key_override"] = ""

    env_has_key = bool(os.getenv("GEMINI_API_KEY", "").strip())
    active_key = (
        st.session_state["api_key_override"].strip()
        if st.session_state["api_key_override"].strip()
        else os.getenv("GEMINI_API_KEY", "").strip()
    )

    st.markdown("#### 🤖 AI Engine Status")
    if active_key:
        st.markdown(
            '<span class="status-pill status-pill-green">🟢 Google Gemini Active</span>',
            unsafe_allow_html=True,
        )
        st.caption("Using official `google-genai` SDK for health remarks.")
    else:
        st.markdown(
            '<span class="status-pill status-pill-amber">🟡 Reference Mode (Key Not Set)</span>',
            unsafe_allow_html=True,
        )
        st.caption("Using baseline clinical educational reference intervals.")

    with st.expander("🔑 Configure Gemini API Key", expanded=not env_has_key):
        st.markdown(
            "<small>You can set <code>GEMINI_API_KEY</code> in a <code>.env</code> file or provide it here for this session.</small>",
            unsafe_allow_html=True,
        )
        user_key_input = st.text_input(
            "Gemini API Key",
            value=st.session_state["api_key_override"],
            type="password",
            placeholder="AIzaSy...",
            help="Read from GEMINI_API_KEY environment variable. Never hardcoded.",
        )
        if user_key_input != st.session_state["api_key_override"]:
            st.session_state["api_key_override"] = user_key_input
            st.rerun()

    st.markdown("---")

    # Quick summary in sidebar
    stats = database.get_patient_stats()
    st.markdown("#### 📊 Quick Overview")
    st.write(f"**Total Records:** {stats['total_patients']}")
    st.write(f"**Database:** SQLite (`healthtrack.db`)")
    st.write(f"**System Date:** {date.today().strftime('%d/%m/%Y')}")

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.75rem; color:#64748b; line-height:1.4;">
        <strong>Safety Note:</strong><br>
        HealthTrack AI provides educational summaries only. It does not replace clinical consultation, diagnosis, or treatment.
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Top Hero Banner
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="healthtrack-hero">
        <div>
            <h1>HealthTrack AI – Patient Health Management System</h1>
            <p>Clinical Record Management & AI-Powered Educational Health Analysis</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Mandatory Clinical Disclaimer Banner
st.markdown(
    """
    <div class="disclaimer-box">
        <strong>⚠️ Clinical & Medical Disclaimer:</strong>
        All remarks and observations generated by HealthTrack AI are intended solely for cautious educational
        and informational guidance. They <strong>do not constitute a medical diagnosis</strong>, treatment plan,
        or professional clinical opinion. Always seek the advice of a licensed physician or qualified healthcare
        provider with any questions regarding lab values or health conditions.
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Metric Summary Cards
# -----------------------------------------------------------------------------
stats = database.get_patient_stats()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Total Patients</div>
            <div class="metric-value">{stats['total_patients']}</div>
            <div class="metric-subtitle">Registered in database</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Avg Glucose</div>
            <div class="metric-value">{stats['avg_glucose']} <span style="font-size:0.9rem; font-weight:normal; color:#64748b;">mg/dL</span></div>
            <div class="metric-subtitle">Ref: 70–99 mg/dL</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Avg Haemoglobin</div>
            <div class="metric-value">{stats['avg_haemoglobin']} <span style="font-size:0.9rem; font-weight:normal; color:#64748b;">g/dL</span></div>
            <div class="metric-subtitle">Ref: 12.0–17.5 g/dL</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Avg Cholesterol</div>
            <div class="metric-value">{stats['avg_cholesterol']} <span style="font-size:0.9rem; font-weight:normal; color:#64748b;">mg/dL</span></div>
            <div class="metric-subtitle">Target: &lt;200 mg/dL</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Main Application Navigation Tabs
# -----------------------------------------------------------------------------
tab_view, tab_add, tab_edit, tab_delete = st.tabs(
    [
        "📋 View Patients",
        "➕ Add Patient",
        "✏️ Edit Patient",
        "🗑️ Delete Patient",
    ]
)


# =============================================================================
# TAB 1: VIEW PATIENTS
# =============================================================================
with tab_view:
    st.subheader("Patient Records Directory")

    search_col, count_col = st.columns([3, 1])
    with search_col:
        search_query = st.text_input(
            "Search Patients",
            placeholder="Search by full name or email address...",
            label_visibility="collapsed",
        )
    with count_col:
        patients_list = database.get_all_patients(search_query=search_query)
        st.write(f"**Found:** {len(patients_list)} record(s)")

    if not patients_list:
        if search_query:
            st.info(f"No patient records matched '{search_query}'. Try another search query.")
        else:
            st.info(
                "No patient records currently exist in the database. "
                "Switch to the **'Add Patient'** tab to create your first record."
            )
    else:
        # Build pandas DataFrame for display
        df_display = pd.DataFrame(
            [
                {
                    "ID": p["id"],
                    "Full Name": p["full_name"],
                    "Date of Birth": p["date_of_birth"],
                    "Email Address": p["email"],
                    "Glucose (mg/dL)": p["glucose"],
                    "Haemoglobin (g/dL)": p["haemoglobin"],
                    "Cholesterol (mg/dL)": p["cholesterol"],
                    "AI Remarks": p["ai_remarks"] or "N/A",
                    "Created At": p["created_at"],
                }
                for p in patients_list
            ]
        )

        # Table Display
        st.dataframe(
            df_display[
                [
                    "ID",
                    "Full Name",
                    "Date of Birth",
                    "Email Address",
                    "Glucose (mg/dL)",
                    "Haemoglobin (g/dL)",
                    "Cholesterol (mg/dL)",
                    "AI Remarks",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Full Name": st.column_config.TextColumn("Full Name", width="medium"),
                "Date of Birth": st.column_config.TextColumn("Date of Birth", width="small"),
                "Email Address": st.column_config.TextColumn("Email Address", width="medium"),
                "Glucose (mg/dL)": st.column_config.NumberColumn("Glucose (mg/dL)", format="%.1f"),
                "Haemoglobin (g/dL)": st.column_config.NumberColumn("Haemoglobin (g/dL)", format="%.1f"),
                "Cholesterol (mg/dL)": st.column_config.NumberColumn("Cholesterol (mg/dL)", format="%.1f"),
                "AI Remarks": st.column_config.TextColumn("AI Remarks", width="large"),
            },
        )

        # Export CSV Button
        csv_data = df_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Patient Records (CSV)",
            data=csv_data,
            file_name=f"healthtrack_patients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

        st.markdown("---")

        # Detailed Patient Inspection Card
        st.markdown("#### 🔍 Patient Health Profile & AI Remarks Inspector")
        patient_options = {
            f"ID #{p['id']} – {p['full_name']} ({p['email']})": p["id"]
            for p in patients_list
        }
        selected_label = st.selectbox(
            "Select a patient to inspect detailed records and AI remarks:",
            options=list(patient_options.keys()),
        )

        if selected_label:
            selected_id = patient_options[selected_label]
            patient_detail = database.get_patient_by_id(selected_id)

            if patient_detail:
                p_col1, p_col2, p_col3 = st.columns(3)
                with p_col1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">Blood Glucose</div>
                            <div class="metric-value">{patient_detail['glucose']} <span style="font-size:0.85rem; font-weight:normal;">mg/dL</span></div>
                            <div class="metric-subtitle">Standard: 70–99 mg/dL</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with p_col2:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">Haemoglobin</div>
                            <div class="metric-value">{patient_detail['haemoglobin']} <span style="font-size:0.85rem; font-weight:normal;">g/dL</span></div>
                            <div class="metric-subtitle">Standard: 12.0–17.5 g/dL</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with p_col3:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">Total Cholesterol</div>
                            <div class="metric-value">{patient_detail['cholesterol']} <span style="font-size:0.85rem; font-weight:normal;">mg/dL</span></div>
                            <div class="metric-subtitle">Target: &lt;200 mg/dL</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:1rem; margin-bottom:1rem;">
                        <strong>Patient:</strong> {patient_detail['full_name']} &nbsp;|&nbsp;
                        <strong>DOB:</strong> {patient_detail['date_of_birth']} &nbsp;|&nbsp;
                        <strong>Email:</strong> {patient_detail['email']} &nbsp;|&nbsp;
                        <strong>Registered:</strong> {patient_detail['created_at']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("##### 🤖 Generated Health Remarks")
                if patient_detail["ai_remarks"]:
                    st.markdown(
                        f"""
                        <div class="ai-remarks-container">
                            {patient_detail['ai_remarks']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("No AI remarks recorded for this patient.")


# =============================================================================
# TAB 2: ADD PATIENT
# =============================================================================
with tab_add:
    st.subheader("Register New Patient Record")
    st.caption(
        "Fill in the patient's personal details and laboratory assessment values. "
        "AI remarks will be generated and stored automatically."
    )

    with st.form("add_patient_form", clear_on_submit=False):
        f_col1, f_col2 = st.columns(2)

        with f_col1:
            add_full_name = st.text_input(
                "Full Name *",
                placeholder="e.g. Eleanor Vance",
                help="Patient's legal full name.",
            )
            add_email = st.text_input(
                "Email Address *",
                placeholder="e.g. eleanor.vance@example.com",
                help="Must be a valid email address.",
            )

        with f_col2:
            st.markdown(
                '<label style="font-size: 14px; font-weight: 500; color: #334155; margin-bottom: 4px; display: block;">'
                'Date of Birth (DD/MM/YYYY) *'
                '</label>',
                unsafe_allow_html=True,
            )
            d_col, m_col, y_col = st.columns([1, 1.4, 1.2])

            # Determine dynamic day range based on currently selected month and year
            add_m_curr = st.session_state.get("add_dob_month", 1)
            add_y_curr = st.session_state.get("add_dob_year", 1990)
            add_max_days = calendar.monthrange(add_y_curr, add_m_curr)[1]
            add_day_options = list(range(1, add_max_days + 1))

            with d_col:
                add_day = st.selectbox(
                    "Day",
                    options=add_day_options,
                    index=0,
                    key="add_dob_day",
                    help="Day of birth (1–31, adjusted for month/year)",
                )
            with m_col:
                add_month = st.selectbox(
                    "Month",
                    options=[m[0] for m in MONTH_OPTIONS],
                    format_func=lambda m: MONTH_OPTIONS[m - 1][1],
                    index=0,
                    key="add_dob_month",
                    help="Month of birth (January–December)",
                )
            with y_col:
                add_year = st.selectbox(
                    "Year",
                    options=YEAR_OPTIONS,
                    index=YEAR_OPTIONS.index(1990),
                    key="add_dob_year",
                    help="Year of birth (1960–2030 inclusive)",
                )

            # Combine selected values into a valid Python datetime.date object
            max_days_for_selected = calendar.monthrange(add_year, add_month)[1]
            valid_add_day = min(add_day, max_days_for_selected)
            add_dob = date(add_year, add_month, valid_add_day)
            st.caption(f"Selected DOB: **{add_dob.strftime('%d/%m/%Y')}**")

        st.markdown("#### Clinical Assessment Values")
        b_col1, b_col2, b_col3 = st.columns(3)

        with b_col1:
            add_glucose = st.number_input(
                "Fasting Glucose (mg/dL) *",
                min_value=10.0,
                max_value=1500.0,
                value=95.0,
                step=0.5,
                format="%.1f",
                help="Standard normal fasting: 70 – 99 mg/dL.",
            )

        with b_col2:
            add_haemoglobin = st.number_input(
                "Haemoglobin (g/dL) *",
                min_value=1.0,
                max_value=35.0,
                value=14.0,
                step=0.1,
                format="%.1f",
                help="Standard adult reference: 12.0 – 17.5 g/dL.",
            )

        with b_col3:
            add_cholesterol = st.number_input(
                "Total Cholesterol (mg/dL) *",
                min_value=20.0,
                max_value=1500.0,
                value=180.0,
                step=1.0,
                format="%.1f",
                help="Desirable level: < 200 mg/dL.",
            )

        submitted_add = st.form_submit_button(
            "🩺 Save Patient Record & Generate AI Remarks",
            use_container_width=True,
            type="primary",
        )

    if submitted_add:
        # Validate inputs
        is_valid, validation_errors, validated_data = validation.validate_patient_record(
            full_name=add_full_name,
            date_of_birth=add_dob,
            email=add_email,
            glucose=add_glucose,
            haemoglobin=add_haemoglobin,
            cholesterol=add_cholesterol,
            exclude_patient_id=None,
            db_check=True,
        )

        if not is_valid:
            st.error("### ❌ Please correct the following validation errors:")
            for err in validation_errors:
                st.markdown(f"- {err}")
        else:
            with st.spinner("Analyzing blood metrics and generating AI remarks with Gemini..."):
                active_key = (
                    st.session_state.get("api_key_override", "").strip()
                    or os.getenv("GEMINI_API_KEY", "").strip()
                )
                ai_remarks = ai_service.generate_health_remarks(
                    full_name=validated_data["full_name"],
                    date_of_birth=validated_data["date_of_birth"],
                    glucose=validated_data["glucose"],
                    haemoglobin=validated_data["haemoglobin"],
                    cholesterol=validated_data["cholesterol"],
                    api_key_override=active_key,
                )

                new_id = database.add_patient(
                    full_name=validated_data["full_name"],
                    date_of_birth=validated_data["date_of_birth"],
                    email=validated_data["email"],
                    glucose=validated_data["glucose"],
                    haemoglobin=validated_data["haemoglobin"],
                    cholesterol=validated_data["cholesterol"],
                    ai_remarks=ai_remarks,
                )

            st.success(
                f"✅ Successfully registered patient **{validated_data['full_name']}** (ID #{new_id})!"
            )
            with st.expander("📄 View Generated AI Remarks", expanded=True):
                st.markdown(ai_remarks)


# =============================================================================
# TAB 3: EDIT PATIENT
# =============================================================================
with tab_edit:
    st.subheader("Edit Patient Record")
    st.caption("Select a patient record to update their details or blood test values.")

    all_patients_edit = database.get_all_patients()
    if not all_patients_edit:
        st.info("No patient records available to edit.")
    else:
        edit_options = {
            f"ID #{p['id']} – {p['full_name']} ({p['email']})": p["id"]
            for p in all_patients_edit
        }
        edit_selected_label = st.selectbox(
            "Select patient to edit:",
            options=list(edit_options.keys()),
            key="edit_patient_selector",
        )

        selected_edit_id = edit_options[edit_selected_label]
        target_patient = database.get_patient_by_id(selected_edit_id)

        if target_patient:
            # Parse existing DOB for prepopulating the three dropdowns
            try:
                curr_dob = datetime.strptime(
                    target_patient["date_of_birth"], "%d/%m/%Y"
                ).date()
                curr_day = curr_dob.day
                curr_month = curr_dob.month
                curr_year = curr_dob.year
            except Exception:
                curr_day = 1
                curr_month = 1
                curr_year = 1990

            edit_years = YEAR_OPTIONS.copy()
            if curr_year not in edit_years:
                edit_years = sorted(edit_years + [curr_year])

            with st.form(f"edit_patient_form_{selected_edit_id}"):
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    edit_name = st.text_input(
                        "Full Name *",
                        value=target_patient["full_name"],
                    )
                    edit_email = st.text_input(
                        "Email Address *",
                        value=target_patient["email"],
                    )
                with e_col2:
                    st.markdown(
                        '<label style="font-size: 14px; font-weight: 500; color: #334155; margin-bottom: 4px; display: block;">'
                        'Date of Birth (DD/MM/YYYY) *'
                        '</label>',
                        unsafe_allow_html=True,
                    )
                    ed_col, em_col, ey_col = st.columns([1, 1.4, 1.2])

                    # Determine day options based on patient's month and year
                    edit_m_curr = st.session_state.get(f"edit_dob_month_{selected_edit_id}", curr_month)
                    edit_y_curr = st.session_state.get(f"edit_dob_year_{selected_edit_id}", curr_year)
                    edit_max_days = calendar.monthrange(edit_y_curr, edit_m_curr)[1]
                    edit_day_options = list(range(1, edit_max_days + 1))
                    day_idx = min(curr_day - 1, len(edit_day_options) - 1) if curr_day >= 1 else 0

                    with ed_col:
                        edit_day = st.selectbox(
                            "Day",
                            options=edit_day_options,
                            index=day_idx,
                            key=f"edit_dob_day_{selected_edit_id}",
                            help="Day of birth",
                        )
                    with em_col:
                        edit_month = st.selectbox(
                            "Month",
                            options=[m[0] for m in MONTH_OPTIONS],
                            format_func=lambda m: MONTH_OPTIONS[m - 1][1],
                            index=curr_month - 1 if 1 <= curr_month <= 12 else 0,
                            key=f"edit_dob_month_{selected_edit_id}",
                            help="Month of birth",
                        )
                    with ey_col:
                        edit_year = st.selectbox(
                            "Year",
                            options=edit_years,
                            index=edit_years.index(curr_year),
                            key=f"edit_dob_year_{selected_edit_id}",
                            help="Year of birth (1960–2030 inclusive)",
                        )

                    # Combine selected values into a valid Python datetime.date object
                    max_days_edit_selected = calendar.monthrange(edit_year, edit_month)[1]
                    valid_edit_day = min(edit_day, max_days_edit_selected)
                    edit_dob = date(edit_year, edit_month, valid_edit_day)
                    st.caption(f"Current / Selected DOB: **{edit_dob.strftime('%d/%m/%Y')}**")

                st.markdown("#### Clinical Assessment Values")
                eb_col1, eb_col2, eb_col3 = st.columns(3)
                with eb_col1:
                    edit_glucose = st.number_input(
                        "Fasting Glucose (mg/dL) *",
                        min_value=10.0,
                        max_value=1500.0,
                        value=float(target_patient["glucose"]),
                        step=0.5,
                        format="%.1f",
                    )
                with eb_col2:
                    edit_haemoglobin = st.number_input(
                        "Haemoglobin (g/dL) *",
                        min_value=1.0,
                        max_value=35.0,
                        value=float(target_patient["haemoglobin"]),
                        step=0.1,
                        format="%.1f",
                    )
                with eb_col3:
                    edit_cholesterol = st.number_input(
                        "Total Cholesterol (mg/dL) *",
                        min_value=20.0,
                        max_value=1500.0,
                        value=float(target_patient["cholesterol"]),
                        step=1.0,
                        format="%.1f",
                    )

                regenerate_ai = st.checkbox(
                    "Regenerate AI remarks with updated assessment values",
                    value=True,
                    help="Calls Gemini AI to analyze the updated laboratory values.",
                )

                submitted_edit = st.form_submit_button(
                    "💾 Update Patient Record",
                    use_container_width=True,
                    type="primary",
                )

            if submitted_edit:
                is_valid, edit_errors, validated_edit = validation.validate_patient_record(
                    full_name=edit_name,
                    date_of_birth=edit_dob,
                    email=edit_email,
                    glucose=edit_glucose,
                    haemoglobin=edit_haemoglobin,
                    cholesterol=edit_cholesterol,
                    exclude_patient_id=selected_edit_id,
                    db_check=True,
                )

                if not is_valid:
                    st.error("### ❌ Please correct the following validation errors:")
                    for err in edit_errors:
                        st.markdown(f"- {err}")
                else:
                    new_remarks = target_patient["ai_remarks"]
                    if regenerate_ai:
                        with st.spinner("Regenerating AI health assessment..."):
                            active_key = (
                                st.session_state.get("api_key_override", "").strip()
                                or os.getenv("GEMINI_API_KEY", "").strip()
                            )
                            new_remarks = ai_service.generate_health_remarks(
                                full_name=validated_edit["full_name"],
                                date_of_birth=validated_edit["date_of_birth"],
                                glucose=validated_edit["glucose"],
                                haemoglobin=validated_edit["haemoglobin"],
                                cholesterol=validated_edit["cholesterol"],
                                api_key_override=active_key,
                            )

                    success = database.update_patient(
                        patient_id=selected_edit_id,
                        full_name=validated_edit["full_name"],
                        date_of_birth=validated_edit["date_of_birth"],
                        email=validated_edit["email"],
                        glucose=validated_edit["glucose"],
                        haemoglobin=validated_edit["haemoglobin"],
                        cholesterol=validated_edit["cholesterol"],
                        ai_remarks=new_remarks,
                    )

                    if success:
                        st.success(
                            f"✅ Record for **{validated_edit['full_name']}** (ID #{selected_edit_id}) updated successfully!"
                        )
                        st.rerun()
                    else:
                        st.error("Failed to update patient record in the database.")


# =============================================================================
# TAB 4: DELETE PATIENT
# =============================================================================
with tab_delete:
    st.subheader("Delete Patient Record")
    st.caption("Permanently remove a patient record from the SQLite database.")

    all_patients_del = database.get_all_patients()
    if not all_patients_del:
        st.info("No patient records available to delete.")
    else:
        del_options = {
            f"ID #{p['id']} – {p['full_name']} ({p['email']})": p["id"]
            for p in all_patients_del
        }
        del_selected_label = st.selectbox(
            "Select patient record to delete:",
            options=list(del_options.keys()),
            key="delete_patient_selector",
        )

        selected_del_id = del_options[del_selected_label]
        target_del = database.get_patient_by_id(selected_del_id)

        if target_del:
            st.markdown(
                f"""
                <div style="background:#fff1f2; border:1px solid #fecdd3; border-radius:8px; padding:1.2rem; margin:1rem 0;">
                    <h4 style="color:#be123c; margin-top:0;">⚠️ Warning: Permanent Record Deletion</h4>
                    <p style="color:#4c0519; margin-bottom:0.5rem;">
                        You are about to permanently delete the following patient record:
                    </p>
                    <ul style="color:#4c0519; font-size:0.92rem;">
                        <li><strong>Patient ID:</strong> #{target_del['id']}</li>
                        <li><strong>Full Name:</strong> {target_del['full_name']}</li>
                        <li><strong>Date of Birth:</strong> {target_del['date_of_birth']}</li>
                        <li><strong>Email:</strong> {target_del['email']}</li>
                        <li><strong>Glucose:</strong> {target_del['glucose']} mg/dL</li>
                        <li><strong>Haemoglobin:</strong> {target_del['haemoglobin']} g/dL</li>
                        <li><strong>Cholesterol:</strong> {target_del['cholesterol']} mg/dL</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

            confirm_check = st.checkbox(
                f"I confirm that I want to delete record #{target_del['id']} ({target_del['full_name']}).",
                key="confirm_delete_checkbox",
            )

            if st.button("🗑️ Permanently Delete Record", type="primary", disabled=not confirm_check):
                deleted = database.delete_patient(selected_del_id)
                if deleted:
                    st.success(
                        f"✅ Patient record #{selected_del_id} ({target_del['full_name']}) was successfully deleted."
                    )
                    st.rerun()
                else:
                    st.error("Failed to delete record from database.")

