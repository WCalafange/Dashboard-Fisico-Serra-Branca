import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Análise de Desempenho")


class AbaDesempenho:
    METRICAS_POR_POSICAO = {
        'Zagueiro': ['ACOES', '% ACOES COM SUCESSO', 'FALTAS', 'FALTAS SOFRIDAS', 'PASSES PROGRESSIVOS',
                     '% PASSES PROGRESSIVOS CONCLUIDOS',
                     'DISPUTAS', '% DISPUTAS GANHAS', 'DESARMES REALIZADOS', '% DESARMES REALIZADOS COM SUCESSO',
                     'PERDA DA BOLA', 'RETOMADA DE POSSE',
                     'BOLA RECUPERADA'],
        'Lateral': ['ACOES', '% ACOES COM SUCESSO', 'FALTAS', 'FALTAS SOFRIDAS', 'PASSES PROGRESSIVOS',
                    '% PASSES PROGRESSIVOS CONCLUIDOS', 'CRUZAMENTOS',
                    'CHANCES CRIADAS', 'DISPUTAS', '% DISPUTAS GANHAS', 'DESARMES REALIZADOS',
                    '% DESARMES REALIZADOS COM SUCESSO', 'DRIBLES FEITOS',
                    '% DRIBLES FEITOS COM SUCESSO', 'PERDA DA BOLA', 'RETOMADA DE POSSE', 'BOLA RECUPERADA'],
        'Volante': ['ACOES', '% ACOES COM SUCESSO', 'FALTAS', 'FALTAS SOFRIDAS', 'PASSES PROGRESSIVOS',
                    '% PASSES PROGRESSIVOS CONCLUIDOS', 'DISPUTAS',
                    '% DISPUTAS GANHAS', 'DESARMES REALIZADOS', '% DESARMES REALIZADOS COM SUCESSO', 'ACOES ULTIMO 3º',
                    '% ACOES ULTIMO 3º COM SUCESSO', 'PASSES CHAVE',
                    'CHANCES CRIADAS', 'PERDA DA BOLA', 'RETOMADA DE POSSE', 'BOLA RECUPERADA'],
        'Meia': ['ACOES', '% ACOES COM SUCESSO', 'FINALIZACOES', 'FINALIZACOES NO ALVO', 'CHANCES DE GOL',
                 'CHANCES CRIADAS', 'FALTAS', 'FALTAS SOFRIDAS',
                 'PASSES PROGRESSIVOS', '% PASSES PROGRESSIVOS CONCLUIDOS', 'ACOES ULTIMO 3º',
                 '% ACOES ULTIMO 3º COM SUCESSO', 'DRIBLES FEITOS', '% DRIBLES FEITOS COM SUCESSO',
                 'PASSES CHAVE', 'RETOMADA DE POSSE', 'PERDA DA BOLA', 'DISPUTAS', '% DISPUTAS GANHAS',
                 'BOLA RECUPERADA'],
        'Extremo': ['ACOES', '% ACOES COM SUCESSO', 'ACOES ULTIMO 3º', '% ACOES ULTIMO 3º COM SUCESSO', 'FINALIZACOES',
                    'FINALIZACOES NO ALVO', 'CHANCES DE GOL',
                    'CHANCES CRIADAS', 'FALTAS', 'FALTAS SOFRIDAS', 'PASSES PROGRESSIVOS',
                    '% PASSES PROGRESSIVOS CONCLUIDOS', 'DRIBLES FEITOS',
                    '% DRIBLES FEITOS COM SUCESSO', 'PASSES CHAVE', 'CRUZAMENTOS', 'DISPUTAS', '% DISPUTAS GANHAS'],
        'Atacante': ['ACOES', '% ACOES COM SUCESSO', 'ACOES ULTIMO 3º', '% ACOES ULTIMO 3º COM SUCESSO', 'FINALIZACOES',
                     'FINALIZACOES NO ALVO',
                     'CHANCES DE GOL', 'CHANCES CRIADAS', 'FALTAS', 'FALTAS SOFRIDAS', 'PASSES PROGRESSIVOS',
                     '% PASSES PROGRESSIVOS CONCLUIDOS',
                     'DRIBLES FEITOS', '% DRIBLES FEITOS COM SUCESSO', 'DISPUTAS', '% DISPUTAS GANHAS', 'PASSES CHAVE']
    }

    def __init__(self, df_partida, df_completo, atleta):
        self.df_partida = df_partida
        self.df_completo = df_completo
        self.atleta = atleta

    def render(self):
        df_atleta = self.df_partida[self.df_partida['ATLETA'] == self.atleta]

        if not df_atleta.empty:
            st.header(f"📊 Análise Individual: {self.atleta}")
            posicao_atual = df_atleta['POSICAO'].iloc[0]

            # 1. Gráfico de Colunas Agrupadas
            st.header(f"Comparativo de Fundamentos: {posicao_atual}")
            metricas_especificas = self.METRICAS_POR_POSICAO.get(posicao_atual, ['INDICE'])
            metricas_especificas = [m for m in metricas_especificas if m in df_atleta.columns]

            dados_atleta = df_atleta[metricas_especificas].iloc[0].to_frame().reset_index()
            dados_atleta.columns = ['Métrica', 'Valor'];
            dados_atleta['Tipo'] = self.atleta

            dados_media = self.df_partida[self.df_partida['POSICAO'] == posicao_atual][
                metricas_especificas].mean().to_frame().reset_index()
            dados_media.columns = ['Métrica', 'Valor'];
            dados_media['Tipo'] = f"Média {posicao_atual}"

            df_comparativo = pd.concat([dados_atleta, dados_media])

            fig_colunas = px.bar(df_comparativo, x='Métrica', y='Valor', color='Tipo', barmode='group', text_auto='.1f',
                                 color_discrete_map={self.atleta: '#32CD32', f"Média {posicao_atual}": '#808080'})

            fig_colunas.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
            fig_colunas.update_layout(xaxis_tickangle=-45, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                      font=dict(color='white'))
            fig_colunas.update_xaxes(fixedrange=True)
            fig_colunas.update_yaxes(fixedrange=True)
            st.plotly_chart(fig_colunas, use_container_width=True, config={'displayModeBar': False}, key="grafico_barras_atleta")

            # 2. Evolução Temporal
            st.markdown("<h3 style='color: #C0C0C0;'>Evolução do índice</h3>", unsafe_allow_html=True)

            # Preparação dos dados
            df_historico = self.df_completo[self.df_completo['ATLETA'] == self.atleta].sort_values('DATA').copy()
            df_historico['DATA_STR'] = df_historico['DATA'].dt.strftime('%d/%m/%Y')

            df_media_hist = self.df_completo[
                (self.df_completo['POSICAO'] == posicao_atual) &
                (self.df_completo['DATA'].isin(df_historico['DATA']))
                ].groupby('DATA')['INDICE'].mean().reset_index()
            df_media_hist['DATA_STR'] = df_media_hist['DATA'].dt.strftime('%d/%m/%Y')

            fig_evolucao = px.line(
                df_historico,
                x='DATA_STR',
                y='INDICE',
                markers=True,
                color_discrete_sequence=['#32CD32']
            )

            fig_evolucao.add_scatter(
                x=df_media_hist['DATA_STR'],
                y=df_media_hist['INDICE'],
                mode='lines+markers',
                name="Média Posição",
                line=dict(color='gray', dash='dash')
            )

            # Ajustes de Layout e Remoção
            fig_evolucao.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(
                    type='category',
                    title_text='DATA',
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    fixedrange=True
                ),
                yaxis=dict(
                    title_text="ÍNDICE",
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    zerolinecolor='rgba(255, 255, 255, 0.2)',
                    fixedrange=True
                ),
                showlegend=True,
                margin=dict(t=10),
            )

            st.plotly_chart(fig_evolucao, use_container_width=True, key="grafico_evolucao_atleta")

            # --- SEÇÃO DE MINI GRÁFICOS DINÂMICOS (Cards) ---
            st.divider()
            st.subheader(f"Indicadores de Performance - {posicao_atual}")

            metricas_para_exibir = [m for m in metricas_especificas if m in df_historico.columns]
            cols = st.columns(2)

            for i, metrica in enumerate(metricas_para_exibir):
                with cols[i % 2]:
                    fig_mini = go.Figure()

                    # Formatação do rótulo
                    if metrica.startswith('%'):
                        texto_pontos = df_historico[metrica].apply(lambda x: f"{x:.1f}%")
                    else:
                        texto_pontos = df_historico[metrica].apply(lambda x: f"{x:.1f}")

                    # 1. Gráfico com valores na cor PRETA
                    fig_mini.add_trace(go.Scatter(
                        x=df_historico['DATA_STR'],
                        y=df_historico[metrica],
                        mode='lines+markers+text',
                        text=texto_pontos,
                        textposition="top center",
                        textfont=dict(size=11, color='black'),
                        line=dict(color='#B22222', width=3),
                        marker=dict(symbol='square', size=8, color='#B22222'),
                        name=metrica
                    ))

                    # 2. Configuração de Layout com Grades mais Escuras
                    fig_mini.update_layout(
                        title=dict(
                            text=f"<b>{metrica}</b>",
                            x=0.5,
                            xanchor='center',
                            font=dict(size=14, color='black')
                        ),
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        margin=dict(l=10, r=10, t=50, b=10),
                        height=230,
                        showlegend=False,

                        xaxis=dict(
                            showgrid=False,
                            tickfont=dict(size=10, color='gray'),
                            fixedrange=True
                        ),

                        yaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(0, 0, 0, 0.15)',
                            showticklabels=False,
                            zeroline=False,
                            range=[df_historico[metrica].min() * 0.7, df_historico[metrica].max() * 1.3],
                            fixedrange=True
                        ),
                    )

                    # Linha de média sutil
                    valor_medio = df_historico[metrica].mean()
                    fig_mini.add_hline(y=valor_medio, line_dash="dot", line_color="rgba(0, 0, 0, 0.1)", line_width=1)

                    st.plotly_chart(fig_mini, use_container_width=True, config={'displayModeBar': False}, key=f"mini_{metrica}")

            # 5. Histórico Completo
            st.divider()
            st.subheader(f"Dados das Partidas Disputadas por {self.atleta}")

            df_display = df_historico.copy()
            df_display['DATA'] = df_display['DATA_STR']  # Usa a data já formatada acima
            colunas_remover = ['NOME', 'ATLETA', 'POSICAO']
            df_display = df_display.drop(columns=colunas_remover, errors='ignore')

            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.warning("Dados do atleta não encontrados.")


