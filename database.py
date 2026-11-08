"""
Database module for HealthTrack AI – Patient Health Management System.
Handles persistent SQLite storage, table initialization, and CRUD operations.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Tuple

# Default database filename
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "healthtrack.db")


@contextmanager
def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that yields an active SQLite connection with Row factory,
    commits changes, and guarantees proper connection closing to prevent WinError file locks.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Automatically create the SQLite database and patients table if they do not exist.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT NOT NULL,
                glucose REAL NOT NULL,
                haemoglobin REAL NOT NULL,
                cholesterol REAL NOT NULL,
                ai_remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Create an index on email and name for optimized searches
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_patients_email ON patients (email)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_patients_name ON patients (full_name)"
        )


def check_duplicate_patient(
    email: str,
    full_name: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    exclude_id: Optional[int] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> Tuple[bool, str]:
    """
    Check if a patient record with the same email or identical (full_name, date_of_birth)
    already exists in the database.
    exclude_id is used during edit operations to ignore the current record.
    
    Returns:
        Tuple[bool, str]: (is_duplicate, explanation_message)
    """
    init_db(db_path)
    norm_email = email.strip().lower()
    norm_name = full_name.strip().lower() if full_name else None
    norm_dob = date_of_birth.strip() if date_of_birth else None

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # Check for duplicate email
        if exclude_id is not None:
            cursor.execute(
                "SELECT id, full_name, email FROM patients WHERE LOWER(email) = ? AND id != ?",
                (norm_email, exclude_id),
            )
        else:
            cursor.execute(
                "SELECT id, full_name, email FROM patients WHERE LOWER(email) = ?",
                (norm_email,),
            )
        row = cursor.fetchone()
        if row:
            return (
                True,
                f"A patient record with the email '{email}' already exists (ID #{row['id']}: {row['full_name']}).",
            )

        # Check for duplicate Full Name + Date of Birth combination
        if norm_name and norm_dob:
            if exclude_id is not None:
                cursor.execute(
                    """
                    SELECT id, full_name, email, date_of_birth 
                    FROM patients 
                    WHERE LOWER(full_name) = ? AND date_of_birth = ? AND id != ?
                    """,
                    (norm_name, norm_dob, exclude_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, full_name, email, date_of_birth 
                    FROM patients 
                    WHERE LOWER(full_name) = ? AND date_of_birth = ?
                    """,
                    (norm_name, norm_dob),
                )
            row_identity = cursor.fetchone()
            if row_identity:
                return (
                    True,
                    f"A patient record for '{full_name}' born on '{date_of_birth}' already exists (ID #{row_identity['id']}).",
                )

    return False, ""


def add_patient(
    full_name: str,
    date_of_birth: str,
    email: str,
    glucose: float,
    haemoglobin: float,
    cholesterol: float,
    ai_remarks: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    """
    Add a new patient record into the SQLite database.
    Returns the newly generated patient ID.
    """
    init_db(db_path)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO patients (
                full_name, date_of_birth, email, glucose, haemoglobin, cholesterol, ai_remarks, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                full_name.strip(),
                date_of_birth.strip(),
                email.strip(),
                float(glucose),
                float(haemoglobin),
                float(cholesterol),
                ai_remarks,
                now_str,
                now_str,
            ),
        )
        return cursor.lastrowid


def get_all_patients(
    search_query: Optional[str] = None, db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """
    Retrieve all patient records from the database, ordered by patient ID ascending.
    Optionally filter by name or email with search_query.
    """
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if search_query and search_query.strip():
            query = f"%{search_query.strip().lower()}%"
            cursor.execute(
                """
                SELECT id, full_name, date_of_birth, email, glucose, haemoglobin, cholesterol, ai_remarks, created_at, updated_at
                FROM patients
                WHERE LOWER(full_name) LIKE ? OR LOWER(email) LIKE ?
                ORDER BY id ASC
                """,
                (query, query),
            )
        else:
            cursor.execute(
                """
                SELECT id, full_name, date_of_birth, email, glucose, haemoglobin, cholesterol, ai_remarks, created_at, updated_at
                FROM patients
                ORDER BY id ASC
                """
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_patient_by_id(
    patient_id: int, db_path: str = DEFAULT_DB_PATH
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single patient record by ID. Returns None if not found.
    """
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, full_name, date_of_birth, email, glucose, haemoglobin, cholesterol, ai_remarks, created_at, updated_at
            FROM patients
            WHERE id = ?
            """,
            (patient_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def update_patient(
    patient_id: int,
    full_name: str,
    date_of_birth: str,
    email: str,
    glucose: float,
    haemoglobin: float,
    cholesterol: float,
    ai_remarks: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> bool:
    """
    Update an existing patient's details and assessment data.
    Preserves original assessment values as submitted.
    """
    init_db(db_path)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE patients
            SET full_name = ?,
                date_of_birth = ?,
                email = ?,
                glucose = ?,
                haemoglobin = ?,
                cholesterol = ?,
                ai_remarks = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                full_name.strip(),
                date_of_birth.strip(),
                email.strip(),
                float(glucose),
                float(haemoglobin),
                float(cholesterol),
                ai_remarks,
                now_str,
                patient_id,
            ),
        )
        return cursor.rowcount > 0


def delete_patient(patient_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Delete a patient record by ID.
    Returns True if a record was deleted, False otherwise.
    """
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        return cursor.rowcount > 0


def get_patient_stats(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Calculate summary statistics for the dashboard:
    total patients, average glucose, average haemoglobin, average cholesterol.
    """
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_patients,
                AVG(glucose) as avg_glucose,
                AVG(haemoglobin) as avg_haemoglobin,
                AVG(cholesterol) as avg_cholesterol
            FROM patients
            """
        )
        row = cursor.fetchone()
        if row and row["total_patients"] > 0:
            return {
                "total_patients": row["total_patients"],
                "avg_glucose": round(row["avg_glucose"], 1) if row["avg_glucose"] is not None else 0.0,
                "avg_haemoglobin": round(row["avg_haemoglobin"], 1) if row["avg_haemoglobin"] is not None else 0.0,
                "avg_cholesterol": round(row["avg_cholesterol"], 1) if row["avg_cholesterol"] is not None else 0.0,
            }
        return {
            "total_patients": 0,
            "avg_glucose": 0.0,
            "avg_haemoglobin": 0.0,
            "avg_cholesterol": 0.0,
        }
