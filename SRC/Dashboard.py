import streamlit as st
import pandas as pd
import os
import glob
import base64
from Styles import apply_custom_styles
from Componentes import AbaDesempenhoIndividual, AbaEquipe, AbaComparacao, AbaDesempenhoPorData, botao_exportar_pdf

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

# --- CRIAÇÃO DO DATAFRAME PRINCIPAL ---
df = pd.concat(lista_dfs, ignore_index=True)
df.columns = [str(col).replace('\ufeff', '').strip().upper() for col in df.columns]

# --- INTEGRAÇÃO DO ARQUIVO TXT DE POSIÇÕES ---
caminho_posicoes = os.path.join(caminho_dados, "posicoes.txt")

if os.path.exists(caminho_posicoes):
    # 1. Remove qualquer coluna de posição que já tenha vindo dos CSVs para evitar duplicidade
    colunas_remover = [c for c in df.columns if c in ['POSIÇÃO', 'POSICAO', 'POSITION', 'POS']]
    if colunas_remover:
        df = df.drop(columns=colunas_remover)

    try:
        # 2. Lê o arquivo TXT usando o separador '|'
        df_posicoes = pd.read_csv(caminho_posicoes, sep='|', names=['PLAYER', 'POSIÇÃO'], engine='python')

        # 3. Padroniza os textos (remove espaços invisíveis e deixa tudo maiúsculo) para o cruzamento bater
        df_posicoes['PLAYER'] = df_posicoes['PLAYER'].astype(str).str.strip().str.upper()
        df_posicoes['POSIÇÃO'] = df_posicoes['POSIÇÃO'].astype(str).str.strip().str.upper()
        df['PLAYER'] = df['PLAYER'].astype(str).str.strip().str.upper()

        # 4. Cruza os dados: anexa a posição certa na linha de cada jogador
        df = pd.merge(df, df_posicoes, on='PLAYER', how='left')
    except Exception as e:
        st.warning(f"Não foi possível processar o arquivo posicoes.txt: {e}")

# --- 5. ORGANIZAÇÃO DAS ABAS ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["👥 Desempenho Equipe", "📅 Desempenho por Data", "👤 Desempenho Individual", "⚔️ Comparar Atletas"])

# --- ABA 1: COMPARATIVO EQUIPE ---
with tab1:
    botao_exportar_pdf()
    AbaEquipe(df).render()

# --- ABA 2: COMPARATIVO POR DATA ---
with tab2:
    botao_exportar_pdf()
    AbaDesempenhoPorData(df).render()

# --- ABA 3: DESEMPENHO ATLETA ---
with tab3:
    botao_exportar_pdf()
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
        # Mantém a organização cronológica crescente criada anteriormente
        datas_comp = df['DATA'].drop_duplicates().sort_values(ascending=True).dt.strftime('%d/%m/%Y').tolist()

        # ALTERADO PARA MULTISELECT: Permite selecionar várias datas. Por padrão, seleciona a sessão mais recente.
        datas_comp_sel = st.multiselect(
            " Datas das Atividades",
            options=datas_comp,
            default=[datas_comp[-1]] if datas_comp else [],
            key="data_comp_multi"
        )

        # Filtra usando .isin() para abranger todas as datas marcadas
        if datas_comp_sel:
            df_partida_comp = df[df['DATA'].dt.strftime('%d/%m/%Y').isin(datas_comp_sel)]

        # Coleta e exibe de forma limpa todas as atividades únicas do período selecionado
        if not df_partida_comp.empty and 'ATIVIDADE' in df_partida_comp.columns:
            atividades_unicas = df_partida_comp['ATIVIDADE'].drop_duplicates().to_numpy().flatten()
            atividades_str = ", ".join(str(at) for at in atividades_unicas)
            st.caption(f"📌 Atividades no Período: :green[{atividades_str}]")

    with c_filtros2:
        if not df_partida_comp.empty:
            lista_comp = [p for p in df_partida_comp['PLAYER'].unique() if "TEAM AVER" not in str(p).upper()]
        else:
            lista_comp = []

        # Mantém o limite máximo de 3 atletas
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
        st.info("💡 Selecione pelo menos uma data para construir a análise comparativa.")