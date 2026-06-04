import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np
import unicodedata
import re
import streamlit.components.v1 as components


# --- BOTÃO DE EXPORTAR PDF ---
def botao_exportar_pdf():
    # Injeta um botão HTML que aciona o comando de imprimir a página principal (parent)
    components.html(
        """
        <script>
        function imprimir() {
            window.parent.print();
        }
        </script>
        <div style="display: flex; justify-content: flex-end;">
            <button onclick="imprimir()" style="background-color: #32CD32; color: #000000; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-family: sans-serif; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                🖨️ Exportar aba para PDF
            </button>
        </div>
        """,
        height=45
    )


# --- FUNÇÃO DE SANITIZAÇÃO ABSOLUTA ---
def sanitizar(texto):
    t = str(texto).upper().strip()
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    t = re.sub(r'[^A-Z0-9]', '', t)
    return t


# Extrai o valor usando Numpy
def extrair_valor(df_linha, chaves_possiveis):
    if df_linha.empty:
        return 0

    chaves_sanitizadas = [sanitizar(c) for c in chaves_possiveis]

    for col in df_linha.columns:
        if sanitizar(col) in chaves_sanitizadas:
            try:
                dados_crus = df_linha[col].to_numpy().flatten()
                if len(dados_crus) == 0:
                    continue
                val = dados_crus[0]
                if pd.isna(val):
                    return 0
                val_float = float(val)
                if val_float.is_integer():
                    return int(val_float)
                return round(val_float, 1)
            except Exception:
                pass
    return 0


# Lista universal de métricas do CSV
METRICAS_FISICAS = [
    'DISTÂNCIA TOTAL (M)', 'DURAÇÃO TOTAL (MIN)', 'DISTÂNCIA RELATIVA (M/MIN)',
    'VELOCIDADE MÁXIMA (KM/H)', 'DISTÂNCIA >19.8 KM/H', '%DISTÂNCIA>19.8 KM/H',
    'DISTÂNCIA >25.2 KM/H', '%DISTÂNCIA >25.2 KM/H', 'NºSPRINTS >25.2 KM/H',
    'DISTÂNCIA ACELERAÇÃO>3M/S²', 'NºACELERAÇÕES >3M/S²',
    'DISTÂNCIA DESACELERAÇÃO>3M/S²', 'NºDESACELERAÇÕES <-3M/S²',
    'DISTÂNCIA POTÊNCIA METABÓLICA >25.5 W/KG', 'TRAINING LOAD',
    'TLMAX_5MIN', 'DYNAMIC INDEX', 'MPMAX', 'PLAYER LOAD', 'STRENGTH INDEX',
    'DISTÂNCIA', 'VELOCIDADE MÁX', 'TLMAX_5M'
]


def obter_colunas_exatas(df_cols):
    cols_reais = []
    alvos_sanitizados = [sanitizar(m) for m in METRICAS_FISICAS]
    for col in df_cols:
        if sanitizar(col) in alvos_sanitizados:
            cols_reais.append(col)
    return list(dict.fromkeys(cols_reais))


