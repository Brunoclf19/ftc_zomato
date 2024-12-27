from haversine import haversine
import pandas as pd
import numpy as np
import plotly.express as px
import folium
import streamlit as st
from streamlit_folium import st_folium
from PIL import Image
import datetime as datetime
import inflection
from folium.plugins import MarkerCluster

st.set_page_config(page_title='Tipos de Culinária', page_icon='🍽️', layout='wide')

#-------------------------------------------------------------------------------
# Funções de apoio e gráficos
#-------------------------------------------------------------------------------

def calculate_cuisine_metrics(df):
    return {
        "tipos_culinaria": df['cuisines'].nunique(),
        "restaurantes_totais": df['restaurant_id'].nunique(),
        "media_geral_avaliacoes": round(df['aggregate_rating'].mean(), 2)
    }

def create_bar_chart(dataframe, x, y, text, title, labels):
    fig = px.bar(dataframe, x=x, y=y, text=text, title=title, labels=labels)
    fig.update_traces(textposition='outside')
    return fig

def create_summary_table(*dataframes):
    summary = dataframes[0]
    for df in dataframes[1:]:
        summary = pd.merge(summary, df, on='cuisines')
    return summary

def preprocess_cuisine_data(df):
    maior_menor_avaliacao = df.groupby(['cuisines', 'restaurant_name'])['aggregate_rating'].mean().reset_index()
    maior_avaliacao = maior_menor_avaliacao.sort_values(['cuisines', 'aggregate_rating'], ascending=[True, False])
    menor_avaliacao = maior_menor_avaliacao.sort_values(['cuisines', 'aggregate_rating'], ascending=[True, True])

    custo_culinaria = df.groupby('cuisines')['average_cost_for_two'].mean().reset_index()
    custo_culinaria = custo_culinaria.sort_values(by='average_cost_for_two', ascending=False).round(2)

    nota_culinaria = df[df['cuisines'] != "Others"].groupby('cuisines')['aggregate_rating'].mean().reset_index()
    nota_culinaria = nota_culinaria.sort_values(by='aggregate_rating', ascending=False).round(2)

    online_delivery = df[(df['is_delivering_now'] == 1) & (df['has_online_delivery'] == 1)]
    mais_online_entregas = online_delivery.groupby('cuisines')['restaurant_id'].count().reset_index()
    mais_online_entregas = mais_online_entregas.sort_values(by='restaurant_id', ascending=False)

    return maior_avaliacao, menor_avaliacao, custo_culinaria, nota_culinaria, mais_online_entregas

#-------------------------------------------------------------------------------
# Função para limpar e carregar os dados
#-------------------------------------------------------------------------------

def country_name(country_id):
    COUNTRIES = {
        1: "India",
        14: "Australia",
        30: "Brazil",
        37: "Canada",
        94: "Indonesia",
        148: "New Zeland",
        162: "Philippines",
        166: "Qatar",
        184: "Singapure",
        189: "South Africa",
        191: "Sri Lanka",
        208: "Turkey",
        214: "United Arab Emirates",
        215: "England",
        216: "United States of America",
    }
    return COUNTRIES.get(country_id, "Unknown")

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

def load_and_clean_data(file_path):
    df = pd.read_csv(file_path)
    df['Country Name'] = df['Country Code'].apply(country_name)
    df = rename_columns(df)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    if "cuisines" in df.columns:
        df["cuisines"] = df["cuisines"].apply(lambda x: x.split(",")[0] if isinstance(x, str) else x)
    return df

#-------------------------------------------------------------------------------
# Carregar e processar os dados
#-------------------------------------------------------------------------------

#file_path = r'C:\Users\Giovanna\OneDrive\Documentos\repos\FTC_projeto_aluno\dataset\zomato.csv'
# df = pd.read_csv('dataset\\zomato.csv')
df1 = load_and_clean_data('dataset/zomato.csv')

# Sidebar
image = Image.open('logo-filtro.jpg')
st.sidebar.image(image, width=120)

country_option = st.sidebar.multiselect("Em qual país você quer encontrar um restaurante?", df1['country_name'].unique(), default=df1['country_name'].unique())
rating_slider = st.sidebar.slider("Qual classificação de restaurante você deseja ver?", min_value=0.0, max_value=5.0, value=(0.0, 5.0), step=0.1, format="%.1f")
culinaria_option = st.sidebar.multiselect("Escolha os tipos de culinária para análise:", options=df1['cuisines'].unique(), default=df1['cuisines'].unique())

df1 = df1[df1['country_name'].isin(country_option)]
df1 = df1[df1['aggregate_rating'].between(rating_slider[0], rating_slider[1])]
df1 = df1[df1['cuisines'].isin(culinaria_option)]

st.sidebar.download_button("Download dados", data=df1.to_csv(index=False), file_name='dados_tratados.csv', mime='text/csv')

#-------------------------------------------------------------------------------
# Dashboard - Culinária
#-------------------------------------------------------------------------------

# Títulos
st.header("Visão por Tipos de Culinária")
st.subheader("Exploração dos Dados de Restaurantes por Tipo de Culinária")
st.markdown("Nesta página, exploramos métricas e insights relacionados aos tipos de culinária oferecidos pelos restaurantes cadastrados.")

# Métricas Gerais
metrics = calculate_cuisine_metrics(df1)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🍴 Total de Tipos de Culinária", value=metrics['tipos_culinaria'])
with col2:
    st.metric(label="🏙️ Total de Restaurantes", value=metrics['restaurantes_totais'])
with col3:
    st.metric(label="🌟 Média Geral de Avaliações", value=metrics['media_geral_avaliacoes'])

# Processar dados por tipo de culinária
(
    maior_avaliacao,
    menor_avaliacao,
    custo_culinaria,
    nota_culinaria,
    mais_online_entregas
) = preprocess_cuisine_data(df1)

# Tabela para maior e menor avaliação
st.markdown("### Restaurantes com as Maiores e Menores Avaliações por Tipo de Culinária")
col1, col2 = st.columns(2)
with col1:
    st.markdown("##### Maiores Avaliações")
    st.dataframe(maior_avaliacao.groupby('cuisines').head(1).reset_index(drop=True))
with col2:
    st.markdown("##### Menores Avaliações")
    st.dataframe(menor_avaliacao.groupby('cuisines').head(1).reset_index(drop=True))

# Tabela para maior custo médio, maior nota média e mais entregas
st.markdown("### Outros Insights")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("##### Maior Valor Médio de Prato para Dois")
    st.dataframe(custo_culinaria.head(1))
with col2:
    st.markdown("##### Maior Nota Média")
    st.dataframe(nota_culinaria.head(1))
with col3:
    st.markdown("##### Mais Restaurantes com Ecommerce")
    st.dataframe(mais_online_entregas.head(1))

# Gráfico: Distribuição dos Tipos de Culinária
st.markdown("### Distribuição dos Tipos de Culinária")
culinaria_distribuicao = df1['cuisines'].value_counts().reset_index()
culinaria_distribuicao.columns = ['Tipo de Culinária', 'Quantidade']
fig_culinaria = create_bar_chart(
    culinaria_distribuicao.head(10),
    x='Tipo de Culinária',
    y='Quantidade',
    text='Quantidade',
    title="Top 10 Tipos de Culinária",
    labels={'Tipo de Culinária': 'Tipo de Culinária', 'Quantidade': 'Quantidade de Restaurantes'}
)
st.plotly_chart(fig_culinaria, use_container_width=True)
