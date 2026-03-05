# streamlit_app.py
importar streamlit como st
import pandas as pd
importar aleatório

st.set_page_config(page_title="Portal Universitas", layout="wide", initial_sidebar_state="collapsed")

# =============================
# ESTADO
# =============================
se "logado" não estiver em st.session_state:
    st.session_state.logado = Falso

# =============================
# FUNÃ‡ÃƒO DADOS ALUNOS
# =============================
def gerar_alunos():
    caça = [
        "Ana Silva", "Bruno Costa", "Carla Mendes",
        "Daniel Souza", "Eduarda Lima", "Felipe Rocha",
        "Gabriela Alves", "Henrique Martins",
        "Isabela Ramos", "João Ferreira"
    ]
    dados = []
    para nome em scri:
        nota1 = random.randint(4,10)
        nota2 = random.randint(4,10)
        mídia = arredondar((nota1 + nota2)/2,1)
        status = "Aprovado" if media >=6 else "Reprovado"
        dados.append([nome, nota1, nota2, mídia, status])
    df = pd.DataFrame(dados, colunas=["Aluno","Nota 1","Nota 2","Média","Status"])
    retornar df

# =============================
# SISTEMA PRINCIPAL
# =============================
def tela_sistema():
    st.title("ðŸ“š Cadeia de Custódia - Sistema de Notas")

    col1, col2 = st.columns([3, 1])
    com col2:
        se st.button("ðŸšª Sair"):
            st.session_state.logado = Falso
            st.rerun()

    st.markdown("---")

    df_alunos = gerar_alunos()

    st.subheader("ðŸ“Š Notas dos Alunos")
    st.dataframe(df_alunos, use_container_width=True)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    com col1:
        st.metric("Total de Alunos", len(df_alunos))
    com col2:
        aprovados = len(df_alunos[df_alunos["Status"] == "Aprovado"])
        st.metric("Aprovados", aprovados)
    com col3:
        reprovados = len(df_alunos[df_alunos["Status"] == "Reprovado"])
        st.metric("Reprovados", reprovados)

