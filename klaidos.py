import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Problemų registravimo sistema", layout="wide")
st.title("🔍 Verslo problemų registravimo ir analizės sistema")

# Google Sheets nustatymai
sheet_id = "1aWqYAcEuAEyV4vbnvsZt475Dc4pg2lNe_EoNX-G-rtY"
worksheet_name = "Sheet1"

# Prisijungimas prie Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(credentials)
sheet = client.open_by_key(sheet_id)
worksheet = sheet.worksheet(worksheet_name)

# Nuskaityti esamus duomenis
records = worksheet.get_all_records()
df = pd.DataFrame(records)

st.markdown("""
### ✏️ Naujos problemos registravimas
""")

with st.form("problem_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("Data", datetime.date.today())
        order_no = st.text_input("Užsakymo nr.")

    with col2:
        problem = st.text_area("Problemos aprašymas")
        consequence = st.text_area("Pasekmė")

    with col3:
        department = st.text_input("Skyrius")
        responsible = st.text_input("Atsakingas asmuo")

    solution = st.text_input("Sprendimas")
    informed = st.selectbox("Ar buvo informuota laiku?", ["Taip", "Ne"])
    notes = st.text_area("Pastabos")

    submitted = st.form_submit_button("➕ Pridėti problemą")

    if submitted:
        new_row = [
            date.strftime("%Y-%m-%d"),
            order_no,
            problem,
            consequence,
            department,
            responsible,
            solution,
            informed,
            notes
        ]
        worksheet.append_row(new_row)
        st.success("Problema įregistruota sėkmingai!")
        st.experimental_rerun()

# Rodyti duomenis
if not df.empty:
    st.markdown("""
    ### 📊 Registruotų problemų sąrašas
    """)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("🗂️ Atsisiųsti kaip CSV", csv, "registruotos_problemos.csv", "text/csv")

    # Paprasta analizė
    st.markdown("""
    ### 📊 Paprasta analizė
    """)
    col_a, col_b = st.columns(2)

    with col_a:
        by_person = df["Atsakingas asmuo"].value_counts()
        st.bar_chart(by_person)

    with col_b:
        by_department = df["Skyrius"].value_counts()
        st.bar_chart(by_department)

    if "Ne" in df["Ar buvo informuota laiku?"].values:
        st.warning("Yra problemų, apie kurias nebuvo pranešta laiku. Reikalingas komunikacijos stiprinimas.")
else:
    st.info("Kol kas nėra registruotų problemų.")