class AbaEquipe:
    def __init__(self, df_completo):
        self.df_geral = df_completo

    def render(self):
        st.header("📊 Painel de Médias da Equipe (Team Average)")

        datas = self.df_geral['DATA'].drop_duplicates().sort_values(ascending=True).dt.strftime('%d/%m/%Y').tolist()
        data_sel = st.selectbox("📅 Filtrar Data para as Médias", datas, key="filtro_data_equipe")

        df_filtrado = self.df_geral[self.df_geral['DATA'].dt.strftime('%d/%m/%Y') == data_sel]

        # --- CORREÇÃO AQUI ---
        # Usamos to_numpy().flatten()[0] para garantir a extração do texto puro,
        # mesmo que existam colunas 'ATIVIDADE' duplicadas lidas do CSV.
        if not df_filtrado.empty and 'ATIVIDADE' in df_filtrado.columns:
            atividade_equipe = str(df_filtrado['ATIVIDADE'].to_numpy().flatten()[0])
            st.caption(f"📌 Atividade Selecionada: :green[{atividade_equipe}]")

        team_aver_df = df_filtrado[df_filtrado['PLAYER'].astype(str).str.contains("Team Aver", case=False, na=False)]

        if not team_aver_df.empty:
            st.divider()
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown("### 🏃‍♂️ Volume Geral")
                st.metric(label="Duração Total", value=f"{extrair_valor(team_aver_df, ['DURAÇÃO TOTAL (MIN)'])} min")
                st.metric(label="Distância Total",
                          value=f"{extrair_valor(team_aver_df, ['DISTÂNCIA TOTAL (M)', 'DISTÂNCIA'])} m")
                st.metric(label="Distância Relativa",
                          value=f"{extrair_valor(team_aver_df, ['DISTÂNCIA RELATIVA (M/MIN)', 'DISTÂNCIA/MIN'])} m/min")

            with col2:
                st.markdown("### ⚡ Alta Intensidade")
                st.metric(label="Velocidade Máxima",
                          value=f"{extrair_valor(team_aver_df, ['VELOCIDADE MÁXIMA (KM/H)', 'VELOCIDADE MÁX'])} km/h")
                st.metric(label="Dist. Alta Velocidade",
                          value=f"{extrair_valor(team_aver_df, ['DISTÂNCIA >19.8 KM/H'])} m")
                st.metric(label="Distância Sprint", value=f"{extrair_valor(team_aver_df, ['DISTÂNCIA >25.2 KM/H'])} m")
                st.metric(label="Nº Sprints", value=extrair_valor(team_aver_df, ['NºSPRINTS >25.2 KM/H', 'NºSPRINTS']))

            with col3:
                st.markdown("### 🚀 Acelerações")
                st.metric(label="Nº Acelerações",
                          value=extrair_valor(team_aver_df, ['NºACELERAÇÕES >3M/S²', 'NºACELERA']))
                st.metric(label="Distância Aceleração",
                          value=f"{extrair_valor(team_aver_df, ['DISTÂNCIA ACELERAÇÃO>3M/S²'])} m")
                st.metric(label="Nº Desacelerações", value=extrair_valor(team_aver_df, ['NºDESACELERAÇÕES <-3M/S²']))
                st.metric(label="Distância Desacel.",
                          value=f"{extrair_valor(team_aver_df, ['DISTÂNCIA DESACELERAÇÃO>3M/S²'])} m")

            with col4:
                st.markdown("### 🔋 Carga Interna/Externa")
                st.metric(label="Training Load", value=extrair_valor(team_aver_df, ['TRAINING LOAD']))
                st.metric(label="TLmax_5m", value=extrair_valor(team_aver_df, ['TLMAX_5MIN', 'TLMAX_5M']))
                st.metric(label="Dynamic Index", value=extrair_valor(team_aver_df, ['DYNAMIC INDEX']))
                st.metric(label="Distância Pot. Metabólica",
                          value=f"{extrair_valor(team_aver_df, ['DISTÂNCIA POTÊNCIA METABÓLICA >25.5 W/KG'])} m")
        else:
            st.warning("Linha 'Team Aver' não encontrada para esta data.")

        st.divider()
        st.subheader("Desempenho Geral do Elenco")
        df_elenco = df_filtrado[~df_filtrado['PLAYER'].astype(str).str.contains("Team Aver", case=False, na=False)]
        if not df_elenco.empty:
            df_elenco = df_elenco.loc[:, ~df_elenco.columns.duplicated()]
            df_elenco = df_elenco.drop(columns=['ATIVIDADE'], errors='ignore')
            st.dataframe(df_elenco, use_container_width=True, hide_index=True)

class AbaDesempenhoPorData:
    def __init__(self, df_completo):
        self.df_geral = df_completo

    def render(self):
        st.header("Evolução do Desempenho por Data (Média da Equipe)")

        df_team = self.df_geral[
            self.df_geral['PLAYER'].astype(str).str.contains("Team Aver", case=False, na=False)].copy()
        df_team = df_team.sort_values(by='DATA')

        if df_team.empty:
            st.warning("⚠️ Nenhuma linha de 'Team Average' localizada.")
            return

        df_team['DATA_STR'] = df_team['DATA'].dt.strftime('%d/%m/%Y')
        datas_disponiveis = df_team['DATA_STR'].unique().tolist()

        datas_sel = st.multiselect("Selecione as Datas para o Histórico", options=datas_disponiveis,
                                   default=datas_disponiveis, key="datas_evolucao")

        st.markdown("#### Selecione as Métricas de Interesse")
        metricas_reais = obter_colunas_exatas(df_team.columns)
        metricas_sel = []

        with st.expander("Mostrar / Esconder Métricas Físicas", expanded=True):
            cols_check = st.columns(3)
            for idx, metrica in enumerate(sorted(metricas_reais)):
                padrao_marcado = True if idx < 2 else False
                with cols_check[idx % 3]:
                    if st.checkbox(metrica, value=padrao_marcado, key=f"chk_met_{metrica}"):
                        metricas_sel.append(metrica)

        df_filtrado = df_team[df_team['DATA_STR'].isin(datas_sel)]
        if df_filtrado.empty or len(metricas_sel) == 0:
            st.info("💡 Selecione uma data e marque as métricas.")
            return

        st.divider()
        cols_grade = st.columns(2)
        for idx, metrica in enumerate(metricas_sel):
            with cols_grade[idx % 2]:
                st.markdown(f"#### Variação de: <span style='color:#32CD32;'>{metrica}</span>",
                            unsafe_allow_html=True)
                df_filtrado[metrica] = pd.to_numeric(df_filtrado[metrica], errors='coerce').fillna(0)

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_filtrado['DATA_STR'], y=df_filtrado[metrica], mode='lines+markers+text',
                    text=df_filtrado[metrica].map(lambda x: f"{int(x)}" if x.is_integer() else f"{round(x, 1)}"),
                    textposition="top center", line=dict(color='#32CD32', width=3),
                    marker=dict(size=8, color='#FFFFFF', line=dict(color='#32CD32', width=2))
                ))
                fig.update_layout(
                    height=240, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30,30,30,0.3)', font=dict(color='white', size=11),
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'), showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


