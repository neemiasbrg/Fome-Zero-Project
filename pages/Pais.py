import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import folium
from folium.plugins import MarkerCluster
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
import inflection

# Configuração da página do Streamlit
st.set_page_config(page_title='Países', page_icon='map.png', layout='wide')

#===================================================
# Funções
#===================================================

def rename_columns(dataframe):
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(dataframe.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    print("Colunas antigas:", cols_old)  # Adicione esta linha para depuração
    print("Colunas novas:", cols_new)    # Adicione esta linha para depuração
    dataframe.columns = cols_new
    return dataframe

def avg_rating_restaurant(df, top_asc):
    """Função para criar gráfico de médias de avaliações por restaurante."""
    media_rating_por_restaurante = df.groupby('restaurant_name')['aggregate_rating'].mean().reset_index()
    media_rating_por_restaurante = media_rating_por_restaurante.sort_values(by='aggregate_rating', ascending=top_asc)
    
    # Preparar os dados para o gráfico
    fig = go.Figure(go.Bar(
        y=media_rating_por_restaurante['restaurant_name'],
        x=media_rating_por_restaurante['aggregate_rating'],
        textposition='inside',
        textinfo='value+percent initial',
        opacity=0.65,
        marker={"color": "#008B8B"}
    ))
    
    fig.update_layout(
        yaxis_title='Restaurante',
        xaxis_title='Média do Aggregate Rating'
    )

    return fig

def clean_data(df):
    """Função para limpeza dos dados do DataFrame."""
    df["cuisines"] = df["cuisines"].astype(str).apply(lambda x: x.split(",")[0] if ',' in x else x)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def country_name(code=None):
    """Função para retornar os nomes dos países com base no country_id."""
    COUNTRIES = {
        1: "India", 14: "Australia", 30: "Brazil", 37: "Canada",
        94: "Indonesia", 148: "New Zealand", 162: "Philippines",
        166: "Qatar", 184: "Singapore", 189: "South Africa",
        191: "Sri Lanka", 208: "Turkey", 214: "United Arab Emirates",
        215: "England", 216: "United States of America"
    }
    if code is None:
        return COUNTRIES
    return COUNTRIES.get(code, "Unknown")

def replace_country_code_with_name(df):
    """Substitui o country_code pelos nomes dos países no DataFrame."""
    # Verificar os nomes das colunas
    print("Colunas no DataFrame antes da substituição:", df.columns.tolist())
    
    if 'country_code' not in df.columns:
        raise KeyError("A coluna 'country_code' não está presente no DataFrame.")
    
    country_mapping = country_name()  # Obtém o dicionário de mapeamento
    df['country_name'] = df['country_code'].map(country_mapping)
    return df

def create_bar_chart(data, x, y, title, color, color_continuous_scale=None):
    """Função para criar um gráfico de barras com Plotly Express."""
    fig = px.bar(data, x=x, y=y, title=title, color=color, color_continuous_scale=color_continuous_scale)
    return fig

def top_countries_by_restaurants(df):
    """Função para criar gráfico dos 10 países com o maior número de restaurantes."""
    restaurantes_por_pais = df.groupby('country_name')['restaurant_name'].count().reset_index(name='Número_de_Restaurantes')
    top_10_paises = restaurantes_por_pais.sort_values(by='Número_de_Restaurantes', ascending=False).head(10)
    fig = create_bar_chart(top_10_paises, 'country_name', 'Número_de_Restaurantes', 'Top 10 Países com o Maior Número de Restaurantes', color='Número_de_Restaurantes')
    fig.update_layout(
        xaxis_title='País',
        yaxis_title='Número de Restaurantes'
    )
    fig.update_traces(marker_color='green')
    return fig

def cities_per_country(df):
    """Função para criar gráfico da quantidade de cidades registradas por país."""
    cidades_por_pais = df.groupby('country_name')['city'].nunique().reset_index(name='Número_de_Cidades')
    fig = create_bar_chart(cidades_por_pais, 'country_name', 'Número_de_Cidades', 'Quantidade de Cidades Registradas por País', color='Número_de_Cidades')
    fig.update_layout(
        xaxis_title='País',
        yaxis_title='Número de Cidades'
    )
    fig.update_traces(marker_color='blue')
    return fig

def avg_rating_per_country(df):
    """Função para criar gráfico da média de avaliação por país."""
    media_avaliacao_por_pais = df.groupby('country_name')['aggregate_rating'].mean().reset_index()
    fig = create_bar_chart(media_avaliacao_por_pais, 'country_name', 'aggregate_rating', 'Média de Avaliação por País', color='aggregate_rating')
    fig.update_layout(
        xaxis_title='País',
        yaxis_title='Média de Avaliação'
    )
    fig.update_traces(marker_color='orange')
    return fig

def plot_detailed_map(df):
    """Função para criar mapa detalhado com os restaurantes e informações formatadas no popup."""
    m = folium.Map(location=[0, 0], zoom_start=2, tiles='OpenStreetMap')
    marker_cluster = MarkerCluster().add_to(m)

    for index, row in df.iterrows():
        # Cria o conteúdo HTML para o popup
        popup_content = f"""
        <div style="font-size: 16px; font-weight: bold;">{row['restaurant_name']}</div>
        <div style="font-size: 12px;">Tipo Culinária: {row['cuisines']}</div>
        <div style="font-size: 12px;">Classificação: {row['aggregate_rating']}</div>
        """
        
        folium.Marker(
            location=[row['latitude'], row['longitude']], 
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)

    return m

#===================================================
# Carregamento dos dados
#===================================================

df = pd.read_csv('zomato.csv')

# Verificar os nomes das colunas após carregar o CSV
print("Colunas após carregar o CSV:", df.columns.tolist())

# Renomear as colunas do DataFrame
df = rename_columns(df)

# Limpeza dos dados
df = clean_data(df)

# Substituir country_code por country_name
try:
    df = replace_country_code_with_name(df)
except KeyError as e:
    print(e)


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
    df['cuisines'].unique(),
    default=['Home-made']
)

