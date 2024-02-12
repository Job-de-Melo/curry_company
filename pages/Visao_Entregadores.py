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

#-------------------------------------------------------------------------------------------------

# Barra Lateral ST

#-------------------------------------------------------------------------------------------------

st.markdown('# Marketplace - Visão Entregadores')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1: 

    #container com 4 colunas
    with st.container():
       
        st.markdown('## Métricas Gerais')
        col1, col2, col3, col4 = st.columns(4, gap='large')

        with col1:
            maior_idade = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric(' Maior Idade :', maior_idade)


        with col2:
            menor_idade = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric(' Menor Idade :', menor_idade)
        
        with col3:
            melhor_codicao = df.loc[:, 'Vehicle_condition'].max()
            col3.metric(' Melhor Condição de Viatura :', melhor_codicao)

        with col4:
            pior_condicao = df.loc[:, 'Vehicle_condition'].min()
            col4.metric(' Pior Condição de Viatura :', pior_condicao)

    #container com 2 colunas
    with st.container():

        st.sidebar.markdown("""___""")
        st.markdown('## Avaliações')
        col1, col2  = st.columns(2, gap='large')

        with col1:
            st.markdown('### Avaliação Médias por Entregador')

            df_avg_ratings_per_deliver = (df.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index())
            st.dataframe(df_avg_ratings_per_deliver)

        with col2:
            st.markdown('## Avaliação Média por Transito') 

            df_avg__std_rating_by_traffic = df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']})

            #mudança de nome das colunas 
            df_avg__std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

            #reset do index
            df_avg__std_rating_by_traffic = df_avg__std_rating_by_traffic.reset_index()

            st.dataframe(df_avg__std_rating_by_traffic)

            #Linha seguinte:        

            st.markdown('## Avaliação Média por Clima')     

            df_avg__std_rating_by_weather = df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']})

            df_avg__std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
            df_avg__std_rating_by_weather = df_avg__std_rating_by_weather.reset_index()

            st.dataframe(df_avg__std_rating_by_weather )

    #container com 2 colunas
    with st.container():

        st.sidebar.markdown("""___""")
        st.markdown('## Velocidade de Entrega')
        col1, col2  = st.columns(2, gap='large')

        with col1:
            st.markdown('### Top Entregadores mais Rápidos')

            df_fast = (df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID'])
                                                                                   .mean()
                                                                                   .sort_values(['City','Time_taken(min)'], ascending=True)
                                                                                   .reset_index())
    
            df_aux01 = df_fast.loc[df_fast['City'] == 'Metropolitian', :].head(10)            
            df_aux02 = df_fast.loc[df_fast['City'] == 'Urban', :].head(10)
            df_aux03 = df_fast.loc[df_fast['City'] == 'Semi-Urban', :].head(10)
            
            df_result = pd.concat ([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

            st.dataframe(df_result)

        with col2:
            st.markdown('### Top Entregadores mais Lentos') 
  
            df_fast = (df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                         .groupby(['City', 'Delivery_person_ID'])
                         .mean()
                         .sort_values(['City','Time_taken(min)'], ascending=False)
                         .reset_index())
    
            df_aux01 = df_fast.loc[df_fast['City'] == 'Metropolitian', :].head(10)            
            df_aux02 = df_fast.loc[df_fast['City'] == 'Urban', :].head(10)
            df_aux03 = df_fast.loc[df_fast['City'] == 'Semi-Urban', :].head(10)
            
            df_result = pd.concat ([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

            st.dataframe(df_result)

#with tab2:




#with tab3:

