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
import numpy as np

#import dataset
df_raw = pd.read_csv("dataset\train.csv")

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
image_path  = 'images\logo.png'
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

    #container 1 com 6 colunas
    with st.container():
       
        st.markdown('## Métricas Gerais')
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap='large')

        with col1:
            delivery_unique = len(df.loc[:, 'Delivery_person_ID'].unique())

            col1.metric(' Entregadores Únicos :', delivery_unique )
        
        with col2:

            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            
            #opções para o haversine percorrder as linhas: for ou lambda  3haversine ((latitude, longitude), (latitude, longitude))
            df['distance'] = (df.loc[:, cols]
                                .apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ))

            #função round para arredondar os valores: np.round(....., 2)
            avg_distance = np.round(df['distance'].mean(), 2)
            
            col2.metric('Distância Média das Entregas', avg_distance )
            
        
        with col3:
 
            cols = ['Time_taken(min)', 'Festival']
            
            df_aux = df.loc[:, cols].groupby('Festival').agg( {'Time_taken(min)': ['mean', 'std']})
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2)

            col3.metric('Tempo Médio de Entrega c/ Festival', df_aux)            
        
        with col4:

            cols = ['Time_taken(min)', 'Festival']
            
            df_aux = df.loc[:, cols].groupby('Festival').agg( {'Time_taken(min)': ['mean', 'std']})
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2)

            col3.metric('Desvio Padrão de Entrega c/ Festival', df_aux)     

        with col5:

            cols = ['Time_taken(min)', 'Festival']
            
            df_aux = df.loc[:, cols].groupby('Festival').agg( {'Time_taken(min)': ['mean', 'std']})
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 2)

            col3.metric('Tempo Médio de Entrega s/ Festival', df_aux)               

        with col6:

            cols = ['Time_taken(min)', 'Festival']
            
            df_aux = df.loc[:, cols].groupby('Festival').agg( {'Time_taken(min)': ['mean', 'std']})
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 2)

            col3.metric('Desvio Padrão de Entrega s/ Festival', df_aux)            
    
    #container 2 com 1 coluna
    with st.container():

        st.markdown('## Tempo Médio de Entrega por Cidade')

        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        
        df['distance'] = df.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
        
        avg_distance = df.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])

        #fig.show()
        st.plotly_chart(fig)


    #container 3, com 2
    with st.container():
        st.markdown('## Distribuição do Tempo')

        col1, col2, = st.columns(2, gap='large')

        with col1:
            st.markdown('#### Tempo médio / Desvio padrão de Entrega por Cidade')

            cols = ['City', 'Time_taken(min)']
            
            df_aux = df.loc[:, cols].groupby('City').agg( {'Time_taken(min)': ['mean', 'std']})
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
            
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)
        
        with col2:
            st.markdown('#### Por Cidade e por Tipo de Tráfego')
            
            cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
            
            df_aux = df.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg( {'Time_taken(min)': ['mean', 'std']})
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))
            
            st.plotly_chart(fig)    
 

    #container 4, com 6 colunas    
    with st.container():
         st.markdown('## Distribuição da Distância')       

         cols = ['City', 'Time_taken(min)', 'Type_of_order']
        
         df_aux = df.loc[:, cols].groupby(['City', 'Type_of_order']).agg( {'Time_taken(min)': ['mean', 'std']})
        
         df_aux.columns = ['avg_time', 'std_time']
         df_aux = df_aux.reset_index()
        
         st.dataframe(df_aux)


#with tab2:




#with tab3:

