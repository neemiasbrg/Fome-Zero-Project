import pandas as pd
import numpy as np
import re
from haversine import haversine, Unit
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
import folium
import datetime

# Configuração da página do Streamlit
st.set_page_config(page_title='Restaurantes', page_icon='restaurant.png', layout='wide')

#===================================================
# Funções
#===================================================

def avg_rating_restraurant(df, top_asc):
    """Função para criar gráfico de funil para médias de avaliações por restaurante."""
    media_rating_por_restaurante = df.groupby('Restaurant Name')['Aggregate rating'].mean().reset_index()
    media_rating_por_restaurante = media_rating_por_restaurante.sort_values(by='Aggregate rating', ascending=top_asc)
    
    # Preparar os dados para o gráfico de funil
    fig = go.Figure(go.Funnel(
        y=media_rating_por_restaurante['Restaurant Name'],
        x=media_rating_por_restaurante['Aggregate rating'],
        textposition='inside',
        textinfo='value+percent initial',
        opacity=0.65,
        marker={"color": "#008B8B"}
    ))
    
    fig.update_layout(
        yaxis_title='Restaurante',
        xaxis_title='Média do Aggregate rating'
    )

    return fig

def clean_data(df):
    """Função para limpeza dos dados do DataFrame."""
    df["Cuisines"] = df["Cuisines"].astype(str).apply(lambda x: x.split(",")[0] if ',' in x else x)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def country_name(code=None):
    """Função para retornar os nomes dos países."""
    COUNTRIES = {
        1: "India", 14: "Australia", 30: "Brazil", 37: "Canada",
        94: "Indonesia", 148: "New Zeland", 162: "Philippines",
        166: "Qatar", 184: "Singapure", 189: "South Africa",
        191: "Sri Lanka", 208: "Turkey", 214: "United Arab Emirates",
        215: "England", 216: "United States of America"
    }
    if code is None:
        return list(COUNTRIES.values())
    return COUNTRIES.get(code, "Unknown")

def create_bar_chart(data, x, y, title, color=None, color_continuous_scale=None):
    """Função para criar um gráfico de barras com Plotly Express."""
    fig = px.bar(data, x=x, y=y, title=title, color=color, color_continuous_scale=color_continuous_scale)
    return fig

def display_types_by_classification(df_filtered, rating_column_name):
    """Função para exibir gráfico de tipos de restaurantes únicos por faixa de classificação."""
    # Agrupar por faixa de classificação e contar tipos únicos de restaurantes
    df_filtered['Cuisine Count'] = df_filtered.groupby(rating_column_name)['Cuisines'].transform(lambda x: x.nunique())
    df_grouped = df_filtered.groupby(rating_column_name)['Cuisine Count'].max().reset_index()
    df_grouped = df_grouped.sort_values(by=rating_column_name)
    
    # Criar o gráfico de barras
    fig = create_bar_chart(df_grouped, rating_column_name, 'Cuisine Count', 'Tipos de Restaurantes Únicos por Classificação', color='Cuisine Count', color_continuous_scale='viridis')
    return fig

#===================================================
# Carregar os dados
#===================================================

dataframe = pd.read_csv('zomato.csv')

#===================================================
# Limpeza dos dados
#===================================================

df = clean_data(dataframe.copy())

#===================================================
# Barra lateral
#===================================================

# Carregar e mostrar a imagem do logo
image_path = 'fome_zero.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Fome Zero')
st.sidebar.markdown('### Delícias que acabam com a fome: Fome Zero, onde cada prato é uma solução!')
st.sidebar.markdown('---')

# Seleção de países
country_options = st.sidebar.multiselect(
    'Selecione o País',
    country_name(),
    default=['Brazil']
)

st.sidebar.markdown('---')

min_note = df['Aggregate rating'].min()
max_note = df['Aggregate rating'].max()

# Slider na barra lateral para seleção de nota
notas_options = st.sidebar.slider(
    'Selecione uma nota',
    min_value=min_note,
    max_value=max_note,
    value=max_note
)

st.sidebar.markdown('---')

# Seleção de tipos de culinária
cuisines_options = st.sidebar.multiselect(
    'Escolha o tipo de Culinária',
    df['Cuisines'].unique(),
    default=['Home-made']
)

st.sidebar.markdown('---')

st.sidebar.markdown('##### Desenvolvido por')
st.sidebar.markdown('#### Neemias Gonçalves Braga')
st.sidebar.markdown('###### neemiasbrg')

# Filtrar dados com base na seleção do slider
if not country_options:
    df_filtered = df[df['Cuisines'].isin(cuisines_options) & (df['Aggregate rating'] <= notas_options)]
else:
    country_codes = [code for code, name in enumerate(country_name(), 1) if name in country_options]
    df_filtered = df[(df['Country Code'].isin(country_codes)) & (df['Cuisines'].isin(cuisines_options)) & (df['Aggregate rating'] <= notas_options)]

# Adicionar a coluna 'Country' ao DataFrame filtrado
df_filtered['Country'] = df_filtered['Country Code'].apply(lambda x: country_name(x))

#===================================================
# Layout no Streamlit
#===================================================

st.header('Visão dos Restaurantes')

# Exibir o gráfico de tipos de restaurantes únicos por faixa de classificação
st.subheader('Tipos de Restaurantes Únicos por Classificação')
fig_types = display_types_by_classification(df_filtered, 'Aggregate rating')
st.plotly_chart(fig_types)

# Exibir os dois gráficos de médias de avaliações lado a lado
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Top Menores Médias do Aggregate rating por Restaurante')
        fig = avg_rating_restraurant(df, True)
        st.plotly_chart(fig)

    with col2:
        st.subheader('Top Maiores Médias do Aggregate rating por Restaurante')
        fig = avg_rating_restraurant(df, False)
        st.plotly_chart(fig)

