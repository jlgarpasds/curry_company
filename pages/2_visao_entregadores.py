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
# from matplotlib import pyplot as plt 
import datetime
import re

st.set_page_config(page_title='Visão Entregadores', layout='wide')


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

def delivery_menor_idade (df1):
    menor_idade = df1.loc[:,'Delivery_person_Age'].min()
    #linhas = df1['Delivery_person_Age']==menor_idade
    #quantas pessoas tem a maior_idade
    #nmenor_idade = df1.loc[linhas,'Delivery_person_ID'].nunique()
    #col2.metric(label=f'Menor idade :busts_in_silhouette:',value=menor_idade, delta=f'{nmenor_idade}: pessoas')
    
    return (menor_idade)


def delivery_maior_idade (df1):
    maior_idade = df1.loc[:,'Delivery_person_Age'].max()
    #linhas = df1['Delivery_person_Age']==maior_idade
    #quantas pessoas tem a maior_idade
    #nmaior_idade = df1.loc[linhas,'Delivery_person_ID'].nunique()
    #.shape[0]
    #col1.metric(label=f'Maior idade :busts_in_silhouette:',value=maior_idade, delta=f'{nmaior_idade}: pessoas')

    return (maior_idade)


def melhor_condicao_veiculo (df1):
    melhor_veiculo = df1.loc[:,'Vehicle_condition'].max()
    #linhas = df1['Vehicle_condition']==melhor_veiculo
    #quantos veículos estam nessa condição
    #nmelhor_veiculo = df1.loc[linhas,'Delivery_person_ID'].nunique()

    return (melhor_veiculo)


def pior_condicao_veiculo (df1):
    pior_veiculo = df1.loc[:,'Vehicle_condition'].min()
    #linhas = df1['Vehicle_condition']==pior_veiculo
    #quantos veículos estam nessa condição
    #npior_veiculo = df1.loc[linhas,'Delivery_person_ID'].nunique()
    #col4.metric(label=f'Pior Condição :motor_scooter:',value=pior_veiculo, delta=f'{npior_veiculo}: veículos')

    return (pior_veiculo)

def aval_media_delivery (df1):
    #retorna a avaliação media por entregador    
    colunas = ['Delivery_person_ID','Delivery_person_Ratings']
    df_aux = (df1.loc[:,colunas]
              .groupby('Delivery_person_ID')
              .mean()
              .reset_index())
    
    return (df_aux)


def aval_media_transito (df1):
    # Avaliação media por tipo de Tránsito')
    colunas = ['Delivery_person_Ratings','Road_traffic_density']
    df_aux = (df1.loc[:,colunas]
              .groupby(['Road_traffic_density'])
              .agg({'Delivery_person_Ratings':['mean','std']})
              )
    #mudança de nome das colunas
    df_aux.columns =['Delivery_mean','Delivery_std']
    df_aux.reset_index()
    return(df_aux)



def top_asc_delivery (df1,type_asc):
    #a variavel type_asc recebe true - order ascending, False - order descending
    #top dos deliverys mas rapidos    
    colunas = ['City','Delivery_person_ID','Time_taken(min)']
    df_aux = df1.loc[:,colunas]
    df_aux = (df_aux.loc[:,colunas]
              .groupby(['City','Delivery_person_ID'])
              .min().sort_values('Time_taken(min)',ascending=type_asc)
              .reset_index())  
    df_city1 = df_aux.loc[(df_aux['City']=='Metropolitian'),:].head(10)
    df_city2 = df_aux.loc[(df_aux['City']=='Urban'),:].head(10)
    df_city3 = df_aux.loc[(df_aux['City']=='Semi-Urban'),:].head(10)
    df_citys = pd.concat([df_city1,df_city2,df_city3])
    df_citys.columns = ['City','Delivery_person_ID','MenorTempoEntrega']
    
    return (df_citys)    


def aval_media_clima(df1):
    #calculo de la media e desvio padrão por tipo de clima
    colunas = ['Delivery_person_Ratings','Weatherconditions']
    df_aux = (df1.loc[:,colunas]
              .groupby(['Weatherconditions'])
              .agg(['mean','std']))
    df_aux.reset_index()
    df_aux.columns =['Delivery_mean','Delivery_std']
    return (df_aux)



# =================================================
#     STREAMLIT--- SIDEBAR
# =================================================

st.header('Marketplace - Visão Entregadores')

#path for local use
#image_path = '/home/jlgarpas/Documents/repos/FTC-AD-COM-PYTHON/logo.png'
image_path = 'logo.png' #path for cloud
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

st.title('CRESCIMENTO DOS ENTREGADORES')

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','',''])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1,col2,col3,col4 = st.columns(4,gap='large')
        
        with col1:
            #A maior idade dos entregadores
            maior_idade = delivery_maior_idade (df1)
            col1.metric(label=f'Maior idade :busts_in_silhouette:',value=maior_idade)
            
        with col2:
            #A menor idade dos entregadores
            menor_idade = delivery_menor_idade(df1)
            col2.metric(label=f'Menor idade :busts_in_silhouette:',value=menor_idade)
                
        with col3:
            # A melhor condição de Veículo')
            melhor_veiculo = melhor_condicao_veiculo (df1)
            col3.metric(label=f'Melhor Condição :motor_scooter:',value=melhor_veiculo)
            
        with col4:
            #A Pior condição de Veículo
            
            pior_veiculo = pior_condicao_veiculo (df1)
            col4.metric(label=f'Pior Condição :motor_scooter:',value=pior_veiculo)    
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        with col1:
             with st.container():
                st.markdown('##### Avaliação media por Entregador')
                df_aux = aval_media_delivery (df1)
                st.dataframe(df_aux)
                
        with col2:
            with st.container():
                st.markdown('##### Avaliação media por tipo de Tránsito')
                df_aux = aval_media_transito (df1)
                st.dataframe(df_aux)
                
            with st.container():
            
                st.markdown('##### Avaliação media Condição Climática')
                df_aux = aval_media_clima(df1)
                st.dataframe(df_aux)
                

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        col1, col2 = st. columns(2)
        with col1:
            st.markdown(f'##### Top Entregadores mais Rápidos :first_place_medal:')
            df_aux = top_asc_delivery(df1,True)
            st.dataframe(df_aux)
        
        with col2:
            st.markdown(f'##### Top Entregadores mais Lentos :second_place_medal:')
            df_aux = top_asc_delivery(df1,False)
            st.dataframe(df_aux)

            
