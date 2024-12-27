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

st.set_page_config(page_title='Geral', page_icon='🎲', layout='wide')

#-------------------------------------------------------------------------------
# Funções de apoio e gráficos
#-------------------------------------------------------------------------------

def create_bar_chart(dataframe, x, y, title, text, labels):
    fig = px.bar(dataframe, x=x, y=y, text=text, title=title, labels=labels)
    fig.update_traces(textposition='outside')
    return fig

def create_pie_chart(dataframe, values, names, title):
    fig = px.pie(dataframe, values=values, names=names, title=title)
    return fig

def create_map(dataframe):
    m = folium.Map(location=[0, 0], zoom_start=2)
    marker_cluster = MarkerCluster().add_to(m)

    for index, row in dataframe.iterrows():
        folium.Marker(location=[row['latitude'], row['longitude']],
                      popup=f"<b>{row['restaurant_name']}</b><br>\n{row['city']} - {row['country_name']}<br>\nAvaliação: {row['aggregate_rating']}\n", 
                      tooltip=row['restaurant_name']).add_to(marker_cluster)
    return m

#-------------------------------------------------------------------------------
# Função para limpar e carregar os dados
#-------------------------------------------------------------------------------

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

COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}

def country_name(country_id):
    return COUNTRIES.get(country_id, "Unknown")

def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

def color_name(color_code):
    return COLORS.get(color_code, "unknown")

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
    # Carrega o dataset
    df = pd.read_csv(file_path)

    # Adiciona o nome do país
    df['Country Name'] = df['Country Code'].apply(country_name)

    # Adiciona o tipo de preço
    df['Price_Tye'] = df['Price range'].apply(create_price_tye)

    # Adiciona o nome da cor
    df['Color_Name'] = df['Rating color'].apply(color_name)

    # Renomeia as colunas
    df = rename_columns(df)

    # Remove valores ausentes e reseta o índice
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Simplifica a coluna "cuisines" para apenas o primeiro tipo de culinária
    if "cuisines" in df.columns:
        df["cuisines"] = df["cuisines"].apply(lambda x: x.split(",")[0] if isinstance(x, str) else x)

    return df

#-------------------------------------------------------------------------------
# Carregar e processar os dados
#-------------------------------------------------------------------------------

#file_path = r'C:\Users\Giovanna\OneDrive\Documentos\repos\FTC_projeto_aluno\dataset\zomato.csv'
# df = pd.read_csv('dataset\\zomato.csv')
df1 = load_and_clean_data('dataset/zomato.csv')

image = Image.open('logo-filtro.jpg')
st.sidebar.image(image, width=120)

# Filtros - país
country_option = st.sidebar.multiselect(
    "Em qual país você quer encontrar um restaurante?",
    df1['country_name'].unique(),  # Garantir que 'country_name' exista
    default=df1['country_name'].unique()
)

# Filtros - classificação
rating_slider = st.sidebar.slider(
    "Qual classificação de restaurante você deseja ver?",
    min_value=0.0,
    max_value=5.0,
    value=(0.0, 5.0),
    step=0.1,
    format="%.1f"
)
st.sidebar.markdown("""---""")

# Aplicar filtros
df1 = df1[df1['country_name'].isin(country_option)]
df1 = df1[df1['aggregate_rating'].between(rating_slider[0], rating_slider[1])]

st.sidebar.markdown("### Powered by Comunidade DS")

# Convertendo o DataFrame para CSV
csv = df1.to_csv(index=False)

# Botão de download
st.sidebar.download_button(
    label="Download dados",
    data=csv,
    file_name='dados_tratados.csv',
    mime='text/csv'
)

#-------------------------------------------------------------------------------
# Dashboard - Geral
#-------------------------------------------------------------------------------
# Título principal
st.header("Início")
st.subheader("Visão Geral dos Restaurantes no Mundo")
st.markdown("Uma análise global dos restaurantes cadastrados no programa Fome Zero")

total_restaurantes = df1.restaurant_id.nunique()
total_paises = df1.country_code.nunique()
total_cidades = df1.city.nunique()
total_avaliacoes = df1.votes.sum()
total_culinarias = df1.cuisines.nunique()

# Layout cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label="🍴 Restaurantes Únicos", value=total_restaurantes)
with col2:
    st.metric(label="🌍 Países", value=total_paises)
with col3:
    st.metric(label="🏙️ Cidades", value=total_cidades)
with col4:
    st.metric(label="⭐ Avaliações Totais", value=total_avaliacoes)
with col5:
    st.metric(label="🍻 Tipos de Culinária", value=total_culinarias) 

# Gráfico 1: Distribuição dos tipos de culinária
st.markdown("### Distribuição dos Tipos de Culinária")
culinarias = df1['cuisines'].value_counts().head(10).reset_index()
culinarias.columns = ['Culinária', 'Quantidade']
fig_culinarias = create_bar_chart(
    culinarias, 
    x='Culinária', 
    y='Quantidade', 
    title="Top 10 Tipos de Culinária Mais Frequentes", 
    text='Quantidade', 
    labels={'Quantidade': 'Número de Restaurantes', 'Culinária': 'Tipo de Culinária'}
)
st.plotly_chart(fig_culinarias, use_container_width=True)

# Gráfico 2: Distribuição por País
st.markdown("### Distribuição dos Restaurantes por País")
paises = df1['country_name'].value_counts().reset_index()
paises.columns = ['País', 'Quantidade']
fig_paises = create_pie_chart(
    paises, 
    values='Quantidade', 
    names='País', 
    title="Participação dos Países no Fome Zero"
)
st.plotly_chart(fig_paises, use_container_width=True)

# Mapa Interativo
st.markdown("### Mapa Interativo dos Restaurantes")
m = create_map(df1)
st_folium(m, width=700, height=500)
