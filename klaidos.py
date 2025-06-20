import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt

st.set_page_config(page_title="Verslo procesų analizė", layout="wide")
st.title("📌 Procesų tobulinimo žurnalas")

# Google Sheets konfigūracija
sheet_id = "1aWqYAcEuAEyV4vbnvsZt475Dc4pg2lNe_EoNX-G-rtY"
worksheet_name = "Sheet1"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key(sheet_id)
worksheet = sheet.worksheet(worksheet_name)

# Duomenų nuskaitymas
records = worksheet.get_all_records()
df = pd.DataFrame(records)

# Naujo įrašo forma
st.subheader("➕ Registruoti naują įrašą")

with st.form("register_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("Data", value=datetime.date.today())
        order_no = st.text_input("Užsakymo nr.")
        department = st.text_input("Skyrius")

    with col2:
        responsible = st.text_input("Atsakingas asmuo")
        client = st.text_input("Klientas")
        supplier = st.text_input("Tiekėjas")

    with col3:
        problem = st.text_area("Problemos aprašymas")
        consequence = st.text_area("Pasekmė")

    solution = st.text_input("Sprendimas")
    informed = st.selectbox("Ar buvo informuota laiku?", ["Taip", "Ne"])
    notes = st.text_area("Pastabos")

    submitted = st.form_submit_button("💾 Įrašyti")

    if submitted:
        new_row = [
            date.strftime("%Y-%m-%d"),
            order_no,
            problem,
            consequence,
            department,
            responsible,
            client,
            supplier,
            solution,
            informed,
            notes
        ]
        worksheet.append_row(new_row)
        st.success("✅ Įrašas išsaugotas!")
        st.experimental_rerun()

# Jei turime duomenų – rodyti analizę
if not df.empty:
    st.subheader("📋 Įrašų sąrašas")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Atsisiųsti CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="procesu_zurnalas.csv",
        mime="text/csv"
    )

    # Paruošiam duomenis analizei
    df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
    df = df.dropna(subset=["Data"])  # pašalinam tuščias datas
    df["Mėnuo"] = df["Data"].dt.to_period("M").astype(str)

    monthly_counts = df["Mėnuo"].value_counts().sort_index()

    st.subheader("📈 Klaidos pagal mėnesius")

    fig1, ax1 = plt.subplots()
    monthly_counts.plot(kind="line", marker="o", ax=ax1)
    ax1.set_title("Klaidų skaičius pagal mėnesius")
    ax1.set_xlabel("Mėnuo")
    ax1.set_ylabel("Klaidos")
    st.pyplot(fig1)

    st.subheader("🧭 Klaidų pasiskirstymas procentais")

    fig2, ax2 = plt.subplots()
    monthly_counts.plot(kind="pie", autopct='%1.1f%%', ax=ax2)
    ax2.set_ylabel("")
    ax2.set_title("Klaidos pagal mėnesius (%)")
    st.pyplot(fig2)

    if "Ne" in df["Ar buvo informuota laiku?"].values:
        st.warning("⚠️ Yra įrašų, apie kuriuos nebuvo pranešta laiku. Vertėtų stiprinti komunikaciją.")
else:
    st.info("Dar nėra užregistruotų duomenų.")
