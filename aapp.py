import streamlit as st
import pandas as pd
import uuid
import hashlib
import random

st.set_page_config(page_title="Cadeia de Custódia", layout="wide")

# ---------------------------
# FUNÇÕES DE NEGÓCIO
# ---------------------------

def calcular_media(row):
    media_parcial = (row["M1"] + row["M2"]) / 2
    
    if media_parcial >= 7:
        return media_parcial
    
    if row["M3"] >= 7:
        return row["M3"]
    
    return media_parcial

def calcular_status(row):
    frequencia_minima = 75
    
    if row["FR"] < frequencia_minima:
        return "REPROVADO POR FALTA"
    
    media_parcial = (row["M1"] + row["M2"]) / 2
    
    if media_parcial >= 7:
        return "APROVADO"
    
    if row["M3"] >= 7:
        return "APROVADO"
    
    return "REPROVADO POR NOTA"


# ---------------------------
# BASE DE ALUNOS
# ---------------------------

def gerar_alunos():
    nomes = [
        "Carlos Mendes","Ana Beatriz Lima","João Victor Alves","Mariana Rocha",
        "Felipe Castro","Juliana Souza","Bruno Henrique","Larissa Martins",
        "Gabriel Silva","Camila Oliveira","Pedro Henrique","Isabela Santos",
        "Rafael Costa","Amanda Nogueira","Lucas Pereira","Fernanda Lima",
        "Matheus Rodrigues","Patrícia Gomes","Thiago Almeida","Beatriz Moraes",
        "Leonardo Araújo","Vanessa Ribeiro","Eduardo Barros","Letícia Carvalho",
        "Gustavo Teixeira","Bianca Freitas","André Fernandes","Natália Duarte",
        "Daniel Moreira","Carolina Batista"
    ]
    
    dados = []
    
    for i in range(30):
        m1 = random.randint(4, 9)
        m2 = random.randint(4, 9)
        m3 = random.randint(4, 9)
        fr = random.randint(60, 100)
        
        dados.append({
            "Matrícula": f"2026{i+1:03}",
            "Nome": nomes[i],
            "M1": m1,
            "M2": m2,
            "M3": m3,
            "FR": fr
        })
    
    df = pd.DataFrame(dados)
    df["MF"] = df.apply(calcular_media, axis=1)
    df["STATUS"] = df.apply(calcular_status, axis=1)
    
    return df


if "alunos" not in st.session_state:
    st.session_state.alunos = gerar_alunos()

# ---------------------------
# LOGIN
# ---------------------------

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("CADEIA DE CUSTÓDIA NA ERA DIGITAL")
    
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("ENTRAR"):
        if usuario and senha:
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Preencha usuário e senha.")
else:
    
    st.title("UNIVERSIDADE CEARENSE")
    st.subheader("Direito Processual Penal I – 2026.1")
    
    df = st.session_state.alunos
    
    aprovados = df[df["STATUS"] == "APROVADO"].shape[0]
    reprovados = df.shape[0] - aprovados
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total de Alunos", df.shape[0])
        st.metric("Aprovados", aprovados)
        st.metric("Reprovados", reprovados)
    
    with col2:
        st.bar_chart(df["MF"])
    
    st.divider()
    
    if st.button("ALUNOS"):
        st.dataframe(df, use_container_width=True)
    
    if st.button("SAIR"):
        st.session_state.logado = False
        st.rerun()
