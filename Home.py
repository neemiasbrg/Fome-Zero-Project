import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
import base64



# Caminho da imagem que será usada como ícone da página
image_path = "home.png"
with open(image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()

# Configuração da página com título, ícone e layout
st.set_page_config(
    page_title='Home',
    page_icon=f"data:image/png;base64,{encoded_string}",
    layout='wide'
)

st.write("# Fome Zero Growth Dashboard")

st.markdown(
    """
    O **Fome Zero Growth Dashboard** foi desenvolvido para fornecer uma visão abrangente sobre o crescimento e o desempenho dos restaurantes, ajudando na tomada de decisões estratégicas. Este dashboard é dividido em várias seções para facilitar a análise dos dados.

    ### Como utilizar esse Growth Dashboard?

    - **Visão Cidade:**
        - **Análise de Desempenho por Cidade:** Visualize e compare o desempenho dos restaurantes em diferentes cidades. Identifique quais cidades têm as melhores e piores avaliações.
        - **Métricas de Entregas:** Acompanhe o número de entregas realizadas por cidade e como isso afeta a avaliação geral.
        - **Preços Médios:** Compare os preços médios dos pratos em diferentes cidades e como isso se relaciona com as avaliações dos clientes.
        - **Tendências de Crescimento:** Identifique as tendências de crescimento em termos de número de restaurantes e avaliações em cada cidade.

    - **Visão País:**
        - **Desempenho por País:** Analise como os restaurantes estão performando em diferentes países e compare as médias de avaliação.
        - **Distribuição de Restaurantes:** Veja a distribuição de restaurantes por país e como isso afeta a competição local.
        - **Comparação Internacional:** Compare os preços e avaliações dos restaurantes em diferentes países.
        - **Insights Regionais:** Identifique oportunidades e desafios específicos para cada país com base nas métricas de avaliação e preço.

    - **Visão Restaurantes:**
        - **Melhores Restaurantes:** Descubra quais são os melhores restaurantes de acordo com a avaliação média e outras métricas importantes.
        - **Restaurantes por Tipo de Culinária:** Explore como diferentes tipos de culinária estão se destacando em termos de avaliações e popularidade.
        - **Análise de Preços:** Compare os preços médios dos pratos nos restaurantes e como isso se correlaciona com as avaliações dos clientes.
        - **Tendências de Reserva e Pedidos Online:** Verifique como a aceitação de reservas e pedidos online está impactando a performance dos restaurantes.

    - **Visão Tipo de Culinárias:**
        - **Melhores Restaurantes por Tipo de Culinária:** Identifique os melhores restaurantes em cada tipo de culinária com base nas avaliações dos clientes.
        - **Médias de Avaliações por Tipo de Culinária:** Analise as médias de avaliações para diferentes tipos de culinária e veja quais são mais apreciados pelos clientes.
        - **Pedidos Online e Reservas:** Compare a aceitação de pedidos online e reservas entre os diferentes tipos de culinária.
        - **Preços e Avaliações:** Explore como o preço médio dos pratos varia entre os diferentes tipos de culinária e como isso impacta as avaliações.

        Utilize este dashboard para obter uma visão detalhada das métricas de crescimento e para tomar decisões informadas sobre estratégias de expansão e melhoria de desempenho.
    """
)

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


st.sidebar.markdown('##### Desenvolvido por')
st.sidebar.markdown('#### Neemias Gonçalves Braga')
st.sidebar.markdown('###### neemiasbrg')