class AbaDesempenhoIndividual:
    def __init__(self, df_completo, atleta):
        self.df_geral = df_completo
        self.atleta = atleta

    def render(self):
        st.header(f"📊 Análise Individual e Evolução: {self.atleta}")

        df_atleta = self.df_geral[self.df_geral['PLAYER'] == self.atleta].copy()
        df_atleta = df_atleta.sort_values(by='DATA')
        df_team = self.df_geral[
            self.df_geral['PLAYER'].astype(str).str.contains("Team Aver", case=False, na=False)].copy()
        df_team = df_team.sort_values(by='DATA')

        if df_atleta.empty:
            st.warning("Dados do atleta não encontrados.")
            return

        col_posicao = None
        for col in self.df_geral.columns:
            if col.upper() in ['POSIÇÃO', 'POSICAO', 'POSITION', 'POS']:
                col_posicao = col
                break

        posicao_atleta = None
        if col_posicao and not df_atleta[col_posicao].dropna().empty:
            posicao_atleta = str(df_atleta[col_posicao].iloc[0])

        df_atleta['DATA_STR'] = df_atleta['DATA'].dt.strftime('%d/%m/%Y')
        df_team['DATA_STR'] = df_team['DATA'].dt.strftime('%d/%m/%Y')
        datas_disponiveis = df_atleta['DATA_STR'].unique().tolist()

        datas_sel = st.multiselect("Selecione as Datas para o Histórico", options=datas_disponiveis,
                                   default=datas_disponiveis, key=f"datas_evolucao_{self.atleta}")

        st.markdown("#### Selecione as Métricas de Interesse")
        metricas_reais = obter_colunas_exatas(df_atleta.columns)
        metricas_sel = []

        with st.expander("Mostrar / Esconder Métricas Físicas", expanded=True):
            cols_check = st.columns(3)
            for idx, metrica in enumerate(sorted(metricas_reais)):
                padrao_marcado = True if idx < 2 else False
                with cols_check[idx % 3]:
                    if st.checkbox(metrica, value=padrao_marcado, key=f"chk_met_atl_{metrica}"):
                        metricas_sel.append(metrica)

        df_filtrado_atleta = df_atleta[df_atleta['DATA_STR'].isin(datas_sel)].copy()
        df_filtrado_team = df_team[df_team['DATA_STR'].isin(datas_sel)].copy()

        df_filtrado_posicao = pd.DataFrame()
        if posicao_atleta:
            df_mesma_pos = self.df_geral[(self.df_geral[col_posicao] == posicao_atleta) & (
                ~self.df_geral['PLAYER'].astype(str).str.contains("Team Aver", case=False, na=False))].copy()
            df_mesma_pos['DATA_STR'] = df_mesma_pos['DATA'].dt.strftime('%d/%m/%Y')
            df_mesma_pos_filt = df_mesma_pos[df_mesma_pos['DATA_STR'].isin(datas_sel)]
            if not df_mesma_pos_filt.empty:
                cols_numericas = df_mesma_pos_filt.select_dtypes(include=['number']).columns
                df_filtrado_posicao = df_mesma_pos_filt.groupby(['DATA', 'DATA_STR'])[
                    cols_numericas].mean().reset_index()
                df_filtrado_posicao = df_filtrado_posicao.sort_values(by='DATA')

        if df_filtrado_atleta.empty or len(metricas_sel) == 0:
            st.info("💡 Selecione pelo menos uma data e uma métrica.")
            return

        st.divider()
        if posicao_atleta:
            st.caption(f" Posição detectada: **{posicao_atleta}**")

        cols_grade = st.columns(2)
        for idx, metrica in enumerate(metricas_sel):
            with cols_grade[idx % 2]:
                st.markdown(f"#### <span style='color:#32CD32;'>{metrica}</span>", unsafe_allow_html=True)
                df_filtrado_atleta[metrica] = pd.to_numeric(df_filtrado_atleta[metrica], errors='coerce').fillna(0)

                fig = go.Figure()
                if not df_filtrado_team.empty and metrica in df_filtrado_team.columns:
                    df_filtrado_team[metrica] = pd.to_numeric(df_filtrado_team[metrica], errors='coerce').fillna(0)
                    fig.add_trace(
                        go.Scatter(x=df_filtrado_team['DATA_STR'], y=df_filtrado_team[metrica], mode='lines+markers',
                                   line=dict(color='rgba(128,128,128,0.5)', width=2, dash='dash'), name='Média Geral'))

                if not df_filtrado_posicao.empty and metrica in df_filtrado_posicao.columns:
                    fig.add_trace(go.Scatter(x=df_filtrado_posicao['DATA_STR'], y=df_filtrado_posicao[metrica],
                                             mode='lines+markers', line=dict(color='#1E90FF', width=2, dash='dot'),
                                             name=f'Média ({posicao_atleta})'))

                fig.add_trace(go.Scatter(
                    x=df_filtrado_atleta['DATA_STR'], y=df_filtrado_atleta[metrica], mode='lines+markers+text',
                    text=df_filtrado_atleta[metrica].map(lambda x: f"{int(x)}" if x.is_integer() else f"{round(x, 1)}"),
                    textposition="top center", line=dict(color='#32CD32', width=3),
                    marker=dict(size=8, color='#FFFFFF', line=dict(color='#32CD32', width=2)), name=self.atleta
                ))
                fig.update_layout(
                    height=240, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30,30,30,0.3)', font=dict(color='white', size=11),
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'), showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


