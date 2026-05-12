import streamlit as st
import pandas as pd
import os
import base64
from Styles import apply_custom_styles
from Componentes import AbaDesempenho, AbaEquipe, AbaComparacao

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Análise de Desempenho", initial_sidebar_state="collapsed")
apply_custom_styles()

# Esconde a sidebar e ajusta o preenchimento superior
st.markdown("""
    <style>
        [data-testid='stSidebar'] {display: none;}
        .block-container {padding-top: 2rem;}
    </style>
""", unsafe_allow_html=True)

try:
    # --- 2. GESTÃO DE CAMINHOS ---
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    diretorio_raiz = os.path.dirname(diretorio_script)

    caminho_excel = os.path.join(diretorio_raiz, "Data", "Jogos Serra.xlsx")
    caminho_escudo = os.path.join(diretorio_raiz, "IMAGES", "Escudo Serra Branca.PNG")

    # --- 3. CABEÇALHO CENTRALIZADO ---
    if os.path.exists(caminho_escudo):
        def get_image_base64(path):
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()

        img_64 = get_image_base64(caminho_escudo)

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: center; gap: 40px; margin-bottom: 10px; padding-bottom: 25px;">
                <img src="data:image/png;base64,{img_64}" width="120">
                <h1 style="color: #32CD32; margin: 0; font-size: 48px; font-weight: 700;">ANÁLISE DE DADOS SERRA BRANCA</h1>
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown("<h1 style='text-align: center; color: #32CD32;'>ANÁLISE DE DADOS SERRA BRANCA</h1>", unsafe_allow_html=True)

    st.divider()

    # --- 4. CARREGAMENTO DE DADOS ---
    df = pd.read_excel(caminho_excel)
    df.columns = [str(col).strip().upper() for col in df.columns]
    df['DATA'] = pd.to_datetime(df['DATA'])

    # --- 5. ORGANIZAÇÃO DAS ABAS ---
    tab1, tab2, tab3 = st.tabs(["👤 Desempenho Atleta", "👥 Comparativo Equipe", "⚔️ Comparar Jogadores"])

    # --- ABA 1: DESEMPENHO ATLETA ---
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            data_opcoes = df['DATA'].dt.strftime('%d/%m/%Y').unique()
            data_sel_str = st.selectbox("📅 Selecione a Data", data_opcoes, key="data_filtro_atleta")

        df_partida = df[df['DATA'].dt.strftime('%d/%m/%Y') == data_sel_str]

        with c2:
            atleta_sel = st.selectbox("👤 Selecione o Atleta", sorted(df_partida['ATLETA'].unique()), key="atleta_sel_final")

        st.markdown("<br>", unsafe_allow_html=True)

        if not df_partida.empty:
            AbaDesempenho(df_partida, df, atleta_sel).render()
        else:
            st.warning("Selecione uma data válida.")

    # --- ABA 2: COMPARATIVO EQUIPE ---
    with tab2:
        AbaEquipe(df).render()

    # --- ABA 3: COMPARAR JOGADORES ---
    with tab3:
        st.markdown("<h3 style='color: #C0C0C0; text-align: center;'>Comparativo Direto entre Atletas</h3>",
                    unsafe_allow_html=True)

        c_filtros1, c_filtros2 = st.columns(2)
        with c_filtros1:
            datas_comp = df['DATA'].dt.strftime('%d/%m/%Y').unique()
            data_comp_sel = st.selectbox(" Data da Partida", datas_comp, key="data_comp")

        df_partida_comp = df[df['DATA'].dt.strftime('%d/%m/%Y') == data_comp_sel]

        with c_filtros2:
            posicoes = sorted(df_partida_comp['POSICAO'].unique()) if not df_partida_comp.empty else []
            pos_sel = st.selectbox(" Filtrar por Posição", posicoes, key="pos_comp")

        if not df_partida_comp.empty:
            df_posicao = df_partida_comp[df_partida_comp['POSICAO'] == pos_sel]
            lista_atletas = sorted(df_posicao['ATLETA'].unique())

            col_atleta1, col_atleta2 = st.columns(2)
            with col_atleta1:
                atleta1 = st.selectbox("Jogador 1", lista_atletas, key="atleta1")
            with col_atleta2:
                default_idx = 1 if len(lista_atletas) > 1 else 0
                atleta2 = st.selectbox("Jogador 2", lista_atletas, index=default_idx, key="atleta2")

            if atleta1 and atleta2:
                AbaComparacao(
                    df_partida=df_partida_comp,
                    df_completo=df,
                    atleta1=atleta1,
                    atleta2=atleta2,
                    posicao=pos_sel
                ).render()
        else:
            st.warning("Não há dados para a data selecionada.")

except Exception as e:
    st.error(f"Erro crítico no sistema: {e}")