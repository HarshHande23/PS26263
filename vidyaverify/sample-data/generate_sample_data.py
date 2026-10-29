"""
Generates synthetic sample CSV and XLSX data files for VidyaVerify demo and testing.
Uses realistic synthetic Indian names, masked identifiers, and test cases for:
1. Valid import batch
2. Batch with deliberate validation errors (format, missing fields)
3. Duplicate APAAR IDs and multi-institution conflict scenarios
4. Intake overflow testing
"""
import os
import pandas as pd

SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Clean valid batch
valid_rows = [
    {
        "full_name": "Aarav Sharma",
        "apaar_id": "123456789012",
        "date_of_birth": "2004-05-14",
        "gender": "Male",
        "email": "aarav.sharma@example.edu.in",
        "phone": "9876543210",
        "enrolment_number": "ENR2024CS001",
        "programme_code": "BTECH-CSE",
        "academic_year": "2024-25",
        "admission_date": "2024-08-01",
        "admission_category": "general",
        "is_supernumerary": "false",
        "is_nri": "false",
        "is_oci": "false",
        "is_foreign_national": "false",
        "is_pwd": "false",
    },
    {
        "full_name": "Diya Patel",
        "apaar_id": "234567890123",
        "date_of_birth": "2003-11-22",
        "gender": "Female",
        "email": "diya.patel@example.edu.in",
        "phone": "9876543211",
        "enrolment_number": "ENR2024CS002",
        "programme_code": "BTECH-CSE",
        "academic_year": "2024-25",
        "admission_date": "2024-08-01",
        "admission_category": "obc",
        "is_supernumerary": "false",
        "is_nri": "false",
        "is_oci": "false",
        "is_foreign_national": "false",
        "is_pwd": "false",
    },
    {
        "full_name": "Rohan Deshmukh",
        "apaar_id": "345678901234",
        "date_of_birth": "2004-02-18",
        "gender": "Male",
        "email": "rohan.d@example.edu.in",
        "phone": "9876543212",
        "enrolment_number": "ENR2024CS003",
        "programme_code": "BTECH-CSE",
        "academic_year": "2024-25",
        "admission_date": "2024-08-01",
        "admission_category": "sc",
        "is_supernumerary": "false",
        "is_nri": "false",
        "is_oci": "false",
        "is_foreign_national": "false",
        "is_pwd": "false",
    },
    {
        "full_name": "Ananya Iyer",
        "apaar_id": "456789012345",
        "date_of_birth": "2004-09-30",
        "gender": "Female",
        "email": "ananya.iyer@example.edu.in",
        "phone": "9876543213",
        "enrolment_number": "ENR2024ECE001",
        "programme_code": "BTECH-ECE",
        "academic_year": "2024-25",
        "admission_date": "2024-08-01",
        "admission_category": "ews",
        "is_supernumerary": "false",
        "is_nri": "false",
        "is_oci": "false",
        "is_foreign_national": "false",
        "is_pwd": "false",
    },
    {
        "full_name": "Vikramaditya Rao",
        "apaar_id": "567890123456",
        "date_of_birth": "2003-07-08",
        "gender": "Male",
        "email": "vikram.rao@example.edu.in",
        "phone": "9876543214",
        "enrolment_number": "ENR2024ME001",
        "programme_code": "BTECH-MECH",
        "academic_year": "2024-25",
        "admission_date": "2024-08-01",
        "admission_category": "management_quota",
        "is_supernumerary": "false",
        "is_nri": "false",
        "is_oci": "false",
        "is_foreign_national": "false",
        "is_pwd": "false",
    },
]

# 2. Batch with errors (missing name, malformed apaar, future date)
error_rows = [
    {
        "full_name": "Kavita Nair",
        "apaar_id": "678901234567",
        "date_of_birth": "2004-03-12",
        "gender": "Female",
        "email": "kavita.nair@example.com",
        "phone": "9876543215",
        "enrolment_number": "ERR001",
        "programme_code": "BTECH-CSE",
        "academic_year": "2024-25",
        "admission_date": "2024-08-01",
        "admission_category": "general",
        "is_supernumerary": "false",
    },
    {
        "full_name": "",  # ERROR: Missing name
        "apaar_id": "789012345678",
        "date_of_birth": "2004-04-14",
        "gender": "Male",
        "email": "noname@example.com",
        "phone": "9876543216",
        "enrolment_number": "ERR002",
        "programme_code": "BTECH-CSE",
        "academic_year": "2024-25",
        "admission_date": "2024-08-01",
        "admission_category": "general",
        "is_supernumerary": "false",
    },
    {
        "full_name": "Tariq Khan",
        "apaar_id": "INVALID123",  # ERROR: Malformed APAAR ID (not 12 digits)
        "date_of_birth": "2004-01-10",
        "gender": "Male",
        "email": "invalid_email_format",  # WARNING: Malformed email
        "phone": "9876543217",
        "enrolment_number": "ERR003",
        "programme_code": "BTECH-CSE",
        "academic_year": "2024-25",
        "admission_date": "2024-08-01",
        "admission_category": "general",
        "is_supernumerary": "false",
    },
    {
        "full_name": "Kavita Nair",  # Within-file duplicate of row 1
        "apaar_id": "678901234567",
        "date_of_birth": "2004-03-12",
        "gender": "Female",
        "email": "kavita.nair2@example.com",
        "phone": "9876543218",
        "enrolment_number": "ERR004",
        "programme_code": "BTECH-CSE",
        "academic_year": "2024-25",
        "admission_date": "2024-08-01",
        "admission_category": "general",
        "is_supernumerary": "false",
    },
]

df_valid = pd.DataFrame(valid_rows)
df_errors = pd.DataFrame(error_rows)

df_valid.to_csv(os.path.join(SAMPLE_DIR, "sample_students_valid.csv"), index=False)
df_valid.to_excel(os.path.join(SAMPLE_DIR, "sample_students_valid.xlsx"), index=False)
df_errors.to_csv(os.path.join(SAMPLE_DIR, "sample_students_with_errors.csv"), index=False)

print("Generated sample CSV and XLSX datasets in:", SAMPLE_DIR)