class AbaComparacao:
    def __init__(self, df_partida, df_completo, atletas):
        self.df_p = df_partida
        self.df_f = df_completo
        self.atletas = atletas

    def render(self):
        df_p_clean = self.df_p.loc[:, ~self.df_p.columns.duplicated()]
        metricas_reais = obter_colunas_exatas(df_p_clean.columns)

        st.markdown("#### <b> Selecione as Métricas para Comparação</b>", unsafe_allow_html=True)
        metricas_sel = []

        with st.expander("Mostrar / Esconder Métricas Físicas", expanded=True):
            cols_check = st.columns(3)
            for idx, metrica in enumerate(sorted(metricas_reais)):
                padrao_marcado = True if idx < 3 else False
                with cols_check[idx % 3]:
                    if st.checkbox(metrica, value=padrao_marcado, key=f"chk_comp_met_{metrica}"):
                        metricas_sel.append(metrica)

        if len(metricas_sel) == 0:
            st.info("💡 Marque pelo menos uma métrica acima para gerar o gráfico.")
            return

        st.divider()
        nomes_formatados = " vs ".join(self.atletas)
        st.markdown(f"<h4 style='color: #C0C0C0; text-align: center;'>{nomes_formatados} <span style='font-size:14px; color:#888;'><br>(Média do Período Selecionado)</span></h4>", unsafe_allow_html=True)

        df_partida_plot = df_p_clean[df_p_clean['PLAYER'].isin(self.atletas)]
        if not df_partida_plot.empty:
            df_melt = df_partida_plot.melt(id_vars=['PLAYER'], value_vars=metricas_sel, var_name='Métrica', value_name='Valor')
            df_melt['Valor'] = pd.to_numeric(df_melt['Valor'], errors='coerce').fillna(0)

            # Agrupa os valores calculando a MÉDIA aritmética para o período selecionado.
            df_melt = df_melt.groupby(['PLAYER', 'Métrica'])['Valor'].mean().reset_index()

            cores_paleta = ['#32CD32', '#FFFFFF', '#1E90FF']
            mapa_cores = {}
            for i, atleta in enumerate(self.atletas):
                mapa_cores[atleta] = cores_paleta[i] if i < len(cores_paleta) else '#888888'

            fig_bar = px.bar(
                df_melt, x='Métrica', y='Valor', color='PLAYER',
                barmode='group', text_auto='.1f', color_discrete_map=mapa_cores
            )
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
                margin=dict(t=50, b=50), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_bar, use_container_width=True)