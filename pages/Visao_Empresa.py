#librarires
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
import datetime
import folium
from streamlit_folium import folium_static

#import dataset
df_raw = pd.read_csv("dataset/train.csv")

#-----------------------------------tratamento dos dados---------------------------------------

# 1. Fazendo uma cópia do DataFrame lido:
df = df_raw.copy()

# 2. Remover espaço da string:
df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
df.loc[:, 'Delivery_person_Age'] = df.loc[:, 'Delivery_person_Age'].str.strip()
df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
df.loc[:, 'multiple_deliveries'] = df.loc[:, 'multiple_deliveries'].str.strip()

# 3. Excluir as linhas das colunas que possuem 'NaN':
linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN' )
df = df.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df['Road_traffic_density'] != 'NaN' )
df = df.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df['City'] != 'NaN' )
df = df.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df['Festival'] != 'NaN' )
df = df.loc[linhas_selecionadas, :].copy()

#neste trecho, uma linha com o conteudo NaN não consegue ser eliminado. Ao fazer o reset, consegue-se obter o index e em seguida, elimina-se a linha com index indicado.
linhas_selecionadas = (df['multiple_deliveries'] != 'NaN'  ) 
df = df.loc[linhas_selecionadas, :].reset_index().copy()
df = df.drop(df.index[7044])

# 4. Conversão de 'Age' e 'multiple_deliveries' de string para int:
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

# 5. Conversão de 'Ratings' de string para decimais:
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)

# 6. Conversão de texto para data:
df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')

#7 Limpar a coluna de time taken
df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda X: X.split('(min) ')[1])
df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

#-------------------------------------------------------------------------------------------------

# VISAO EMPRESA

#-------------------------------------------------------------------------------------------------

st.set_page_config(page_title='Visão Entregadores', layout='wide')

#-------------------------------------------------------------------------------------------------

# Barra Lateral ST

#-------------------------------------------------------------------------------------------------

st.markdown('# Marketplace - Visão Cliente')

#imagem - Biblioteca PIL
image_path  = 'images/logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)


# cada # significa o tamanho do título
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite' )

#primeiro filtro
date_slider = st.sidebar.slider('Até qual valor? ', value= datetime.datetime(2022, 4, 13),
                                                    min_value= datetime.datetime(2022, 2 , 11),
                                                    max_value= datetime.datetime(2022, 4, 6),
                                                    format='DD-MM-YYYY')

#st.header(date_slider)
st.sidebar.markdown("""___""")

#segundo filtro
traffic_options = st.sidebar.multiselect('Quais as condições do trânsito? ', ['Low', 'Medium', 'High', 'Jam'], default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""___""")
st.sidebar.markdown('Powered by Jobson de Melo')

#filtro das datas:
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#-------------------------------------------------------------------------------------------------

# Layout ST

#-------------------------------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1: 

    #Criação do primeiro container:
    with st.container():
       
        st.markdown('### Quantidade de pedidos por dia')
    
        #Colunas
        cols = ['ID', 'Order_Date']

        #Seleção das linhas
        df_aux = df.loc[:, cols].groupby( 'Order_Date').count().reset_index()

        #sintaxe: px. tipo do gráfico ( parametros)   #1º paramentro: vaariaveis: (df_aux) #eixo X: order date. Eixo Y: ID
        fig = px.bar( df_aux, x='Order_Date', y='ID')

        st.plotly_chart(fig, use_container_width=True)

    #container seguinte com 2 colunas
    with st.container():

        col1, col2 = st.columns(2)

        with col1:

            st.markdown('### Distribuição dos pedidos por tipo de tráfego')

            #primeiro necessário realizar uma conta
            df_aux = df.loc[ : , ['ID', 'Road_traffic_density' ]].groupby( 'Road_traffic_density' ).count().reset_index()

            #cálculo de entregas perc = soma a coluna toda e dividir por cada uma das linhas para ter uma percentagem
            df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

            #grafico pizza
            fig= px.pie( df_aux, values='entregas_perc', names= 'Road_traffic_density')
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            st.markdown('### volume de pedidos por cidade e tipo de tráfego')
            #4. Comparação do volume de pedidos por cidade e tipo de tráfego

            df_aux = df.loc[ : , ['ID', 'City', 'Road_traffic_density'] ].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()

            #gráfico de bolhas
            fig = px.scatter(df_aux, x='City', y= 'Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig, use_container_width = True)

    

with tab2:

    with st.container():

        st.markdown('### Quantidade de Pedidos por Semana')

        df['week_of_year'] = df['Order_Date'].dt.strftime('%U')

        df_aux = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux.head()

        fig= px.line(df_aux, x='week_of_year', y='ID')
        st.plotly_chart(fig, use_container_width = True)
   
    with st.container():

        st.markdown('### Quantidade de Pedidos por Entregador por Semana')   

        #quantidade de pedidos por semana / número único de entregadores por semana. Será preciso duas partes
        df_aux1 = df.loc[ : , ['ID', 'week_of_year'] ].groupby('week_of_year').count().reset_index()
        df_aux2 = df.loc[ : , ['Delivery_person_ID', 'week_of_year'] ].groupby('week_of_year').nunique().reset_index()

        #unindo os dataframes através da função merge
        df_aux = pd.merge(df_aux1, df_aux2, how='inner', on='week_of_year' )

        #nova coluna 
        df_aux['Order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

        fig= px.line(df_aux, x='week_of_year', y= 'Order_by_delivery')
        st.plotly_chart(fig, use_container_width = True)

with tab3:

    st.markdown( '### Localização Central das Cidade por Tipo de Tráfego')

    df_aux = df.loc[ : , ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude'] ].groupby(['City', 'Road_traffic_density']).median().reset_index()


    #biblioteca que desenha um mapa mundial: folium
    map = folium.Map()

    #sintaxe do folium marker:  folium.Marker ( [latitude, longitude ] ).add_to()

    #iterrow cria um objeto de iteração, está de acordo com a biblioteca do folium
    for index, location_info in df_aux.iterrows():
       folium.Marker ( [location_info['Delivery_location_latitude'], 
                        location_info ['Delivery_location_longitude'] ],
                        popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

    #para imprimir o mapa no streamlit é preciso instalar e importar a biblioteca streamlit_folium
    folium_static(map, width=1204, height= 600)
