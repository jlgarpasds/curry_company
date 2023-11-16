# import Libraries
from haversine import haversine, Unit
import plotly.express as px
import plotly.graph_objects as go

# Bibliotecas
import folium
mymap = folium.Map()
import pandas as pd
import numpy as np
import streamlit as st
#from streamlit_folium import folium_static #desatualizado
from streamlit_folium import st_folium  
from PIL import Image # Libraria para manipulação de imagenes
#from matplotlib import pyplot as plt 
import datetime
import re

st.set_page_config(page_title='Visão Restaurantes', layout='wide')

# ------- Import Dataset ----------------
df = pd.read_csv('dataset/train.csv')


### ==================================================================
### ----------------- FUNÇÕES ----------------------------------------
### ==================================================================
def clean_dfCury(df1):
    """ Função clean_dfCury(df1)
        Realiza a limpeça e formatação de dados do dataframe curycompany
        Limpezas feitas:
        1. Remoção dos dados 'NaN '
        2. Conversão de tipo de dados em algumas colunas
        3. Remoção de espação brancos.
        4. Formatação de colunas tipo data
        5. Limpeza, coluna tempo (remoção do texto para deixar so valor númerico dos dados da coluna.)

        Input = DataFrame
        output = DataFrame
    """

    #Remoção dos dados 'NaN'
           
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()
    
    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()
    
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas= df1['Weatherconditions'] != 'conditions NaN'
    df1 = df1.loc[linhas_selecionadas,:].copy()
    
    
    #Conversão de tipo de dados em algumas colunas
       
    #Conversão do formato objet/text da coluna Delivery_person_Age para dado tipo int
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    #Conversão do formato objet/text da coluna 'Delivery_person_Ratings' para dado tipo float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    #conversão do formato objet/text da coluna 'multiple_deliveries' para o tipo int
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
        
    #Remoção de espação brancos.
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip() #
    df1.loc[:,'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()

    #Formatação de colunas tipo data
    #"""Conversão do formato objet/text da coluna Order_date para tipo de dado DataTime
    #usaremos uma função da libreria "pandas"""
    df1['Order_Date'] = pd.to_datetime (df1['Order_Date'], format= '%d-%m-%Y')
    
    #Limpeza, coluna tempo (remoção do texto para deixar so valor númerico dos dados da coluna.)
    #Limpeza do campo time_taken(min)"""
    df1['Time_taken(min)']=df1['Time_taken(min)'].apply(lambda x:x.split('(min) ')[1]).astype(int)
    
    #resetamos o index do DataFrame
    df1 = df1.reset_index(drop=True)

    return (df1)


def distance_haversine (df1):
    colunas = (['Restaurant_latitude',
                'Restaurant_longitude',
                'Delivery_location_latitude',
                'Delivery_location_longitude'])
    df1['DistanceLocaltoDelivery']= (df1.loc[:,colunas]
                                     .apply(lambda x: haversine 
                                            ((x['Restaurant_latitude'],x['Restaurant_longitude']),
                                            (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),
                                            axis=1))
    avg_distance = np.round(df1['DistanceLocaltoDelivery'].mean(),2)
    return avg_distance


def avg_std_time_delivery(df1,festi_flag,operation):
    #Esta função calcula o tempo medio e o desvio padrão do tempo de entrega
    #Parametros --- 
    # input:
    #       -df1         : dataframe para realizaro os calculos 
    #       -festiflag   : determinamos se e em dia com festival (Yes) ou dias sem festival (No)
    #       -operation    : tipo de operação - mean or std 
    # output: float number avg or std time
    
    
    colunas = ['Time_taken(min)','Festival']
    df_aux = (df1.loc[:,colunas]
              .groupby(['Festival'])
              .agg({'Time_taken(min)':['mean','std']}))
    df_aux.columns = ['avg_time','std_time']
    df_aux= df_aux.reset_index()
    linha = df_aux['Festival']==festi_flag # Yes - No
    if operation == 'mean':
        time_avg_std_entregas =np.round(df_aux.loc[linha,'avg_time'],2)
    elif operation == 'std':
        time_avg_std_entregas =np.round(df_aux.loc[linha,'std_time'],2)
    return (time_avg_std_entregas)
    
def avg_std_entregasbycidade(df1):
            
    #O tempo médio e o desvio padrão de entrega por cidade.
    colunas = ['City','Time_taken(min)']
    df_aux = (df1.loc[:,colunas]
              .groupby(['City'])
              .agg({'Time_taken(min)':['mean','std']}))
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',x=df_aux['City'],y=df_aux['avg_time'],
                         error_y=dict(type='data',array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    
    return (fig)


def avg_std_cidade_typeorder(df1):

    colunas = ['City','Type_of_order','Time_taken(min)']
    df_aux = df1.loc[:,colunas].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    
    return (df_aux)


def distancelocaldelivery (df1):
            
    #A distância média dos resturantes e dos locais de entrega.
    # SA - Retornar o valor da distância media dos restaurantes e dos locais de entrega
    # P  - 
    # E  -colunas['ID','Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    # Para calculo entre pontos georeferencias usamos a funçaõ  haversine -- Precissa ser importada antes.
            
    colunas = (['Restaurant_latitude',
                'Restaurant_longitude',
                'Delivery_location_latitude',
                'Delivery_location_longitude'])
    df_aux['DistanceLocaltoDelivery']=( df1.loc[:,colunas]
                                        .apply(lambda x: haversine ((x['Restaurant_latitude'],
                                                                     x['Restaurant_longitude']),
                                                                    (x['Delivery_location_latitude'],
                                                                     x['Delivery_location_longitude'])),axis=1))
    avg_distance = df_aux.loc[:,['City','DistanceLocaltoDelivery']].groupby(['City']).mean().reset_index()      
    fig = (go.Figure(data=[go.Pie(labels=avg_distance['City'],
                                  values=avg_distance['DistanceLocaltoDelivery'],
                                  pull=[0,0.1,0])]))
    fig.update_layout(autosize=False,width=600,height=600)
           
    return (fig)

def avg_std_entregas_citytraffic(df1):
      #O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego.
    colunas = ['City','Time_taken(min)','Road_traffic_density']
    df_aux = (df1.loc[:,colunas]
              .groupby(['City','Road_traffic_density'])
              .agg({'Time_taken(min)':['mean','std']}))
    
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    
    fig = px.sunburst(df_aux, path=['City','Road_traffic_density'],values='avg_time',
                      color='std_time',color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))
            
    fig.update_layout(autosize=False,width=500,height=500)                  
            
    return (fig) 
            
        


# =================================================
#     STREAMLIT--- SIDEBAR
# =================================================

st.header('Marketplace - Visão Restaurantes')

#path for local use
#image_path = '/home/jlgarpas/Documents/repos/FTC-AD-COM-PYTHON/logo.png'
image_path = 'logo.png'
image = Image.open(image_path)

st.sidebar.image(image, width=120)

st.sidebar.markdown('# THE CURY COMPANY')
st.sidebar.markdown('## Fasfest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione suas opções')

#Data Slider

date_slider = st.sidebar.slider('Até qual data?', value=datetime.date(2022,4,13), min_value=datetime.date(2022,2,11),max_value=datetime.date(2022,4,6), format = 'DD-MM-YYYY')

st.sidebar.markdown ("""---""")

#Condicoes do trãnsito Slider
transito_slider = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['High', 'Jam', 'Low', 'Medium'], default =['High', 'Jam', 'Low', 'Medium'])

#Condicoes climaticas
clima_slider = st.sidebar.multiselect(
    'Quais as condições do tempo/clima',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy','conditions Sunny','conditions Windy'],
    default =['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy','conditions Sunny','conditions Windy'])

st.sidebar.markdown ("""---""")

# pie de sidebar
st.sidebar.markdown('### Powered by ComunidadeDS')



# =================================================
#     ESTRUTURA LOGICA DO CODIGO
# =================================================
df1=clean_dfCury(df)

# ================================================
# VINCULAÇÃO DOS ELEMENTOS DO SIDEBAR AO DATASET
# ================================================

date_slider = np.datetime64(date_slider)  #conversao de dados

linhas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas,:]

