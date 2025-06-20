import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt

st.set_page_config(page_title="Problemų registravimo sistema", layout="wide")
st.title("🔍 Verslo problemų registravimo ir analizės sistema")

# Google Sheets nustatymai
sheet_id = "1aWqYAcEuAEyV4vbnvsZt475Dc4pg2lNe_EoNX-G-rtY"
worksheet_name = "Sheet1"

# Prisijungimas
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(credentials)
worksheet = client.open_by_key(sheet_id).worksheet(worksheet_name)

# Gauti duomenis
records = worksheet.get_all_records()
headers = worksheet.row_values(1)
df = pd.DataFrame(records)
if df.empty:
    df = pd.DataFrame(columns=headers)

# Forma
st.markdown("### ✏️ Naujos problemos registravimas")
with st.form("problem_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("Data", datetime.date.today())
        order_no = st.text_input("Užsakymo nr./Sąskaitos nr.")
        klientas = st.text_input("Klientas")
    with col2:
        problem = st.text_area("Problemos aprašymas")
        consequence = st.text_area("Pasekmė")
        tiekejas = st.text_input("Tiekėjas")
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
            klientas,
            tiekejas,
            solution,
            informed,
            notes
        ]
        worksheet.append_row(new_row)
        st.success("✅ Problema įregistruota sėkmingai!")
        st.rerun()

# Rodymas
if not df.empty:
    st.markdown("### 📋 Registruotų problemų sąrašas")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Atsisiųsti kaip CSV", csv, "problemos.csv", "text/csv")

    # Analizė
    st.markdown("### 📊 Analizė")
    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"])
        df["Metai-mėnuo"] = df["Data"].dt.to_period("M").astype(str)
        klaidos_per_men = df.groupby("Metai-mėnuo").size()

        fig1, ax1 = plt.subplots()
        klaidos_per_men.plot(kind="line", marker="o", ax=ax1)
        ax1.set_title("📈 Klaidos pagal mėnesius")
        ax1.set_xlabel("Metai-Mėnuo")
        ax1.set_ylabel("Klaidos")
        st.pyplot(fig1)

        pasirinktas = st.selectbox("Pasirink mėnesį analizei", klaidos_per_men.index)
        df_pas = df[df["Metai-mėnuo"] == pasirinktas]

        if not df_pas.empty and "Skyrius" in df_pas.columns:
            fig2, ax2 = plt.subplots()
            df_pas["Skyrius"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax2)
            ax2.set_ylabel("")
            ax2.set_title(f"🎯 Klaidos pagal skyrių ({pasirinktas})")
            st.pyplot(fig2)

    if "Ar buvo informuota laiku?" in df.columns:
        if "Ne" in df["Ar buvo informuota laiku?"].values:
            st.warning("⚠️ Yra problemų, apie kurias nebuvo informuota laiku. Reikalinga komunikacijos stiprinimas.")
else:
    st.info("🔎 Kol kas nėra registruotų problemų.")
