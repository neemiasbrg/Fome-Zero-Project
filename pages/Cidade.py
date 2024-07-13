import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

# Configuração da página do Streamlit
st.set_page_config(page_title='Cidades', page_icon='city.png', layout='wide')

#===================================================
# Funções
#===================================================
# Definição das funções
def clean_data(df):
    """Função para limpeza dos dados do DataFrame."""
    df["Cuisines"] = df["Cuisines"].astype(str).apply(lambda x: x.split(",")[0] if ',' in x else x)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def country_name(code):
    """Função para retornar o nome do país com base no código."""
    COUNTRIES = {
        1: "India", 14: "Australia", 30: "Brazil", 37: "Canada",
        94: "Indonesia", 148: "New Zeland", 162: "Philippines",
        166: "Qatar", 184: "Singapure", 189: "South Africa",
        191: "Sri Lanka", 208: "Turkey", 214: "United Arab Emirates",
        215: "England", 216: "United States of America"
    }
    return COUNTRIES.get(code, "Unknown")

def create_bar_chart(data, x, y, title, color=None, color_continuous_scale=None):
    """Função para criar um gráfico de barras com Plotly Express."""
    fig = px.bar(data, x=x, y=y, title=title, color=color, color_continuous_scale=color_continuous_scale)
    return fig

def display_top_cities_graph(df_filtered):
    """Função para exibir o gráfico das top 10 cidades com mais restaurantes."""
    restaurantes_por_cidade = df_filtered.groupby('City').size().reset_index(name='Quantidade de Restaurantes')
    restaurantes_por_cidade = restaurantes_por_cidade.sort_values(by='Quantidade de Restaurantes', ascending=False)
    top_10_cidades = restaurantes_por_cidade.head(10)
    fig = create_bar_chart(top_10_cidades, 'City', 'Quantidade de Restaurantes', 'Top 10 cidades com mais restaurantes')
    st.plotly_chart(fig, use_container_width=True)

def display_top_countries_graph(df_filtered, country_options):
    """Função para exibir o gráfico das top 10 países com mais cidades selecionadas."""
    restaurantes_por_pais = df_filtered.groupby('Country').size().reset_index(name='Quantidade de Cidades')
    restaurantes_por_pais = restaurantes_por_pais.sort_values(by='Quantidade de Cidades', ascending=False)
    restaurantes_por_pais = restaurantes_por_pais[restaurantes_por_pais['Country'].isin(country_options)]
    top_10_paises = restaurantes_por_pais.head(10)
    fig = create_bar_chart(top_10_paises, 'Country', 'Quantidade de Cidades', 'Top 10 países com mais Cidades')
    st.plotly_chart(fig, use_container_width=True)

def display_classification_graphs(df_filtered, rating_column_name):
    """Função para exibir gráficos de barras para classificações de cidades."""
    st.subheader('Classificação das Cidades')

    # Cidades com classificação abaixo de 2.5
    df_baixo = df_filtered[df_filtered['Aggregate rating'] < 2.5]
    cidades_baixo = df_baixo.groupby('City').size().reset_index(name='Quantidade')
    fig_baixo = create_bar_chart(cidades_baixo, 'City', 'Quantidade', 'Cidades com Classificação Abaixo de 2.5', color='Quantidade', color_continuous_scale='blues')
    st.plotly_chart(fig_baixo, use_container_width=True)

    # Cidades com classificação acima de 4
    df_alto = df_filtered[df_filtered['Aggregate rating'] > 4]
    cidades_alto = df_alto.groupby('City').size().reset_index(name='Quantidade')
    fig_alto = create_bar_chart(cidades_alto, 'City', 'Quantidade', 'Cidades com Classificação Acima de 4', color='Quantidade', color_continuous_scale='reds')
    st.plotly_chart(fig_alto, use_container_width=True)

#===================================================
# Carregamento dos dados
#===================================================

dataframe = pd.read_csv('zomato.csv')

# Limpeza dos dados
df = clean_data(dataframe.copy())

# Adapte o nome da coluna de classificação se necessário
rating_column_name = 'Aggregate rating'

# Barra lateral
st.sidebar.header('Cidade')

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
    [country_name(code) for code in [1, 14, 30, 37, 94, 148, 162, 166, 184, 189, 191, 208, 214, 215, 216]],
    default=['Brazil']
)

st.sidebar.markdown('---')

# Seleção de tipos de culinária
cuisines_options = st.sidebar.multiselect(
    'Escolha o tipo de Culinária',
    df['Cuisines'].unique(),
    default=['Home-made']
)

# Seleção de tipos de culinária
cities_options = st.sidebar.multiselect(
    'Selecione a Cidade',
    df['City'].unique(),
    default=['São Paulo']
)

st.sidebar.markdown('---')

st.sidebar.markdown('##### Desenvolvido por')
st.sidebar.markdown('#### Neemias Gonçalves Braga')
st.sidebar.markdown('###### neemiasbrg')

# Filtrar dados com base na seleção do slider
if not country_options:
    df_filtered = df[df['Cuisines'].isin(cuisines_options) & df['City'].isin(cities_options)]

else:
    selected_countries = [code for code in [1, 14, 30, 37, 94, 148, 162, 166, 184, 189, 191, 208, 214, 215, 216] if country_name(code) in country_options]
    df_filtered = df[(df['Country Code'].isin(selected_countries)) & (df['Cuisines'].isin(cuisines_options))]

# Adicionar a coluna 'Country' ao DataFrame filtrado
df_filtered['Country'] = df_filtered['Country Code'].apply(lambda x: country_name(x))

# Layout principal no Streamlit
st.header('Visão das Cidades')

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        display_top_cities_graph(df_filtered)
        
    with col2:
        display_top_countries_graph(df_filtered, country_options)

with st.container():
    display_classification_graphs(df_filtered, rating_column_name)
