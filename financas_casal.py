import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import os
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ================= CONFIG =================
st.set_page_config(page_title="💑 Finanças Casal JR & VIC", layout="wide")

USERS = {
    "junior": "9391",
    "victoria": "1612"
}

DATA_FILE = "dados_financas.csv"

COLUNAS = [
    "ID","Usuario","Descricao","Data","Valor Parcela","Valor Total",
    "Parcela","Total Parcelas","Pago","Data Pagamento"
]

# ================= THEME =================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def aplicar_css():
    if st.session_state.dark_mode:
        bg = "#0e1117"
        card = "#161b22"
        text = "white"
    else:
        bg = "#f5f7fb"
        card = "white"
        text = "#111"

    st.markdown(f"""
    <style>
    .stApp {{background:{bg}; color:{text};}}
    .big-title {{
        text-align:center;
        font-size:42px;
        font-weight:800;
        background: linear-gradient(90deg,#8a2be2,#00c6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .card {{
        background:{card};
        padding:18px;
        border-radius:18px;
        box-shadow:0 8px 25px rgba(0,0,0,0.25);
    }}
    </style>
    """, unsafe_allow_html=True)

aplicar_css()

# ================= BANCO =================
def carregar():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        for c in COLUNAS:
            if c not in df.columns:
                df[c] = None
        return df[COLUNAS]
    return pd.DataFrame(columns=COLUNAS)

def salvar(df):
    df.to_csv(DATA_FILE, index=False)

df = carregar()

# ================= SESSION =================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "editando" not in st.session_state:
    st.session_state.editando = None

# ================= LOGIN =================
def tela_login():
    st.markdown('<div class="big-title">💑 Finanças Casal JR & VIC</div>', unsafe_allow_html=True)
    st.markdown("### 🔐 Acesso Premium")

    with st.form("login_form"):
        user = st.text_input("Usuário").lower()
        pwd = st.text_input("Senha", type="password")
        ok = st.form_submit_button("Entrar")

        if ok:
            if user in USERS and USERS[user] == pwd:
                st.session_state.logado = True
                st.session_state.usuario = user
                st.rerun()
            else:
                st.error("Credenciais inválidas")

if not st.session_state.logado:
    tela_login()
    st.stop()

# ================= HEADER =================
top1, top2 = st.columns([8,2])
top1.markdown('<div class="big-title">💑 Finanças Casal JR & VIC</div>', unsafe_allow_html=True)

if top2.button("🌙 / ☀️"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# filtra por usuário
df_user = df[df["Usuario"] == st.session_state.usuario]

# ================= NOVA COMPRA =================
st.markdown("## ➕ Nova Compra")

c1,c2,c3 = st.columns(3)
descricao = c1.text_input("Descrição")
valor_total = c2.number_input("Valor total", min_value=0.0, format="%.2f")
parcelas = c3.number_input("Parcelas", 1, 24, 1)
data_compra = st.date_input("Mês da compra", datetime.today())

if st.button("💾 Salvar Compra"):
    if descricao and valor_total > 0:
        valor_parcela = valor_total / parcelas
        novos = []

        for i in range(parcelas):
            data_parcela = data_compra + relativedelta(months=i)
            novos.append({
                "ID": datetime.now().timestamp()+i,
                "Usuario": st.session_state.usuario,
                "Descricao": descricao,
                "Data": data_parcela.strftime("%Y-%m"),
                "Valor Parcela": round(valor_parcela,2),
                "Valor Total": valor_total,
                "Parcela": i+1,
                "Total Parcelas": parcelas,
                "Pago": False,
                "Data Pagamento": ""
            })

        df = pd.concat([df,pd.DataFrame(novos)], ignore_index=True)
        salvar(df)
        st.success("Compra lançada!")
        st.rerun()

# ================= FILTRO =================
st.markdown("## 📅 Filtro mensal")
mes = st.text_input("Mês (YYYY-MM)", datetime.today().strftime("%Y-%m"))
df_mes = df_user[df_user["Data"] == mes]

# ================= DASHBOARD =================
total = df_mes["Valor Parcela"].sum()
pago = df_mes[df_mes["Pago"]==True]["Valor Parcela"].sum()
restante = total - pago

m1,m2,m3 = st.columns(3)
m1.metric("💰 Total", f"R$ {total:,.2f}")
m2.metric("✅ Pago", f"R$ {pago:,.2f}")
m3.metric("⏳ Restante", f"R$ {restante:,.2f}")

# previsão simples IA-like
media_mensal = df_user.groupby("Data")["Valor Parcela"].sum().mean() if not df_user.empty else 0
st.info(f"🤖 Previsão média mensal: R$ {media_mensal:,.2f}")

# ================= ALERTA =================
vencer = df_mes[df_mes["Pago"]==False]
if not vencer.empty:
    st.warning(f"⚠️ {len(vencer)} conta(s) pendente(s) este mês")

# ================= LISTA =================
st.markdown("## 📋 Despesas")

for idx,row in df_mes.iterrows():
    with st.container():
        a,b,c,d,e,f = st.columns([3,2,2,1,1,1])

        a.write(row["Descricao"])
        b.write(f"R$ {row['Valor Parcela']:,.2f}")
        c.write(f"{int(row['Parcela'])}ª de {int(row['Total Parcelas'])}x")

        pago_chk = d.checkbox("Pago", bool(row["Pago"]), key=f"pg{idx}")
        if pago_chk != row["Pago"]:
            df.loc[idx,"Pago"] = pago_chk
            df.loc[idx,"Data Pagamento"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            salvar(df)
            st.rerun()

        if e.button("✏️", key=f"ed{idx}"):
            st.session_state.editando = idx

        if f.button("🗑️", key=f"dl{idx}"):
            df = df.drop(idx)
            salvar(df)
            st.rerun()

# ================= GRÁFICOS =================
if not df_user.empty:
    evol = df_user.groupby("Data")["Valor Parcela"].sum().reset_index()
    fig = px.line(evol, x="Data", y="Valor Parcela", title="📈 Evolução mensal")
    st.plotly_chart(fig, use_container_width=True)

# ================= PDF =================
st.markdown("## 📄 Relatório")

if st.button("📄 Baixar PDF"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elems = [
        Paragraph("Finanças Casal JR & VIC", styles["Title"]),
        Paragraph(f"Mês: {mes}", styles["Normal"]),
        Paragraph(f"Gerado em: {datetime.now()}", styles["Normal"]),
        Spacer(1,12)
    ]

    dados = [["Descrição","Valor","Parcela","Pago"]]
    for _,r in df_mes.iterrows():
        dados.append([
            r["Descricao"],
            f"R$ {r['Valor Parcela']:.2f}",
            f"{int(r['Parcela'])}/{int(r['Total Parcelas'])}",
            "Sim" if r["Pago"] else "Não"
        ])

    tabela = Table(dados)
    tabela.setStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('GRID',(0,0),(-1,-1),0.5,colors.black)
    ])

    elems.append(tabela)
    doc.build(elems)

    st.download_button(
        "⬇️ Download",
        data=buffer.getvalue(),
        file_name=f"Relatorio_{mes}.pdf",
        mime="application/pdf"
    )
