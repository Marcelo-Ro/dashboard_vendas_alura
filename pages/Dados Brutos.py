# Importando as Bibliotecas necessárias 

import streamlit as st
import requests 
import pandas as pd
import time 

# Criando Funções para Fazer Download da Base de Dados Conforme Filtros Aplicados

@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo Baixado com Sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty()

# Iniciando o Streamlit

st.title('Dados Brutos')

# Lendo os Dados 

url = 'https://labdados.com/produtos'

# Realizando a Requisição, Coletando os Dados e Armazenando em um DataFrame

response = requests.get(url) # Fazendo requisição para a API. Requests > Jason > Dataframe
dados = pd.DataFrame.from_dict(response.json()) # Transformando a requisição em um Jason e um Jason em um Dataframe
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y') # Transformando os dados da coluna data para o formato datetime

# Criando Elementos de Filtros para Seleção pelo Usuário

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as Colunas Desejadas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')

with st.sidebar.expander('Nome do Produto'):
    produtos = st.multiselect('Selecione os Produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Categoria do Produto'):
    categoria = st.multiselect('Selecione as Categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

with st.sidebar.expander('Preço do Produto'):
    preco = st.slider('Selecione o Preço', 0, 5000, (0, 5000))

with st.sidebar.expander('Frete da Venda'):
    frete = st.slider('Selecione o Preço', 0, 250, (0, 250))
    
with st.sidebar.expander('Data da Compra'):
    data_compra = st.sidebar.date_input('Selecione a Data:', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione os Vendedores:', dados['Vendedor'].unique(), dados['Vendedor'].unique())

with st.sidebar.expander('Local da Compra'):
    local_compra = st.multiselect('Selecione o Local da Compra:', dados['Local da compra'].unique(), dados['Local da compra'].unique())

with st.sidebar.expander('Avaliação da Compra'):
    avaliacao = st.slider('Selecione a Avaliação da Compra:', 1, 5, value = (1, 5))

with st.sidebar.expander('Tipo de Pagamento'):
    tipo_pagamento = st.multiselect('Selecione o Tipo de Pagamento:', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

with st.sidebar.expander('Quantidade de Parcelas'):
    qtd_parcelas = st.slider('Selecione a Quantidade de Parcelas', 1, 24, value = (1, 24))


# Filtrando o DataFrame Pandas de Acordo com Os Filtros Selecionados pelo Usuário

query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

# Mostrando os Dados na Tela do App Streamlit

st.dataframe(dados_filtrados)

# Mostrando a Quantidade de Linhas e Colunas que Foram Geradas com os Filtros

st.markdown(f'A Tabela Possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

# Adicionando o Botão de Download

st.markdown('Escreva o Nome para o Arquivo')

coluna1, coluna2 = st.columns(2)

with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'

with coluna2:
    st.download_button('Fazer Download da Tabela em csv', data = converte_csv(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)
