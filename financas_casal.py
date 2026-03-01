import streamlit as st
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io
from supabase import create_client

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="💑 Finanças Casal JR & VIC", layout="wide")

USERS = {
    "junior": "9391",
    "victoria": "1612"
}

# =========================
# SUPABASE CLIENT
# =========================
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =========================
# INIT DB (cria tabela se não existir)
# =========================
def init_db():
    tables = supabase.table("expenses").select("*").execute()
    if tables.error:
        # Criação inicial da tabela
        # Obs: Supabase só permite criar tabelas via SQL ou interface web
        # Aqui vamos tentar criar via RPC SQL
        query = """
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            descricao TEXT,
            valor_parcela NUMERIC,
            total_parcelas INTEGER,
            parcela_atual INTEGER,
            data_vencimento DATE,
            pago BOOLEAN DEFAULT FALSE,
            data_pagamento TIMESTAMP
        );
        """
        supabase.rpc("sql", {"query": query}).execute()

# =========================
# LOGIN
# =========================
if "logged" not in st.session_state:
    st.session_state.logged = False

def login_screen():
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("## 💑 Finanças Casal JR & VIC")

        user = st.text_input("Usuário")
        pwd = st.text_input("Senha", type="password")

        if user and pwd:
            if USERS.get(user.lower()) == pwd:
                st.session_state.logged = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

if not st.session_state.logged:
    login_screen()
    st.stop()

# =========================
# FUNÇÕES DB (via Supabase)
# =========================
def inserir_parcelas(descricao, valor_total, parcelas, data_compra):
    valor_parcela = round(valor_total / parcelas, 2)
    for i in range(parcelas):
        venc = data_compra + relativedelta(months=i)
        supabase.table("expenses").insert({
            "descricao": descricao,
            "valor_parcela": valor_parcela,
            "total_parcelas": parcelas,
            "parcela_atual": i+1,
            "data_vencimento": venc,
            "pago": False
        }).execute()

def carregar_dados():
    res = supabase.table("expenses").select("*").order("data_vencimento").execute()
    if res.error:
        st.error("Erro ao carregar dados")
        return pd.DataFrame()
    df = pd.DataFrame(res.data)
    if not df.empty:
        df["data_vencimento"] = pd.to_datetime(df["data_vencimento"])
    return df

def marcar_pago(id, status):
    if status:
        supabase.table("expenses").update({
            "pago": True,
            "data_pagamento": datetime.now()
        }).eq("id", id).execute()
    else:
        supabase.table("expenses").update({
            "pago": False,
            "data_pagamento": None
        }).eq("id", id).execute()

def excluir(id):
    supabase.table("expenses").delete().eq("id", id).execute()

# =========================
# HEADER
# =========================
st.title("💑 Finanças Casal JR & VIC")

# =========================
# NOVA COMPRA
# =========================
st.subheader("➕ Nova Compra")

c1, c2, c3 = st.columns(3)

descricao = c1.text_input("Descrição")
valor_total = c2.number_input("Valor total da compra", min_value=0.0, format="%.2f")
parcelas = c3.number_input("Parcelas", min_value=1, max_value=24, step=1)

data_compra = st.date_input("Mês da compra", value=date.today())

if st.button("Salvar compra", use_container_width=True):
    if descricao and valor_total > 0:
        inserir_parcelas(descricao, valor_total, parcelas, data_compra)
        st.success("Compra cadastrada!")
        st.experimental_rerun()

# =========================
# FILTRO MENSAL
# =========================
st.subheader("📅 Filtro mensal")

df = carregar_dados()

meses = df["data_vencimento"].dt.strftime("%Y-%m").unique().tolist() if not df.empty else []
mes_sel = st.selectbox("Selecione o mês", meses)

if mes_sel:
    df_mes = df[df["data_vencimento"].dt.strftime("%Y-%m") == mes_sel]
else:
    df_mes = df

# =========================
# KPIs
# =========================
total = df_mes["valor_parcela"].sum() if not df_mes.empty else 0
pago = df_mes[df_mes["pago"] == True]["valor_parcela"].sum() if not df_mes.empty else 0
restante = total - pago

k1, k2, k3 = st.columns(3)
k1.metric("💰 Total", f"R$ {total:,.2f}")
k2.metric("✅ Pago", f"R$ {pago:,.2f}")
k3.metric("⏳ Restante", f"R$ {restante:,.2f}")

# =========================
# TABELA
# =========================
st.subheader("📋 Despesas do mês")

for _, row in df_mes.iterrows():
    c1, c2, c3, c4, c5 = st.columns([3,1,1,1,1])

    c1.write(row["descricao"])
    c2.write(f"{int(row['parcela_atual'])}ª de {int(row['total_parcelas'])}x")
    c3.write(f"R$ {row['valor_parcela']:,.2f}")

    pago_check = c4.checkbox(
        "Pago",
        value=row["pago"],
        key=f"pg_{row['id']}"
    )
    if pago_check != row["pago"]:
        marcar_pago(row["id"], pago_check)
        st.experimental_rerun()

    if c5.button("🗑️", key=f"del_{row['id']}"):
        excluir(row["id"])
        st.experimental_rerun()

# =========================
# PDF
# =========================
st.divider()

def gerar_pdf(df_pdf, mes):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("Finanças Casal JR e VIC", styles["Title"]))
    elements.append(Paragraph(f"Mês: {mes}", styles["Normal"]))
    elements.append(Paragraph(f"Gerado em: {datetime.now()}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    tabela = [["Descrição", "Parcela", "Valor", "Pago"]]

    for _, r in df_pdf.iterrows():
        tabela.append([
            r["descricao"],
            f"{int(r['parcela_atual'])}/{int(r['total_parcelas'])}",
            f"R$ {r['valor_parcela']:,.2f}",
            "Sim" if r["pago"] else "Não"
        ])

    table = Table(tabela)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.purple),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),0.25,colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer

if not df_mes.empty:
    pdf_file = gerar_pdf(df_mes, mes_sel)
    st.download_button(
        "📥 Baixar relatório mensal (PDF)",
        pdf_file,
        file_name=f"financas_{mes_sel}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
