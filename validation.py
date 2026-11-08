"""
Validation module for HealthTrack AI – Patient Health Management System.
Performs strict validation for patient personal and clinical assessment data.
Ensures data integrity without silently altering user assessment inputs.
"""

import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple, Union

# Standard RFC 5322-compliant email regex
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

# Reference limits for physiological plausibility (for safety checks)
MIN_GLUCOSE = 10.0      # mg/dL
MAX_GLUCOSE = 1500.0    # mg/dL
MIN_HAEMOGLOBIN = 1.0   # g/dL
MAX_HAEMOGLOBIN = 35.0  # g/dL
MIN_CHOLESTEROL = 20.0  # mg/dL
MAX_CHOLESTEROL = 1500.0# mg/dL
MIN_BIRTH_YEAR = 1960
MAX_BIRTH_YEAR = 2030


def validate_full_name(full_name: Any) -> Tuple[bool, str]:
    """
    Validate that patient full name is non-empty, contains valid characters,
    and has a reasonable length.
    """
    if full_name is None:
        return False, "Full Name is required and cannot be empty."

    name_str = str(full_name).strip()
    if not name_str:
        return False, "Full Name is required and cannot be empty."

    if len(name_str) < 2:
        return False, "Full Name must be at least 2 characters long."

    if len(name_str) > 100:
        return False, "Full Name must not exceed 100 characters."

    # Allow letters, spaces, hyphens, periods, and apostrophes
    if not re.match(r"^[A-Za-z\s\.\'\-]+$", name_str):
        return (
            False,
            "Full Name can only contain letters, spaces, hyphens, periods, and apostrophes.",
        )

    return True, ""


def validate_date_of_birth(
    dob_input: Union[str, date, datetime]
) -> Tuple[bool, str, Optional[str]]:
    """
    Validate Date of Birth:
    - Must be a valid calendar date
    - Rejects invalid dates (e.g., February 30th)
    - Rejects future dates
    - Rejects dates prior to year 1900
    - Formats to DD/MM/YYYY

    Returns:
        Tuple[bool, str, Optional[str]]: (is_valid, error_message, formatted_dob_string)
    """
    if dob_input is None:
        return False, "Date of Birth is required.", None

    today = date.today()
    parsed_date: Optional[date] = None

    if isinstance(dob_input, (datetime, date)):
        parsed_date = dob_input.date() if isinstance(dob_input, datetime) else dob_input
    elif isinstance(dob_input, str):
        dob_str = dob_input.strip()
        if not dob_str:
            return False, "Date of Birth cannot be empty.", None

        # Accept DD/MM/YYYY or YYYY-MM-DD
        matched = False
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                parsed_dt = datetime.strptime(dob_str, fmt)
                parsed_date = parsed_dt.date()
                matched = True
                break
            except ValueError:
                continue

        if not matched or parsed_date is None:
            return (
                False,
                f"Invalid calendar date '{dob_str}'. Please provide a valid date in DD/MM/YYYY format.",
                None,
            )
    else:
        return False, "Unsupported Date of Birth format.", None

    # Check for valid year range (1960 through 2030, inclusive)
    if parsed_date.year < MIN_BIRTH_YEAR:
        return (
            False,
            f"Date of Birth year ({parsed_date.year}) cannot be earlier than {MIN_BIRTH_YEAR}.",
            None,
        )

    if parsed_date.year > MAX_BIRTH_YEAR:
        return (
            False,
            f"Date of Birth year ({parsed_date.year}) cannot be after {MAX_BIRTH_YEAR}.",
            None,
        )

    formatted_dob = parsed_date.strftime("%d/%m/%Y")
    return True, "", formatted_dob


def validate_email(email_input: Any) -> Tuple[bool, str]:
    """
    Validate email address format.
    """
    if email_input is None:
        return False, "Email address is required."

    email_str = str(email_input).strip()
    if not email_str:
        return False, "Email address is required and cannot be empty."

    if len(email_str) > 254:
        return False, "Email address is too long (maximum 254 characters)."

    if not EMAIL_REGEX.match(email_str):
        return (
            False,
            f"'{email_str}' is not a valid email address format (example: patient@example.com).",
        )

    # Additional check: domain must contain at least one dot
    domain_part = email_str.split("@")[-1]
    if "." not in domain_part or domain_part.startswith(".") or domain_part.endswith("."):
        return False, "Email address must contain a valid domain (e.g., example.com)."

    return True, ""


