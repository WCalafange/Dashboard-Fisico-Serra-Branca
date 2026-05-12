import streamlit as st

def apply_custom_styles():
    st.markdown(
        """
        <style>
        /* Esconde o menu de hambúrguer e a sidebar completamente */
        [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        
        /* Ajusta o espaçamento do topo */
        .block-container {
            padding-top: 1rem;
        }
        
        /* 1. Fundo Principal */
        .stApp {
            background-color: #001524; 
        }

        /* 2. Caixa de Informações (st.info) */
        div[data-testid="stNotification"] {
            background-color: #0A243D;
            color: white;
            border: none;
        }

        /* 3. Caixas de Seleção */
        div[data-baseweb="select"] > div {
            background-color: #0A243D !important;
            color: white !important;
            border: 1px solid #32CD32 !important;
        }


        /* 4. Títulos */
        h1, h2, h3 {
            color: #32CD32 !important;
        }

        /* 5. Texto das Abas */
        .stTabs [data-baseweb="tab"] {
            color: white !important;
        }

        /* 6. CORREÇÃO DO HEADER E BOTÃO */
        header[data-testid="stHeader"] {
            visibility: visible !important;
            background: rgba(0,0,0,0) !important; /* Deixa o fundo do topo transparente */
        }

        }
        .main .block-container {
            padding-top: 2rem; /* Ajusta o respiro no topo */
        }
        
        /* Esconde o botão da sidebar e a própria sidebar */
        [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebar"] {
            display: none;
        }
        
        /* Ajusta a área principal para usar todo o topo */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        """,
        unsafe_allow_html=True
    )