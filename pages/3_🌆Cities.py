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

st.set_page_config(page_title='Cidade', page_icon='🏙️', layout='wide')

#-------------------------------------------------------------------------------
# Funções de apoio e gráficos
#-------------------------------------------------------------------------------

def calculate_city_metrics(df):
    return {
        "cidades_unicas": len(df['city'].unique()),
        "restaurantes_totais": df['restaurant_id'].nunique(),
        "tipos_culinaria": df['cuisines'].nunique()
    }

def create_bar_chart(dataframe, x, y, text, title, labels):
    fig = px.bar(dataframe, x=x, y=y, text=text, title=title, labels=labels)
    fig.update_traces(textposition='outside')
    return fig

def create_summary_table(*dataframes):
    summary = dataframes[0]
    for df in dataframes[1:]:
        summary = pd.merge(summary, df, on='city')
    return summary

def preprocess_city_data(df):
    cidades_restaurantes = df.groupby('city')['restaurant_id'].nunique().reset_index().rename(columns={'restaurant_id': 'Restaurantes'})
    cidades_tipos_culinaria = df.groupby('city')['cuisines'].nunique().reset_index().rename(columns={'cuisines': 'Tipos de Culinária'})
    cidades_custo_medio = df.groupby('city')['average_cost_for_two'].mean().reset_index().rename(columns={'average_cost_for_two': 'Custo Médio para Dois'}).round(2)
    cidades_avaliacoes = df.groupby('city')['votes'].sum().reset_index().rename(columns={'votes': 'Avaliações'})
    return cidades_restaurantes, cidades_tipos_culinaria, cidades_custo_medio, cidades_avaliacoes

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
city_option = st.sidebar.multiselect("Escolha as cidades para análise:", options=df1['city'].unique(), default=df1['city'].unique())

df1 = df1[df1['country_name'].isin(country_option)]
df1 = df1[df1['aggregate_rating'].between(rating_slider[0], rating_slider[1])]
df1 = df1[df1['city'].isin(city_option)]

st.sidebar.download_button("Download dados", data=df1.to_csv(index=False), file_name='dados_tratados.csv', mime='text/csv')

#-------------------------------------------------------------------------------
# Dashboard - Cidades
#-------------------------------------------------------------------------------

# Títulos
st.header("Visão por Cidade")
st.subheader("Exploração dos Dados de Restaurantes por Cidade")
st.markdown("Nesta página, exploramos os dados agrupados por cidades, analisando os restaurantes, tipos de culinária e outras métricas relevantes.")

# Métricas Gerais
metrics = calculate_city_metrics(df1)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🏙️ Cidades Únicas", value=metrics['cidades_unicas'])
with col2:
    st.metric(label="🍴 Restaurantes Totais", value=metrics['restaurantes_totais'])
with col3:
    st.metric(label="🌍 Tipos de Culinária", value=metrics['tipos_culinaria'])

# Processar dados por cidade
(
    cidades_restaurantes,
    cidades_tipos_culinaria,
    cidades_custo_medio,
    cidades_avaliacoes
) = preprocess_city_data(df1)

# Gráficos
st.markdown("### Top 10 Cidades com Mais Restaurantes Registrados")
fig_restaurantes = create_bar_chart(cidades_restaurantes.sort_values(by='Restaurantes', ascending=False).head(10), x='city', y='Restaurantes', text='Restaurantes', title="Top 10 Restaurantes", labels={'city': 'Cidade', 'Restaurantes': 'Quantidade de Restaurantes'})
st.plotly_chart(fig_restaurantes, use_container_width=True)

st.markdown("### Top 10 Cidades com Maior Custo Médio para Dois")
fig_custo = create_bar_chart(cidades_custo_medio.sort_values(by='Custo Médio para Dois', ascending=False).head(10), x='city', y='Custo Médio para Dois', text='Custo Médio para Dois', title="Top 10 Custos", labels={'city': 'Cidade', 'Custo Médio para Dois': 'Custo Médio para Dois'})
st.plotly_chart(fig_custo, use_container_width=True)

st.markdown("### Top 10 Cidades com Mais Tipos de Culinária")
fig_culinaria = create_bar_chart(cidades_tipos_culinaria.sort_values(by='Tipos de Culinária', ascending=False).head(10), x='city', y='Tipos de Culinária', text='Tipos de Culinária', title="Top 10 Tipos de Culinária", labels={'city': 'Cidade', 'Tipos de Culinária': 'Quantidade de Tipos de Culinária'})
st.plotly_chart(fig_culinaria, use_container_width=True)

# Resumo por Cidade
st.markdown("### Resumo por Cidade")
resumo = create_summary_table(cidades_restaurantes, cidades_tipos_culinaria, cidades_custo_medio, cidades_avaliacoes)
st.dataframe(resumo, use_container_width=True)