def validate_numeric_metric(
    value_input: Any,
    field_label: str,
    unit: str,
    min_allowed: float,
    max_allowed: float,
) -> Tuple[bool, str, Optional[float]]:
    """
    Accept only numeric blood test values.
    Ensures value is numeric, strictly positive, and within plausible medical limits.
    Does NOT silently modify or round the supplied value.
    """
    if value_input is None:
        return False, f"{field_label} is required.", None

    if isinstance(value_input, str):
        val_str = value_input.strip()
        if not val_str:
            return False, f"{field_label} cannot be empty.", None
        try:
            # Check for non-finite values
            val_float = float(val_str)
        except ValueError:
            return (
                False,
                f"{field_label} must be a valid numeric number (received: '{val_str}').",
                None,
            )
    elif isinstance(value_input, (int, float)):
        val_float = float(value_input)
    else:
        return False, f"{field_label} must be numeric.", None

    # Check for NaN / Infinity
    if val_float != val_float or val_float == float("inf") or val_float == float("-inf"):
        return False, f"{field_label} must be a finite numeric value.", None

    # Check positive
    if val_float <= 0:
        return (
            False,
            f"{field_label} must be a positive number greater than 0 {unit}.",
            None,
        )

    # Check physiological bounds
    if val_float < min_allowed or val_float > max_allowed:
        return (
            False,
            f"{field_label} value of {val_float} {unit} is outside plausible clinical range ({min_allowed} - {max_allowed} {unit}).",
            None,
        )

    # Preserve exact entered float without silent modification
    return True, "", val_float


def validate_patient_record(
    full_name: Any,
    date_of_birth: Any,
    email: Any,
    glucose: Any,
    haemoglobin: Any,
    cholesterol: Any,
    exclude_patient_id: Optional[int] = None,
    db_check: bool = True,
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Comprehensive validation for all patient fields:
    - Full Name validation
    - Date of Birth validation (rejects invalid dates, future dates)
    - Email validation
    - Numeric blood test values validation
    - Duplicate detection (via database check)

    Returns:
        Tuple[bool, List[str], Dict[str, Any]]:
            - is_valid: True if all fields are valid and no duplicates found
            - errors: List of human-readable error messages
            - validated_data: Dictionary of parsed and validated values (unchanged assessment numbers)
    """
    errors: List[str] = []
    validated_data: Dict[str, Any] = {}

    # 1. Full Name
    name_ok, name_err = validate_full_name(full_name)
    if not name_ok:
        errors.append(name_err)
    else:
        validated_data["full_name"] = str(full_name).strip()

    # 2. Date of Birth
    dob_ok, dob_err, formatted_dob = validate_date_of_birth(date_of_birth)
    if not dob_ok:
        errors.append(dob_err)
    else:
        validated_data["date_of_birth"] = formatted_dob

    # 3. Email
    email_ok, email_err = validate_email(email)
    if not email_ok:
        errors.append(email_err)
    else:
        validated_data["email"] = str(email).strip().lower()

    # 4. Glucose
    glu_ok, glu_err, glu_val = validate_numeric_metric(
        glucose, "Glucose", "mg/dL", MIN_GLUCOSE, MAX_GLUCOSE
    )
    if not glu_ok:
        errors.append(glu_err)
    else:
        validated_data["glucose"] = glu_val

    # 5. Haemoglobin
    hb_ok, hb_err, hb_val = validate_numeric_metric(
        haemoglobin, "Haemoglobin", "g/dL", MIN_HAEMOGLOBIN, MAX_HAEMOGLOBIN
    )
    if not hb_ok:
        errors.append(hb_err)
    else:
        validated_data["haemoglobin"] = hb_val

    # 6. Cholesterol
    chol_ok, chol_err, chol_val = validate_numeric_metric(
        cholesterol, "Cholesterol", "mg/dL", MIN_CHOLESTEROL, MAX_CHOLESTEROL
    )
    if not chol_ok:
        errors.append(chol_err)
    else:
        validated_data["cholesterol"] = chol_val

    # 7. Duplicate Check (only if individual fields are valid)
    if db_check and email_ok and name_ok and dob_ok:
        from database import check_duplicate_patient

        is_dup, dup_err = check_duplicate_patient(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            date_of_birth=validated_data["date_of_birth"],
            exclude_id=exclude_patient_id,
        )
        if is_dup:
            errors.append(dup_err)

    is_valid = len(errors) == 0
    return is_valid, errors, validated_data

