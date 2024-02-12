
import streamlit as st
from PIL import Image

#função para juntar as páginas dentro de pages
st.set_page_config(
    page_title="Home",
)


#para inserir um símbolo dentro de set_page_config: edit --> Emojis --> Simbol

image_path='images/'
image= Image.open(image_path + 'logo.png')
st.sidebar.image(image, width=120)


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write('# Curry Company Growth Dashboard')

st.markdown(

    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar este Growth Dashboard?
    - #### Visão empresa:
        - Visão Gerenciaç: Métricas Gerais de Comportamento
        - Visão Tática: Indicadores Semanais de Crescimento
        - Visão Geográfica: Insights de Geolocalização
    - #### Visão Entregadores:
        - Acompanhamento dos Indicadores Semanais de Crescimento
    - #### Visão Restaurante:
        - Indicadores Semanais de Crescimento dos Restaurantes
    """
)
