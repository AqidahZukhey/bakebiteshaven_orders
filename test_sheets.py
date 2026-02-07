import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("🧪 Google Sheets Access Test")

# --- Google Sheets setup ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )
    client = gspread.authorize(creds)
    st.success("✅ Service account authorized successfully!")
except Exception as e:
    st.error("❌ Failed to authorize service account")
    st.write(e)

# --- Test accessing sheet ---
SPREADSHEET_KEY = "18MA-Oy0nbasDc0Kr-2iUhYSpj-R4AmLHsog1N8fUMzI"  # replace with your sheet key

try:
    sheet = client.open_by_key(SPREADSHEET_KEY).sheet1
    st.success("✅ Accessed Google Sheet successfully!")
    # Show first 5 rows
    data = sheet.get_all_values()
    st.write("First 5 rows of the sheet:")
    st.write(data[:5])
except Exception as e:
    st.error("❌ Failed to access the sheet")
    st.write(e)