class AbaEquipe:
    def __init__(self, df_completo):
        # Recebemos o dataframe total para filtrar dentro da aba
        self.df_geral = df_completo

    def render(self):
        st.header("Comparativo da Equipe")

        # --- FILTROS EXCLUSIVOS DA ABA ---
        f1, f2, f3 = st.columns(3)

        with f1:
            locais = ["Todos"] + sorted(self.df_geral['LOCAL'].unique().tolist())
            local_sel = st.selectbox("Filtrar Local", locais, key="filtro_local_aba")

        with f2:
            advs = ["Todos"] + sorted(self.df_geral['ADVERSARIO'].unique().tolist())
            adv_sel = st.selectbox("Filtrar Adversário", advs, key="filtro_adv_aba")

        with f3:
            datas = ["Todas"] + sorted(self.df_geral['DATA'].dt.strftime('%d/%m/%Y').unique().tolist())
            data_sel = st.selectbox("Filtrar Data", datas, key="filtro_data_aba")

        # --- LÓGICA DE FILTRAGEM ---
        df_filtrado = self.df_geral.copy()

        if local_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado['LOCAL'] == local_sel]
        if adv_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado['ADVERSARIO'] == adv_sel]
        if data_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado['DATA'].dt.strftime('%d/%m/%Y') == data_sel]

        if not df_filtrado.empty:
            df_tab = df_filtrado.copy()
            df_tab['DATA'] = df_tab['DATA'].dt.strftime('%d/%m/%Y')

            tabela_pivot = df_tab.pivot_table(
                index=['LOCAL', 'DATA', 'ADVERSARIO', 'POSICAO'],
                values=['INDICE', 'ACOES', '% ACOES COM SUCESSO', 'DISPUTAS', '% DISPUTAS GANHAS', 'PERDA DA BOLA',
                                                                     'RETOMADA DE POSSE', 'BOLA RECUPERADA'],
                aggfunc='mean'
            )

            # Reordenar para o ÍNDICE vir logo após POSIÇÃO
            colunas_ordem = ['INDICE', 'ACOES', '% ACOES COM SUCESSO', 'DISPUTAS', '% DISPUTAS GANHAS', 'PERDA DA BOLA',
                                                                     'RETOMADA DE POSSE', 'BOLA RECUPERADA']
            tabela_pivot = tabela_pivot.reindex(columns=colunas_ordem)

            styled_df = tabela_pivot.style.background_gradient(
                cmap='RdYlGn',
                subset=['INDICE']
            ).format(precision=1)

            st.dataframe(styled_df, use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")


        #Grafico de colunas
        metric_pos = st.selectbox("Desempenho médio das posições por métrica", ['INDICE', 'ACOES', '% ACOES COM SUCESSO', 'DISPUTAS',
                                                                     '% DISPUTAS GANHAS', 'PERDA DA BOLA',
                                                                     'RETOMADA DE POSSE', 'BOLA RECUPERADA'])
        df_posicoes = self.df_geral.groupby('POSICAO')[metric_pos].mean().sort_values(ascending=False).reset_index()
        fig_pos = px.bar(df_posicoes, x='POSICAO', y=metric_pos, color="POSICAO",
             # Definir a ordem exata das posições com as cores:
             color_discrete_map={
                 'Lateral': '#44FFBB',  # Azul Piscina Claro
                 'Zagueiro': '#33CCFF',     # Azul Céu
                 'Meia': '#FFD700',  # Ouro Sutil
                 'Atacante': '#FF5555', # Vermelho Suave
                 'Extremo': '#DDA0DD',  # Ameixa
                 'Volante': '#99FF33'  # Lima Sutil)
             }
                         )
        fig_pos.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True)
        )
        st.plotly_chart(fig_pos)


