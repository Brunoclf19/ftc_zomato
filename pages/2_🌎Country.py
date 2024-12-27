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

st.set_page_config(page_title='País', page_icon='🌎', layout='wide')

#-------------------------------------------------------------------------------
# Funções de apoio e gráficos
#-------------------------------------------------------------------------------

def calculate_metrics(df):
    return {
        "paises_unicos": len(df['country_name'].unique()),
        "cidades_unicas": df['city'].nunique(),
        "restaurantes_totais": df['restaurant_id'].nunique()
    }

def create_bar_chart(dataframe, x, y, text, title, labels):
    fig = px.bar(dataframe, x=x, y=y, text=text, title=title, labels=labels)
    fig.update_traces(textposition='outside')
    return fig

def create_summary_table(*dataframes):
    summary = dataframes[0]
    for df in dataframes[1:]:
        summary = pd.merge(summary, df, on='country_name')
    return summary

def calculate_country_stats(df):
    country_stats = df.groupby('country_name').agg(
        total_votes=('aggregate_rating', 'sum'),
        unique_restaurants=('restaurant_id', 'nunique')
    )
    country_stats['media_por_restaurantes'] = country_stats['total_votes'] / country_stats['unique_restaurants']
    return country_stats['media_por_restaurantes'].reset_index().rename(columns={'media_por_restaurantes': 'Média de Avaliações'})

def preprocess_country_data(df):
    paises_cidades = df.groupby('country_name')['city'].nunique().reset_index().rename(columns={'city': 'Cidades'})
    paises_restaurantes = df.groupby('country_name')['restaurant_id'].count().reset_index().rename(columns={'restaurant_id': 'Restaurantes'})
    paises_tipos_culinaria = df.groupby('country_name')['cuisines'].nunique().reset_index().rename(columns={'cuisines': 'Tipos de Culinária'})
    paises_avaliacoes = df.groupby('country_name')['restaurant_id'].count().reset_index().rename(columns={'restaurant_id': 'Avaliações'})
    paises_media_avaliacoes = calculate_country_stats(df).round(2)
    paises_media_notas = df.groupby('country_name')['aggregate_rating'].mean().reset_index().rename(columns={'aggregate_rating': 'Nota Média'})
    paises_media_preco = df.groupby('country_name').agg(
        Média_Preço_para_Dois=('average_cost_for_two', 'mean')
    ).sort_values(by='Média_Preço_para_Dois', ascending=False).reset_index().round(2)

    return (
        paises_cidades,
        paises_restaurantes,
        paises_tipos_culinaria,
        paises_avaliacoes,
        paises_media_avaliacoes,
        paises_media_notas,
        paises_media_preco
    )

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
df1 = df1[df1['country_name'].isin(country_option)]
df1 = df1[df1['aggregate_rating'].between(rating_slider[0], rating_slider[1])]
st.sidebar.download_button("Download dados", data=df1.to_csv(index=False), file_name='dados_tratados.csv', mime='text/csv')

#-------------------------------------------------------------------------------
# Dashboard - Países
#-------------------------------------------------------------------------------

# Títulos
st.header("Visão por País")
st.subheader("Exploração dos Dados de Restaurantes por País")
st.markdown("Nesta seção, exploramos os dados agrupados por países, fornecendo insights como quantidade de cidades, restaurantes e métricas relacionadas.")

# Métricas Gerais
metrics = calculate_metrics(df1)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🌍 Países Únicos", value=metrics['paises_unicos'])
with col2:
    st.metric(label="🏙️ Cidades Registradas", value=metrics['cidades_unicas'])
with col3:
    st.metric(label="🍴 Restaurantes Totais", value=metrics['restaurantes_totais'])

# Processar dados por país
(
    paises_cidades,
    paises_restaurantes,
    paises_tipos_culinaria,
    paises_avaliacoes,
    paises_media_avaliacoes,
    paises_media_notas,
    paises_media_preco
) = preprocess_country_data(df1)

# Gráficos
st.markdown("### Top 10 Países com Mais Cidades Registradas")
fig_cidades = create_bar_chart(paises_cidades.sort_values(by='Cidades', ascending=False).head(10), x='country_name', y='Cidades', text='Cidades', title="Top 10 Países", labels={'country_name': 'País', 'Cidades': 'Quantidade de Cidades'})
st.plotly_chart(fig_cidades, use_container_width=True)

st.markdown("### Top 10 Países com Mais Restaurantes Registrados")
fig_restaurantes = create_bar_chart(paises_restaurantes.sort_values(by='Restaurantes', ascending=False).head(10), x='country_name', y='Restaurantes', text='Restaurantes', title="Top 10 Restaurantes", labels={'country_name': 'País', 'Restaurantes': 'Quantidade de Restaurantes'})
st.plotly_chart(fig_restaurantes, use_container_width=True)

st.markdown("### Top 10 Países com Maior Média de Avaliações")
fig_avaliacoes = create_bar_chart(paises_media_avaliacoes.sort_values(by='Média de Avaliações', ascending=False).head(10), x='country_name', y='Média de Avaliações', text='Média de Avaliações', title="Top 10 Avaliações", labels={'country_name': 'País', 'Média de Avaliações': 'Média de Avaliações'})
st.plotly_chart(fig_avaliacoes, use_container_width=True)

st.markdown("### Top 10 Países com Maior Média de Preço para Dois")
fig_preco = create_bar_chart(paises_media_preco.sort_values(by='Média_Preço_para_Dois', ascending=False).head(10), x='country_name', y='Média_Preço_para_Dois', text='Média_Preço_para_Dois', title="Top 10 Preços", labels={'country_name': 'País', 'Média_Preço_para_Dois': 'Média Preço para Dois'})
st.plotly_chart(fig_preco, use_container_width=True)

# Resumo por País
st.markdown("### Resumo por País")
resumo = create_summary_table(paises_cidades, paises_restaurantes, paises_tipos_culinaria, paises_avaliacoes, paises_media_notas, paises_media_preco)
st.dataframe(resumo, use_container_width=True)
