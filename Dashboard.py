# Importando as Bibliotecas necessárias 

import streamlit as st
import requests 
import pandas as pd
import plotly.express as px 

# Configurando o layout padrão do aplicativo 

st.set_page_config(layout = 'wide')

# Definindo as Funções

# [01] Função para Formatar Números

def fomarta_numero(valor, prefixo = ''):
    if valor < 1000:
        return f'{prefixo} {valor: .2f} {""}'
    elif valor >= 10000:
        valor = valor/1000000
        return f'{prefixo} {valor: .2f} {"Milhões"}'
    else: 
        valor = valor/1000
        return f'{prefixo} {valor: .2f} {"Mil"}'
    

# Iniciando o Streamlit

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

# Lendo os Dados 

url = 'https://labdados.com/produtos'

# Criando Estrutura para Filtros que São Possíveis Antes de Executar a Requisição

regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul'] # Lista que armazena os valores possíveis

st.sidebar.title('Filtros') # Componente do Streamlit para criar uma side bar na tela
regiao = st.sidebar.selectbox('Escolha a Região', regioes) # Componente selectbox que será adicionado à side bar para que o usuário selecione os filtros 

if regiao == 'Brasil': # Condicional para não fazer filtro se a opção escolhida for Brasil
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de Todo o Período', value = True) # Componente checkbox que será adicionado à side bar para que o usuário selecione os anos
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023) 
    
# Criando dicionário para armazenar os valores selecionados para o usuário para que possa modificar a requisição

query_string = {'regiao':regiao.lower(), 'ano': ano}

# Realizando a Requisição, Coletando os Dados e Armazenando em um DataFrame

response = requests.get(url, params = query_string) # Fazendo requisição para a API. Requests > Jason > Dataframe
dados = pd.DataFrame.from_dict(response.json()) #Transformando a requisição em um Jason e um Jason em um Dataframe
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y') # Transformando os dados da coluna data para o formato datetime

# Criando Filtros Pós Requisição

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# Tabelas

# [01] Tabelas de Receita
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values(by = 'Preço', ascending = False)

receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
coordenadas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']]
receita_estados = coordenadas_estados.merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

# [02] Tabelas de Quantidade de Vendas

# [03] Tabelas de Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

# Gráficos
# [01] Gráfico de Mapa
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita por Estado')

# [02] Gráfico de Linhas
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita Mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

# [03] Gráfico de Barras Receita por Estado
fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'TOP 5 Estados com Maior Receita',
                             )

fig_receita_estados.update_layout(yaxis_title = 'Receita')

# [04] Gráfico de Barras Receita por Categorias
fig_receita_categorias = px.bar(receita_categorias,
                             text_auto = True,
                             title = 'Receita por Categoria de Produtos',
                             )

fig_receita_categorias.update_layout(yaxis_title = 'Receita')

# Visualização Streamlit: Inserindo métricas no Dashboard em colunas

# [01] Construindo Abas para Organizar as Páginas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

# Aba 1 - Receita
with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', fomarta_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with coluna2:
        st.metric('Quantidade de Vendas', fomarta_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)


# Aba 2 - Vendas
with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', fomarta_numero(dados['Preço'].sum(), 'R$'))
        
    with coluna2:
        st.metric('Quantidade de Vendas', fomarta_numero(dados.shape[0]))
        

# Aba 3 - Vendedores
with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', fomarta_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} Vendedores (Receita)')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de Vendas', fomarta_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} Vendedores (Quantidade de Vendas)')
        st.plotly_chart(fig_vendas_vendedores)