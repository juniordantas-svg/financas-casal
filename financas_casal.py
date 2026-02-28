import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Finanças do Casal", layout="wide")

# ---------------- BANCO SQLITE ----------------
conn = sqlite3.connect("financas.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS despesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT,
    parcelas INTEGER,
    valor REAL,
    data TEXT,
    pago INTEGER
)
""")
conn.commit()

# ---------------- LOGIN ----------------
USERS = {
    "junior": "9391",
    "victoria": "1612",
}

if "logged" not in st.session_state:
    st.session_state.logged = False

def login():
    st.markdown("<h1 style='text-align:center;'>💰 Finanças do Casal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        user = st.text_input("Usuário")
        pwd = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):
            if USERS.get(user.lower()) == pwd:
                st.session_state.logged = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

# ---------------- EXPORTAÇÃO ----------------
def export_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()

def export_pdf(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Relatório de Despesas", styles["Title"])]

    data_table = [df.columns.tolist()] + df.astype(str).values.tolist()
    table = Table(data_table)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()

# ---------------- APP PRINCIPAL ----------------
def app():
    st.title("📊 Controle Financeiro")

    df = pd.read_sql("SELECT * FROM despesas", conn)

    st.subheader("➕ Nova Despesa")
    with st.form("form"):
        col1, col2, col3, col4, col5 = st.columns(5)

        desc = col1.text_input("Descrição")
        parcelas = col2.number_input("Parcelas", min_value=1, step=1)
        valor = col3.number_input("Valor", min_value=0.0, step=0.01)
        data = col4.date_input("Data")
        pago = col5.checkbox("Pago")

        if st.form_submit_button("Salvar"):
            c.execute("INSERT INTO despesas (descricao, parcelas, valor, data, pago) VALUES (?, ?, ?, ?, ?)",
                      (desc, parcelas, valor, data.strftime("%Y-%m-%d"), int(pago)))
            conn.commit()
            st.success("Despesa salva!")
            st.rerun()

    if not df.empty:
        df["Pago"] = df["pago"].astype(bool)
        df_view = df[["descricao", "parcelas", "valor", "data", "Pago"]]
        df_view.columns = ["Descrição", "Parcelas", "Valor", "Data", "Pago"]

        total = df["valor"].sum()
        pago_total = df[df["pago"] == 1]["valor"].sum()
        a_vencer = total - pago_total

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Geral", f"R$ {total:,.2f}")
        col2.metric("Total Pago", f"R$ {pago_total:,.2f}")
        col3.metric("A Vencer", f"R$ {a_vencer:,.2f}")

        st.dataframe(df_view, use_container_width=True)

        col1, col2 = st.columns(2)
        col1.download_button("Baixar Excel", export_excel(df_view), "despesas.xlsx")
        col2.download_button("Baixar PDF", export_pdf(df_view), "despesas.pdf")

if not st.session_state.logged:
    login()
else:
    app()