linhas = df1['Road_traffic_density'].isin(transito_slider)
df1 = df1.loc[linhas,:]

linhas = df1['Weatherconditions'].isin(clima_slider)
df1 = df1.loc[linhas,:]

# =================================================
#     STREAMLIT --- LAYOUT CENTRAL
# =================================================

st.title('Crescimento Restaurantes')

tab1,tab2,tab3 = st.tabs(['Visão Geral','',''])

with tab1:
    with st.container():
        st.header('Overall Metrics')
        col1,col2,col3,col4,col5,col6 = st.columns(6)

        with col1:
            #'Quantidade de Entregadores Unicos')
            n_entregadores_unicos = df1.loc[:,'Delivery_person_ID'].nunique()
            col1.metric(label=f':busts_in_silhouette: Entregadores',value=n_entregadores_unicos)
            
            
        with col2:
            #st.subheader('EA distância média dos resturantes e dos locais de entrega.')
            # Para calculo entre pontos georeferencias usamos a funçaõ  haversine -- Precissa ser importada antes.
            avg_distance = distance_haversine(df1)
            col2.metric(label=f':straight_ruler: Distancia media',value=f'{avg_distance} Km.')
                
        with col3:
            #'Tempo de Entrega medio c Festival')
            time_avg_std_entregas = avg_std_time_delivery(df1,'Yes','mean')
            col3.metric(label=f':stopwatch: :sparkles: avg deliveries/fest', value=time_avg_std_entregas)

        with col4:
            #st.subheader('Desviação padra do tempo de entrega c Festival')
            time_avg_std_entregas = avg_std_time_delivery(df1,'Yes','std')
            col4.metric(label=f':stopwatch: :sparkles: STD deliveries/Fest', value=time_avg_std_entregas)

        with col5:
            #st.subheader('Tempo de Entrega medio SIN Festival')
            time_avg_std_entregas = avg_std_time_delivery(df1,'No','mean')
            col5.metric(label=f':stopwatch: Avgtime-Deliveries', value=time_avg_std_entregas)

        with col6:
            #st.subheader('Desviação padra do tempo de entrega c Festival')
            time_avg_std_entregas = avg_std_time_delivery(df1,'No','std')
            col6.metric(label=f':stopwatch: STD deliveries', value=time_avg_std_entregas)
            
    with st.container():
        #'tempo de entrega'
        st.markdown("""---""")
        st.header('Tempo de entrega')
        
        col1, col2 = st.columns(2)

        with col1:
            #O tempo médio e o desvio padrão de entrega por cidade
            st.markdown('### Avg-Std entregas by Cidade')
            fig = avg_std_entregasbycidade(df1)
            st.plotly_chart(fig, use_container_width=True)            
            
        with col2:
            #O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido.
            st.markdown('### Avg-Std Entregas Cidade/Type Order')
            df_aux = avg_std_cidade_typeorder (df1)  
            st.dataframe(df_aux,use_container_width=True)
               
    with st.container():
        #'Distribuição do tempo'
        st.markdown("""---""")
        st.header('Distribuição do Tempo')

        col1, col2 = st.columns(2)
            
        with col1:
            st.markdown('### Distance Local to Delivery Point')
            fig = distancelocaldelivery (df1)
            st.plotly_chart(fig, use_container_width=True) 
            
        with col2:     
            #O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego.
            st.markdown('### Avg_Std-Entregas-CidadeXTraffic')
            fig = avg_std_entregas_citytraffic(df1)
            st.plotly_chart(fig, use_container_width=True)
           
            