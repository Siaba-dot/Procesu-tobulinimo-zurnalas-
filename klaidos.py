import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import matplotlib.pyplot as plt

# Google Sheets prisijungimas
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("tavo_failas.json", scope)
gc = gspread.authorize(credentials)

# Pasirink Google Sheets dokumentą ir lentelę
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/...")
worksheet = spreadsheet.sheet1

# Įkeliami duomenys į DataFrame
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Puslapio pavadinimas
st.title("🔧 Probleminių situacijų registras")

# --- Duomenų įvedimo forma ---
with st.form("problemos_forma"):
    st.subheader("➕ Registruoti naują problemą")
    date_input = st.date_input("Data", value=date.today())
    order_no = st.text_input("Užsakymo nr.")
    problem = st.text_area("Problemos aprašymas")
    consequence = st.text_area("Pasekmė")
    department = st.text_input("Skyrius")
    responsible = st.text_input("Atsakingas asmuo")
    klientas = st.text_input("Klientas")
    tiekejas = st.text_input("Tiekėjas")
    solution = st.text_input("Sprendimas")
    informed = st.selectbox("Ar buvo informuota laiku?", ["Taip", "Ne"])
    notes = st.text_area("Pastabos")
    submit = st.form_submit_button("➕ Pridėti problemą")

    if submit:
        nauja_eilute = [
            date_input.strftime("%Y-%m-%d"),
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
        worksheet.append_row(nauja_eilute)
        st.success("✅ Problema sėkmingai įrašyta!")

# --- Duomenų atvaizdavimas ---
st.subheader("📋 Registruotų problemų sąrašas")
st.dataframe(df)

# --- Atsisiuntimas ---
st.download_button("📁 Atsisiųsti CSV", data=df.to_csv(index=False), file_name="problemos.csv", mime="text/csv")

# --- Paprasta analizė ---
st.subheader("📊 Paprasta analizė")

# Paruošiame datą analizavimui
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["Mėnuo"] = df["Data"].dt.to_period("M").astype(str)

# Linijinis grafikas pagal mėnesius
mėnesiai = df.groupby("Mėnuo").size()

fig1, ax1 = plt.subplots()
ax1.plot(mėnesiai.index, mėnesiai.values, marker="o")
ax1.set_title("Klaidų skaičius pagal mėnesius")
ax1.set_ylabel("Klaidų kiekis")
ax1.set_xlabel("Mėnuo")
st.pyplot(fig1)

# Skritulinė diagrama pagal pasirinktą mėnesį
pasirinktas_mėnuo = st.selectbox("Pasirink mėnesį skritulinei diagramai", df["Mėnuo"].unique())

if pasirinktas_mėnuo:
    df_filtruotas = df[df["Mėnuo"] == pasirinktas_mėnuo]
    grupuota = df_filtruotas["Skyrius"].value_counts()

    if not grupuota.empty:
        fig2, ax2 = plt.subplots()
        ax2.pie(grupuota, labels=grupuota.index, autopct='%1.1f%%')
        ax2.set_title(f"Klaidų pasiskirstymas ({pasirinktas_mėnuo})")
        st.pyplot(fig2)
    else:
        st.info("Pasirinktame mėnesyje nėra duomenų.")

