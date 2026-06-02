import streamlit as st
import pandas as pd
import os
import glob
import base64
from Styles import apply_custom_styles
from Componentes import AbaDesempenhoIndividual, AbaEquipe, AbaComparacao, AbaDesempenhoPorData

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Análise de Desempenho", initial_sidebar_state="collapsed")
apply_custom_styles()

# --- 2. GESTÃO DE CAMINHOS ---
diretorio_script = os.path.dirname(os.path.abspath(__file__))
diretorio_raiz = os.path.dirname(diretorio_script)

caminho_dados = os.path.join(diretorio_raiz, "Data")
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
            <h1 style="color: #32CD32; margin: 0; font-size: 48px; font-weight: 700;">MONITORAMENTO FÍSICO SERRA BRANCA</h1>
        </div>
        """, unsafe_allow_html=True
    )
else:
    st.markdown("<h1 style='text-align: center; color: #32CD32;'>MONITORAMENTO FÍSICO SERRA BRANCA</h1>",
                unsafe_allow_html=True)

st.divider()

# --- 4. CARREGAMENTO MÚLTIPLO DE ARQUIVOS CSV ---
arquivos_csv = glob.glob(os.path.join(caminho_dados, "*.csv"))
lista_dfs = []

if len(arquivos_csv) == 0:
    st.error(f"🚨 Nenhum arquivo .csv foi encontrado na pasta: {caminho_dados}")
    st.stop()

for arquivo in arquivos_csv:
    nome_arquivo = os.path.basename(arquivo)

    try:
        data_str = nome_arquivo[:10]
        data_arquivo = pd.to_datetime(data_str, format='%Y_%m_%d')
        atividade = nome_arquivo[11:].replace('.csv', '').strip()
    except Exception:
        data_arquivo = pd.to_datetime('today')
        atividade = "Sessão não identificada"

    try:
        df_temp = pd.read_csv(arquivo, sep=';', decimal=',', encoding='utf-8-sig')
    except Exception:
        df_temp = pd.read_csv(arquivo, sep=None, engine='python', encoding='utf-8-sig')

    df_temp['DATA'] = data_arquivo
    df_temp['ATIVIDADE'] = atividade
    lista_dfs.append(df_temp)

df = pd.concat(lista_dfs, ignore_index=True)
df.columns = [str(col).replace('\ufeff', '').strip().upper() for col in df.columns]

# --- 5. ORGANIZAÇÃO DAS ABAS ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["👥 Desempenho Equipe", "📅 Desempenho por Data", "👤 Desempenho Individual", "⚔️ Comparar Atletas"])

# --- ABA 1: COMPARATIVO EQUIPE ---
with tab1:
    AbaEquipe(df).render()

# --- ABA 2: COMPARATIVO POR DATA ---
with tab2:
    AbaDesempenhoPorData(df).render()

# --- ABA 3: DESEMPENHO ATLETA ---
with tab3:
    lista_jogadores = [p for p in df['PLAYER'].unique() if "TEAM AVER" not in str(p).upper()]
    atleta_sel = st.selectbox("👤 Selecione o Atleta", sorted(lista_jogadores), key="atleta_sel_aba3")

    st.markdown("<br>", unsafe_allow_html=True)

    if atleta_sel:
        AbaDesempenhoIndividual(df_completo=df, atleta=atleta_sel).render()
    else:
        st.warning("Nenhum atleta selecionado.")

# --- ABA 4: COMPARAR JOGADORES ---
with tab4:
    st.markdown("<h3 style='color: #C0C0C0; text-align: center;'>Comparativo Direto entre Atletas</h3>",
                unsafe_allow_html=True)

    df_partida_comp = pd.DataFrame()
    c_filtros1, c_filtros2 = st.columns(2)

    with c_filtros1:
        datas_comp = sorted(df['DATA'].dt.strftime('%d/%m/%Y').unique(), reverse=True)
        data_comp_sel = st.selectbox("📅 Data da Atividade", datas_comp, key="data_comp")

        if data_comp_sel:
            df_partida_comp = df[df['DATA'].dt.strftime('%d/%m/%Y') == data_comp_sel]

        # --- CORREÇÃO APLICADA AQUI ---
        # Garantindo que extraímos a string limpa mesmo com colunas duplicadas
        if not df_partida_comp.empty and 'ATIVIDADE' in df_partida_comp.columns:
            atividade_comp_poura = str(df_partida_comp['ATIVIDADE'].to_numpy().flatten()[0])
            st.caption(f"📌 Atividade Selecionada: :green[{atividade_comp_poura}]")

    with c_filtros2:
        if not df_partida_comp.empty:
            lista_comp = [p for p in df_partida_comp['PLAYER'].unique() if "TEAM AVER" not in str(p).upper()]
        else:
            lista_comp = []

        # Caixa de multiselect ajustada para até 3 atletas
        atletas_sel = st.multiselect(
            "👤 Selecione até 3 Atletas",
            options=sorted(lista_comp),
            default=sorted(lista_comp)[:2] if len(lista_comp) >= 2 else lista_comp,
            max_selections=3,
            key="atletas_comp_multi"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if not df_partida_comp.empty and len(atletas_sel) > 0:
        AbaComparacao(
            df_partida=df_partida_comp,
            df_completo=df,
            atletas=atletas_sel
        ).render()
    elif len(atletas_sel) == 0:
        st.info("💡 Selecione pelo menos um atleta na caixa acima para iniciar a comparação.")
    else:
        st.warning("Não há dados de atletas para a data selecionada.")