import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
from fpdf import FPDF
import os

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="💑 Finanças Casal JR & VIC",
    layout="wide"
)

# =========================
# USUÁRIOS
# =========================
USERS = {
    "junior": "9391",
    "victoria": "1612"
}

DATA_FILE = "dados_financas.csv"

COLUNAS_PADRAO = [
    "ID",
    "Descricao",
    "Data",
    "Valor Parcela",
    "Valor Total",
    "Parcela",
    "Total Parcelas",
    "Pago",
    "Data Pagamento"
]

# =========================
# CSS PREMIUM
# =========================
st.markdown("""
<style>
.big-title {
    text-align:center;
    font-size:42px;
    font-weight:800;
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom:20px;
}
.card {
    background: rgba(255,255,255,0.05);
    padding:18px;
    border-radius:16px;
    backdrop-filter: blur(10px);
}
</style>
""", unsafe_allow_html=True)

# =========================
# BANCO
# =========================
def carregar_dados():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

        # 🔥 GARANTE COLUNAS (corrige KeyError)
        for col in COLUNAS_PADRAO:
            if col not in df.columns:
                df[col] = None

        return df[COLUNAS_PADRAO]

    return pd.DataFrame(columns=COLUNAS_PADRAO)

def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)

df = carregar_dados()

# =========================
# LOGIN
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

def login_screen():
    st.markdown('<div class="big-title">💑 Finanças Casal JR & VIC</div>', unsafe_allow_html=True)
    st.markdown("### 🔐 Acesso Premium")

    usuario = st.text_input("Usuário").lower()
    senha = st.text_input("Senha", type="password")

    if usuario and senha:
        if usuario in USERS and USERS[usuario] == senha:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

if not st.session_state.logado:
    login_screen()
    st.stop()

# =========================
# TÍTULO
# =========================
st.markdown('<div class="big-title">💑 Finanças Casal JR & VIC</div>', unsafe_allow_html=True)

# =========================
# NOVA COMPRA
# =========================
st.markdown("## ➕ Nova Compra")

col1, col2, col3 = st.columns(3)

descricao = col1.text_input("Descrição")
valor_total = col2.number_input("Valor total da compra", min_value=0.0, format="%.2f")
parcelas = col3.number_input("Parcelas", min_value=1, max_value=24, step=1)

data_compra = st.date_input("Mês da compra", datetime.today())

if st.button("💾 Salvar Compra"):

    if descricao and valor_total > 0:

        valor_parcela = valor_total / parcelas

        novos = []

        for i in range(parcelas):
            data_parcela = data_compra + relativedelta(months=i)

            novos.append({
                "ID": datetime.now().timestamp() + i,
                "Descricao": descricao,
                "Data": data_parcela.strftime("%Y-%m"),
                "Valor Parcela": round(valor_parcela, 2),
                "Valor Total": valor_total,
                "Parcela": i + 1,
                "Total Parcelas": parcelas,
                "Pago": False,
                "Data Pagamento": ""
            })

        df = pd.concat([df, pd.DataFrame(novos)], ignore_index=True)
        salvar_dados(df)
        st.success("Compra lançada com sucesso!")
        st.rerun()

# =========================
# FILTRO MENSAL
# =========================
st.markdown("## 📅 Filtro mensal")

mes_filtro = st.text_input(
    "Selecione o mês (YYYY-MM)",
    datetime.today().strftime("%Y-%m")
)

df_mes = df[df["Data"] == mes_filtro]

# =========================
# DASHBOARD
# =========================
total_mes = df_mes["Valor Parcela"].sum()
pago_mes = df_mes[df_mes["Pago"] == True]["Valor Parcela"].sum()
restante_mes = total_mes - pago_mes

c1, c2, c3 = st.columns(3)
c1.metric("💰 Total", f"R$ {total_mes:,.2f}")
c2.metric("✅ Pago", f"R$ {pago_mes:,.2f}")
c3.metric("⏳ Restante", f"R$ {restante_mes:,.2f}")

# =========================
# LISTA DE DESPESAS
# =========================
st.markdown("## 📋 Despesas do mês")

for idx, row in df_mes.iterrows():
    with st.container():
        c1, c2, c3, c4, c5 = st.columns([3,2,2,1,1])

        c1.write(row["Descricao"])
        c2.write(f"R$ {row['Valor Parcela']:,.2f}")

        # 🔥 seguro contra KeyError
        try:
            parcela_txt = f"{int(row['Parcela'])}ª de {int(row['Total Parcelas'])}x"
        except:
            parcela_txt = "Única"

        c3.write(parcela_txt)

        pago = c4.checkbox(
            "Pago",
            value=bool(row["Pago"]),
            key=f"pago_{idx}"
        )

        if pago != row["Pago"]:
            df.loc[idx, "Pago"] = pago
            df.loc[idx, "Data Pagamento"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            salvar_dados(df)
            st.rerun()

        if c5.button("🗑️", key=f"del_{idx}"):
            df = df.drop(idx)
            salvar_dados(df)
            st.rerun()

# =========================
# GRÁFICO
# =========================
if not df_mes.empty:
    graf = df_mes.groupby("Descricao")["Valor Parcela"].sum().reset_index()
    fig = px.pie(graf, names="Descricao", values="Valor Parcela")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# PDF
# =========================
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Financas Casal JR e VIC", ln=True)
    pdf.cell(0, 10, f"Mes: {mes_filtro}", ln=True)
    pdf.cell(0, 10, f"Gerado em: {datetime.now()}", ln=True)

    pdf.ln(10)

    for _, r in df_mes.iterrows():
        pdf.cell(0, 8, f"{r['Descricao']} - R$ {r['Valor Parcela']}", ln=True)

    nome = "relatorio_financas.pdf"
    pdf.output(nome)
    return nome

if st.button("📄 Baixar relatório PDF"):
    arquivo = gerar_pdf()
    with open(arquivo, "rb") as f:
        st.download_button(
            "⬇️ Download PDF",
            f,
            file_name=arquivo
        )
