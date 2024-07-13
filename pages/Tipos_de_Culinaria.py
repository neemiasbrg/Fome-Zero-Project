import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

# Configuração da página do Streamlit
st.set_page_config(page_title='Culinárias', page_icon='cuisine.png', layout='wide')

#===================================================
# Funções
#===================================================
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

def best_restaurant_by_cuisine(df):
    """Função para obter o melhor restaurante por tipo de culinária."""
    best_restaurants = df.loc[df.groupby('Cuisines')['Aggregate rating'].idxmax()]
    return best_restaurants[['Cuisines', 'Restaurant Name', 'Aggregate rating']]

def avg_rating_by_cuisine(df, ascending=True):
    """Função para criar gráfico de barras para médias de avaliações por tipo de culinária."""
    avg_rating_cuisine = df.groupby('Cuisines')['Aggregate rating'].mean().reset_index()
    avg_rating_cuisine = avg_rating_cuisine.sort_values(by='Aggregate rating', ascending=ascending)
    color_scale = 'YlOrBr' if ascending else 'Blues'
    fig = create_bar_chart(avg_rating_cuisine, 'Cuisines', 'Aggregate rating', 
                           'Média de Avaliação por Tipo de Culinária', 'Aggregate rating', color_continuous_scale=color_scale)
    return fig

def restaurants_by_online_order(df):
    """Função para criar gráfico do número de restaurantes que aceitam e não aceitam pedidos online."""
    if 'Has Online delivery' not in df.columns:
        st.error("Coluna 'Has Online delivery' não encontrada no DataFrame.")
        return go.Figure()  # Retorna um gráfico vazio em caso de erro
    
    online_order_counts = df['Has Online delivery'].value_counts().reset_index()
    online_order_counts.columns = ['Has Online delivery', 'Number of Restaurants']
    fig = create_bar_chart(online_order_counts, 'Has Online delivery', 'Number of Restaurants', 
                           'Número de Restaurantes por Aceitação de Pedidos Online', 'Has Online delivery', color_continuous_scale='Viridis')
    fig.update_traces(marker_color='blue')
    return fig

def restaurants_by_reservation(df):
    """Função para criar gráfico do número de restaurantes que fazem e não fazem reservas."""
    if 'Has Table booking' not in df.columns:
        st.error("Coluna 'Has Table booking' não encontrada no DataFrame.")
        return go.Figure()  # Retorna um gráfico vazio em caso de erro
    
    reservation_counts = df['Has Table booking'].value_counts().reset_index()
    reservation_counts.columns = ['Has Table booking', 'Number of Restaurants']
    fig = create_bar_chart(reservation_counts, 'Has Table booking', 'Number of Restaurants', 
                           'Número de Restaurantes por Reserva', 'Has Table booking', color_continuous_scale='Viridis')
    fig.update_traces(marker_color='orange')
    return fig

def create_bar_chart(data, x, y, title, color, color_continuous_scale=None):
    """Função para criar um gráfico de barras com Plotly Express."""
    fig = px.bar(data, x=x, y=y, title=title, color=color, color_continuous_scale=color_continuous_scale)
    fig.update_layout(xaxis_title=x, yaxis_title=y)
    return fig

def convert_to_brl(df, exchange_rate):
    """Função para converter o preço de um prato para duas pessoas da moeda local para BRL."""
    df['Price (BRL)'] = df['Average Cost for two'] * exchange_rate
    return df

#===================================================
# Carregar os dados
#===================================================

dataframe = pd.read_csv('zomato.csv')

#===================================================
# Limpeza dos dados
#===================================================

df = clean_data(dataframe.copy())

# Adicionar a coluna 'Country' ao DataFrame
df['Country'] = df['Country Code'].apply(lambda x: country_name(x))

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

# Opção para conversão de preço
convert_to_brl_option = st.sidebar.checkbox('Converter preço para BRL', value=True)

st.sidebar.markdown('---')

st.sidebar.markdown('##### Desenvolvido por')
st.sidebar.markdown('#### Neemias Gonçalves Braga')
st.sidebar.markdown('###### neemiasbrg')

# Filtrar dados com base na seleção do slider
if not country_options:
    df_filtered = df[df['Cuisines'].isin(cuisines_options) & (df['Aggregate rating'] <= notas_options)]
else:
    country_codes = [code for code, name in enumerate(range(1, 217), 1) if country_name(code) in country_options]
    df_filtered = df[(df['Country Code'].isin(country_codes)) & (df['Cuisines'].isin(cuisines_options)) & (df['Aggregate rating'] <= notas_options)]

# Adicionar a coluna 'Country' ao DataFrame filtrado
df_filtered['Country'] = df_filtered['Country Code'].apply(lambda x: country_name(x))

# Se a opção de conversão para BRL estiver marcada, converter os preços
if convert_to_brl_option:
    exchange_rate = st.number_input('Taxa de Câmbio USD/BRL', min_value=0.0, value=5.0, step=0.01)
    df_filtered = convert_to_brl(df_filtered, exchange_rate)
    price_column = 'Price (BRL)'
else:
    price_column = 'Average Cost for two'

#===================================================
# Layout no Streamlit
#===================================================

st.header('Visão de Culinárias')

# Melhores Restaurantes por Tipo de Culinária
with st.container():
    st.subheader('Melhor Restaurante por Tipo de Culinária')
    best_restaurants = best_restaurant_by_cuisine(df_filtered)
    st.dataframe(best_restaurants)

# Gráficos adicionais
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Maiores Médias de Avaliação por Tipo de Culinária')
        fig_avg_rating_high = avg_rating_by_cuisine(df_filtered, ascending=False)
        st.plotly_chart(fig_avg_rating_high)

    with col2:
        st.subheader('Menores Médias de Avaliação por Tipo de Culinária')
        fig_avg_rating_low = avg_rating_by_cuisine(df_filtered, ascending=True)
        st.plotly_chart(fig_avg_rating_low)

# Gráficos adicionais sobre pedidos online e reservas
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Número de Restaurantes que Aceitam e Não Aceitam Pedidos Online')
        fig_online_order = restaurants_by_online_order(df_filtered)
        st.plotly_chart(fig_online_order)

    with col2:
        st.subheader('Número de Restaurantes que Fazem e Não Fazem Reservas')
        fig_reservation = restaurants_by_reservation(df_filtered)
        st.plotly_chart(fig_reservation)