# =============================
# LOGIN ESTILIZADO - DESIGN AZUL COM ILUSTRAÇÃO
# =============================
def tela_login():
    # CSS Personalizado - Baseado na imagem fornecida
    st.markdown("""
    <style>
        /* Remover padding padrã do Streamlit */
        .block-container {
            preenchimento: 0 !importante;
            largura-máxima: 100% !importante;
        }

        /* Esconder cabeçalho e rodapé do Streamlit */
        cabeçalho {visibilidade: oculto;}
        rodapé {visibilidade: oculto;}
        #MenuPrincipal {visibilidade: oculta;}

        /* Estilo do corpo - fundo branco */
        .stApp {
            fundo: #f5f5f5;
        }

        /* Container de duas colunas */
        [data-testid="column"] {
            preenchimento: 0 !importante;
        }

        /* Entradas customizadas - brancos com borda arredondada */
        .stTextInput > div > div > input {
            raio da borda: 25px;
            preenchimento: 15px 20px;
            fronteira: nenhuma;
            tamanho da fonte: 15px;
            fundo: branco;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .stTextInput > div > div > input::placeholder {
            cor: #999;
        }

        /* Etiquetas Esconder */
        .stTextInput > rótulo {
            exibir: nenhum;
        }

        /* Marque esta caixa para me lembrar */
        .stCheckbox {
            cor: branca;
            tamanho da fonte: 13px;
        }

        /* Botão de login - verde */
        .stButton > botão {
            largura: 100%;
            preenchimento: 15px;
            raio da borda: 25px;
            fronteira: nenhuma;
            fundo: #00C851;
            cor: branca;
            tamanho da fonte: 16px;
            peso da fonte: 700;
            cursor: ponteiro;
            transição: todos os 0,3s de facilidade;
            margem superior: 15px;
            text-transform: maiúsculas;
            espaçamento entre letras: 1px;
            box-shadow: 0 4px 12px rgba(0,200,81,0.3);
        }

        .stButton > botão:hover {
            fundo: #00A843;
            transformar: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,200,81,0.4);
        }

        /* Mensagem de erro */
        .stAlert {
            raio da borda: 15px;
            margem superior: 15px;
        }
    </style>
    "", unsafe_allow_html=True)

    # Layout de duas colunas
    col1, col2 = st.columns([1, 1.2])

    # ========== COLUNA ESQUERDA - PAINEL AZUL ==========
    com col1:
        st.markdown("""
        <div style="
            fundo: gradiente-linear(180deg, #00B4DB 0%, #0083B0 100%);
            altura: 100vh;
            Exibir: flexível;
            flex-direction: coluna;
            justificar-conteúdo: centralizado;
            alinhamento-itens: centro;
            preenchimento: 60px 40px;
            box-shadow: 4px 0 20px rgba(0,0,0,0.1);
        ">
            <div style="width: 100%; max-width: 340px;">
                <h1 style="
                    cor: branca;
                    tamanho da fonte: 32px;
                    peso da fonte: 300;
                    espaçamento entre letras: 3px;
                    margem-inferior: 50px;
                    alinhamento do texto: centralizado;
                "BEM-VINDO(A)"
            </div>
        </div>
        "", unsafe_allow_html=True)

        # Formulário dentro do painel azul
        st.markdown('<div style="margin-top: -580px; padding: 0 40px;">', unsafe_allow_html=True)

        com st.form("login_form", clear_on_submit=False):
            usuário = st.text_input(
                "usuário",
                espaço reservado="Nome de usuário",
                chave="usuario_input",
                visibilidade_do_rótulo="recolhido"
            )

            senha = st.text_input(
                "senha",
                tipo="senha",
                placeholder="Senha",
                chave="senha_input",
                visibilidade_do_rótulo="recolhido"
            )

            col_check, col_forgot = st.columns([1, 1])
            com col_check:
                lembrar = st.checkbox("Lembrar", key="remember_check")
            com col_forgot:
                st.markdown('<p style="color: white; font-size: 13px; text-align: right; margin-top: 5px;">Esqueceu sua senha?</p>', unsafe_allow_html=True)

            enviar = st.form_submit_button("ENVIAR")

            Se enviar:
                if usuário == "dantas" e senha == "1234":
                    st.session_state.logado = True
                    st.success("âœ… Login realizado com sucesso!")
                    st.balloons()
                    st.rerun()
                outro:
                    st.error("Usuário ou senha inválida")

        st.markdown('</div>', unsafe_allow_html=True)

    # ========== COLUNA DIREITA - ILUSTRAÇÃO ==========
    com col2:
        st.markdown("""
        <div style="
            altura: 100vh;
            Exibir: flexível;
            justificar-conteúdo: centralizado;
            alinhamento-itens: centro;
            fundo: branco;
            posição: relativa;
            overflow: oculto;
        ">
            <div style="text-align: center; position: relative; z-index: 2;">
                <svg width="400" height="400" viewBox="0 0 400 400" style="max-width: 100%;">
                    <!-- Avião de papel -->
                    <path d="M 320 40 L 360 60 L 340 70 Z" fill="#00B4DB" opacity="0.8">
                        <animateTransform attributeName="transform" type="translate"
                            valores="0,0; 50,-20; 0,0" duração="4s" contagemRepetição="indefinida"/>
                    </path>
                    <path d="M 320 40 L 380 80" stroke="#00B4DB" stroke-width="2" stroke-dasharray="5,5" opacity="0.5"/>

                    <!-- Celular grande -->
                    <rect x="150" y="80" width="140" height="260" rx="20" fill="#00B4DB" opacity="0.9"/>
                    <rect x="160" y="90" width="120" height="240" rx="10" fill="#0083B0"/>

                    <!-- Tela do celular -->
                    <rect x="170" y="100" width="100" height="180" rx="8" fill="white"/>

                    <!-- cone de usuário -->
                    <circle cx="220" cy="140" r="20" fill="#00B4DB"/>
                    <circle cx="220" cy="135" r="8" fill="white"/>
                    <path d="M 210 145 Q 220 150 230 145" stroke="white" stroke-width="3" fill="none"/>

                    <!-- Campos de senha -->
                    <rect x="180" y="170" width="80" height="8" rx="4" fill="#00B4DB" opacity="0.6"/>
                    <rect x="180" y="185" width="80" height="8" rx="4" fill="#FF6B6B" opacity="0.6"/>

                    <!-- BotÃ£o no celular -->
                    <rect x="185" y="205" width="70" height="25" rx="12" fill="#00C851"/>

                    <!-- Pessoa à esquerda (mulher) -->
                    <ellipse cx="120" cy="200" rx="15" ry="20" fill="#2C3E50"/>
                    <circle cx="120" cy="185" r="12" fill="#F4A460"/>
                    <rect x="110" y="220" width="20" height="80" rx="5" fill="#00C851"/>
                    <rect x="105" y="235" width="10" height="50" rx="3" fill="#F4A460"/>
                    <rect x="125" y="235" width="10" height="50" rx="3" fill="#F4A460"/>

                    <!-- Pessoa à direita (homem sentado) -->
                    <circle cx="340" cy="280" r="15" fill="#F4A460"/>
                    <rect x="320" y="295" width="40" height="50" rx="8" fill="#0083B0"/>
                    <rect x="315" y="310" width="20" height="40" rx="4" fill="#F4A460"/>
                    <rect x="345" y="310" width="20" height="40" rx="4" fill="#F4A460"/>

                    <!-- Notebook -->
                    <rect x="310" y="320" width="60" height="35" rx="3" fill="#34495E"/>
                    <rect x="312" y="322" width="56" height="28" rx="2" fill="#ECF0F1"/>

                    <!-- Plantar bem -->
                    <ellipse cx="380" cy="340" rx="25" ry="15" fill="#95E1D3" opacity="0.6"/>
                    <path d="M 380 340 Q 385 320 390 310" stroke="#48C9B0" stroke-width="3" fill="none"/>
                    <path d="M 380 340 Q 375 325 370 315" stroke="#48C9B0" stroke-width="3" fill="none"/>
                    <ellipse cx="390" cy="310" rx="8" ry="12" fill="#48C9B0" opacity="0.7"/>
                    <ellipse cx="370" cy="315" rx="8" ry="12" fill="#48C9B0" opacity="0.7"/>
                </svg>
            </div>

            <!-- Elementos de fundo -->
            <div style="position: absolute; bottom: 30px; right: 30px; width: 100px; height: 100px; background: #E8F8F5; border-radius: 50%; opacity: 0.3;"></div>
            <div style="position: absolute; top: 80px; right: 100px; width: 60px; height: 60px; background: #D6EAF8; border-radius: 50%; opacity: 0.3;"></div>
        </div>
        "", unsafe_allow_html=True)

# =============================
# CONTROLE DE FLUXO
# =============================
se não st.session_state.logado:
    tela_login()
outro:
    tela_sistema()