# Seleção de tipos de culinária
cities_options = st.sidebar.multiselect(
    'Selecione a Cidade',
    df['city'].unique(),
    default=['São Paulo']
)

st.sidebar.markdown('---')

st.sidebar.markdown('##### Desenvolvido por')
st.sidebar.markdown('#### Neemias Gonçalves Braga')
st.sidebar.markdown('###### neemiasbrg')

# Filtrar dados com base na seleção do slider
if not country_options:
    df_filtered = df[df['cuisines'].isin(cuisines_options) & df['city'].isin(cities_options)]

else:
    selected_countries = [code for code in [1, 14, 30, 37, 94, 148, 162, 166, 184, 189, 191, 208, 214, 215, 216] if country_name(code) in country_options]
    df_filtered = df[(df['country_code'].isin(selected_countries)) & (df['cuisines'].isin(cuisines_options))]

# Adicionar a coluna 'Country' ao DataFrame filtrado
df_filtered['country_name'] = df_filtered['country_code'].apply(lambda x: country_name(x))

#===================================================
# Layout no Streamlit
#===================================================

st.header('Visão dos Países')

# Gráficos adicionais
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Top 10 Países com o Maior Número de Restaurantes')
        fig_countries = top_countries_by_restaurants(df_filtered)
        st.plotly_chart(fig_countries, use_container_width=True)

    with col2:
        st.subheader('Quantidade de Cidades Registradas por País')
        fig_cities = cities_per_country(df_filtered)
        st.plotly_chart(fig_cities, use_container_width=True)

# Exibir gráfico de média de avaliação por país
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Média de Avaliação por País')
        fig_avg_rating = avg_rating_per_country(df_filtered)
        st.plotly_chart(fig_avg_rating, use_container_width=True)

    with col2:
        st.subheader('Média do Preço de um Prato para Duas Pessoas')
        # Define a coluna de preço
        price_column = 'average_cost_for_two'
        media_preco_por_pais = df_filtered.groupby('country_name')[price_column].mean().reset_index()
        fig_avg_price = create_bar_chart(media_preco_por_pais, 'country_name', price_column, f'Média do Preço de um Prato para Duas Pessoas ({price_column})', color=price_column)
        st.plotly_chart(fig_avg_price, use_container_width=True)

# Exibir o mapa usando o Streamlit-Folium
st.subheader('Mapa Detalhado dos Restaurantes')
m = plot_detailed_map(df_filtered)
folium_static(m, width=800, height=600)