class AbaComparacao:
    METRICAS = AbaDesempenho.METRICAS_POR_POSICAO

    def __init__(self, df_partida, df_completo, atleta1, atleta2, posicao):
        self.df_p = df_partida
        self.df_f = df_completo
        self.a1 = atleta1
        self.a2 = atleta2
        self.pos = posicao

    def render(self):
        # 1. Filtra todas as métricas configuradas para a posição
        metricas_alvo = [m for m in self.METRICAS.get(self.pos, []) if m in self.df_f.columns]

        # --- GRÁFICO DE BARRAS ---
        st.markdown(
            f"<h3 style='color: #C0C0C0; text-align: center;'>Comparativo na Partida: {self.a1} vs {self.a2}</h3>",
            unsafe_allow_html=True)

        df_partida_plot = self.df_p[self.df_p['ATLETA'].isin([self.a1, self.a2])]
        if not df_partida_plot.empty:
            df_melt = df_partida_plot.melt(id_vars=['ATLETA'], value_vars=metricas_alvo, var_name='Métrica',
                                           value_name='Valor')

            fig_bar = px.bar(
                df_melt, x='Métrica', y='Valor', color='ATLETA',
                barmode='group', text_auto='.1f',
                color_discrete_map={self.a1: '#32CD32', self.a2: '#FFFFFF'}
            )
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(t=50, b=50),  # Espaço para o título não bater nas barras
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title=None)
            )
            st.plotly_chart(fig_bar, use_container_width=True, key="bar_partida_final", config={'staticPlot': True})

        st.divider()

        # --- MINI GRÁFICOS DE EVOLUÇÃO  ---
        st.markdown(f"<h3 style='color: #C0C0C0; text-align: center;'>Comparação Histórica</h3>", unsafe_allow_html=True)

        df_hist = self.df_f[self.df_f['ATLETA'].isin([self.a1, self.a2])].copy()
        df_hist = df_hist.sort_values('DATA')
        df_hist['DATA_STR'] = df_hist['DATA'].dt.strftime('%d/%m')

        cols_graf = st.columns(2)
        for i, metrica in enumerate(metricas_alvo):
            with cols_graf[i % 2]:
                fig = px.line(
                    df_hist, x='DATA_STR', y=metrica, color='ATLETA',
                    markers=True, title=metrica,
                    color_discrete_map={self.a1: '#32CD32', self.a2: '#FFFFFF'}
                )

                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'), height=280,
                    margin=dict(l=10, r=10, t=100, b=40),
                    title=dict(x=0.5, y=0.85, xanchor='center', yanchor='top'),
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.1,
                        xanchor="center", x=0.5, title=None, font=dict(size=10)
                    ),
                    # Desativa o clique duplo e o arraste
                    dragmode=False,
                    clickmode='none'
                )

                # Impede o Zoom
                fig.update_xaxes(showgrid=False, title=None, fixedrange=True)
                fig.update_yaxes(showgrid=True, gridcolor='#333', title=None, fixedrange=True)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key=f"mini_static_{metrica}",
                    config={
                        'staticPlot': True,  # Remove botões
                        'doubleClick': 'reset',  # Desativa reação ao clique duplo
                        'displayModeBar': False  # Esconde a barra de ferramentas
                    }
                )