import streamlit as st
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import plotly.express as px
import bcrypt
import os
import io

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Finanças Casal JR & VIC",
    layout="wide",
    page_icon="💑"
)

DATA_FILE = "dados_financas.csv"

# =====================================================
# CSS PREMIUM
# =====================================================

st.markdown("""
<style>
.main-title{
    text-align:center;
    font-size:42px;
    font-weight:800;
    background: linear-gradient(90deg,#7c3aed,#06b6d4);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.card{
    background:#111827;
    padding:18px;
    border-radius:14px;
    margin-bottom:10px;
}
.badge-pago{color:#10b981;font-weight:700;}
.badge-vencer{color:#f59e0b;font-weight:700;}
.badge-atrasado{color:#ef4444;font-weight:700;}
</style>
""", unsafe_allow_html=True)

# =====================================================
# USUÁRIOS (HASH FIXO)
# =====================================================

def make_hash(p):
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt())

def check_hash(p, h):
    return bcrypt.checkpw(p.encode(), h)

USERS = {
    "junior": make_hash("9391"),
    "victoria": make_hash("1612"),
}

# =====================================================
# DATA
# =====================================================

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["Vencimento"] = pd.to_datetime(df["Vencimento"])
        df["Data Pagamento"] = pd.to_datetime(df["Data Pagamento"], errors="coerce")
        return df
    return pd.DataFrame(columns=[
        "Descrição","Valor Parcela","Parcela",
        "Total Parcelas","Vencimento",
        "Pago","Data Pagamento"
    ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# =====================================================
# SESSION
# =====================================================

if "logged" not in st.session_state:
    st.session_state.logged = False

if "df" not in st.session_state:
    st.session_state.df = load_data()

if "editando" not in st.session_state:
    st.session_state.editando = None

# =====================================================
# LOGIN COM ENTER
# =====================================================

def tela_login():
    st.markdown("<h1 class='main-title'>💑 Finanças Casal JR & VIC</h1>", unsafe_allow_html=True)

    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            user = st.text_input("Usuário")
            pwd = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar", use_container_width=True)

            if entrar:
                u = user.lower()
                if u in USERS and check_hash(pwd, USERS[u]):
                    st.session_state.logged = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos")

if not st.session_state.logged:
    tela_login()
    st.stop()

# =====================================================
# HEADER
# =====================================================

top1,top2 = st.columns([6,1])
top1.markdown("<h1 class='main-title'>💑 Finanças Casal JR & VIC</h1>", unsafe_allow_html=True)

if top2.button("🚪 Logout"):
    st.session_state.logged = False
    st.rerun()

# =====================================================
# FUNÇÕES
# =====================================================

def status_conta(row):
    hoje = date.today()
    if row["Pago"]:
        return "Pago"
    if row["Vencimento"].date() < hoje:
        return "Atrasado"
    return "A vencer"

# =====================================================
# CADASTRO INTELIGENTE
# =====================================================

st.subheader("➕ Nova Compra")

c1,c2,c3 = st.columns(3)
descricao = c1.text_input("Descrição")
valor_total = c2.number_input("Valor total da compra", min_value=0.0)
parcelas = c3.selectbox("Parcelas", list(range(1,25)))
data_compra = st.date_input("Mês da compra")

if st.button("💾 Registrar compra", use_container_width=True):

    if descricao and valor_total > 0:

        valor_parcela = valor_total / parcelas
        hoje = datetime.today()

        mes_atual = datetime(hoje.year, hoje.month, 1)
        mes_compra = datetime(data_compra.year, data_compra.month, 1)

        diff = (mes_atual.year - mes_compra.year)*12 + (mes_atual.month - mes_compra.month)

        for i in range(parcelas):

            venc = mes_compra + relativedelta(months=i)
            pago_auto = i < diff

            nova = {
                "Descrição": descricao,
                "Valor Parcela": valor_parcela,
                "Parcela": i+1,
                "Total Parcelas": parcelas,
                "Vencimento": venc,
                "Pago": pago_auto,
                "Data Pagamento": datetime.now() if pago_auto else None
            }

            st.session_state.df = pd.concat(
                [st.session_state.df, pd.DataFrame([nova])],
                ignore_index=True
            )

        save_data(st.session_state.df)
        st.success("Compra registrada com parcelamento automático!")
        st.rerun()

# =====================================================
# FILTRO MENSAL
# =====================================================

st.subheader("📅 Filtro mensal")

df = st.session_state.df.copy()

if not df.empty:

    df["Mes"] = df["Vencimento"].dt.to_period("M")
    meses = sorted(df["Mes"].astype(str).unique())
    mes_sel = st.selectbox("Selecione o mês", meses)

    df_mes = df[df["Mes"].astype(str) == mes_sel]

    total = df_mes["Valor Parcela"].sum()
    pago = df_mes[df_mes["Pago"]]["Valor Parcela"].sum()
    restante = total - pago

    m1,m2,m3 = st.columns(3)
    m1.metric("💰 Total", f"R$ {total:,.2f}")
    m2.metric("✅ Pago", f"R$ {pago:,.2f}")
    m3.metric("⏳ Restante", f"R$ {restante:,.2f}")

    st.markdown("### 📋 Despesas do mês")

    for idx,row in df_mes.iterrows():

        status = status_conta(row)
        badge = {
            "Pago":"badge-pago",
            "A vencer":"badge-vencer",
            "Atrasado":"badge-atrasado"
        }[status]

        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            a,b,c,d,e,f = st.columns([3,1.3,1.5,1,1,1])

            a.write(f"**{row['Descrição']}**")
            b.markdown(f"<span class='{badge}'>{status}</span>", unsafe_allow_html=True)
            c.write(f"{int(row['Parcela'])}ª de {int(row['Total Parcelas'])}x")
            d.write(f"R$ {row['Valor Parcela']:.2f}")

            pago_check = e.checkbox("Pago", value=row["Pago"], key=f"pg{idx}")

            if pago_check and not row["Pago"]:
                st.session_state.df.at[idx,"Pago"] = True
                st.session_state.df.at[idx,"Data Pagamento"] = datetime.now()
                save_data(st.session_state.df)

            if f.button("✏️", key=f"edit{idx}"):
                st.session_state.editando = idx

            if f.button("🗑️", key=f"del{idx}"):
                st.session_state.df = st.session_state.df.drop(idx).reset_index(drop=True)
                save_data(st.session_state.df)
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# EDITOR COMPLETO
# =====================================================

if st.session_state.editando is not None:

    idx = st.session_state.editando
    row = st.session_state.df.loc[idx]

    st.subheader("✏️ Editar despesa")

    with st.form("edit_form"):
        nova_desc = st.text_input("Descrição", value=row["Descrição"])
        novo_valor = st.number_input("Valor parcela", value=float(row["Valor Parcela"]))
        novo_pago = st.checkbox("Pago", value=row["Pago"])

        salvar = st.form_submit_button("Salvar alterações")

        if salvar:
            st.session_state.df.at[idx,"Descrição"] = nova_desc
            st.session_state.df.at[idx,"Valor Parcela"] = novo_valor
            st.session_state.df.at[idx,"Pago"] = novo_pago

            if novo_pago:
                st.session_state.df.at[idx,"Data Pagamento"] = datetime.now()

            save_data(st.session_state.df)
            st.session_state.editando = None
            st.success("Atualizado!")
            st.rerun()

# =====================================================
# DASHBOARD
# =====================================================

st.subheader("📊 Evolução financeira")

if not df.empty:
    resumo = df.groupby(df["Vencimento"].dt.to_period("M"))["Valor Parcela"].sum().reset_index()
    resumo["Vencimento"] = resumo["Vencimento"].astype(str)

    fig = px.line(resumo, x="Vencimento", y="Valor Parcela", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# PDF PROFISSIONAL
# =====================================================

if not df.empty and st.button("📥 Baixar relatório do mês"):

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("Finanças Casal JR e VIC", styles["Title"]))
    elements.append(Paragraph(f"Mês: {mes_sel}", styles["Normal"]))
    elements.append(Paragraph(f"Gerado em: {datetime.now()}", styles["Normal"]))
    elements.append(Spacer(1,12))

    data = [df_mes.columns.tolist()] + df_mes.astype(str).values.tolist()
    table = Table(data)
    table.setStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('GRID',(0,0),(-1,-1),0.5,colors.black)
    ])

    elements.append(table)
    doc.build(elements)

    st.download_button(
        "Download PDF",
        data=buffer.getvalue(),
        file_name=f"Financas_{mes_sel}.pdf",
        mime="application/pdf"
    )
