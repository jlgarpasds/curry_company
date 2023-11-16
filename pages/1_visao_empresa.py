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

st.set_page_config(page_title='Visão Empresa', layout='wide')


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


def metrics_orders_by_date(df1):
    #Funçao retorna um grafico de barras - Quantidade de pedidos por día
    colunas = ['ID','Order_Date']
    df_aux = df1.loc[:,colunas].groupby(['Order_Date']).count().reset_index()
    df_aux.columns=['Order_Date','qtd_pedidos']
    fig = px.bar(df_aux,x='Order_Date',y='qtd_pedidos',color='qtd_pedidos',title='Quantidade de Pedidos por día')
    return fig

def traffic_order(df1):
    # Função que retorna um grafico tipo pie - (%) Distribuição dos pedidos por tipo de tráfego    
    colunas = ['ID','Road_traffic_density']
    df_aux = (df1.loc[:,colunas]
                  .groupby(['Road_traffic_density'])
                  .count()
                  .reset_index())
    df_aux.columns =['Traffic_density','qt_pedidos']
    df_aux['entregas_perc']= (df_aux['qt_pedidos'] / df_aux['qt_pedidos'].sum()) 
    fig = px.pie( df_aux, values='entregas_perc', names='Traffic_density', title='(%) Distribuição dos pedidos por tipo de trâfego. ')
    return fig             


def traffic_order_city(df1):
    # Função que retorna um grafico tipo scatter - Comparação do volume de pedidos por cidade e por tipo de trâfego'
    colunas = ['ID','City', 'Road_traffic_density']
    df_aux = df1.loc[:,colunas].groupby(['City', 'Road_traffic_density']).count().reset_index()
    df_aux.columns =['City','Traffic_Density','Qt_pedidos']         
    fig = (px.scatter(df_aux,x='City', 
                              y='Traffic_Density',
                              size='Qt_pedidos',
                              color='Traffic_Density',
                              title='Comparação do volume de pedidos por cidade e por tipo de trâfego'))
    return fig


def orders_by_week(df1):
    # função retorno um gráfico tipo line - quantidade de pedidos por semana
    
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux=df1.loc[:,['ID','Week_of_year']].groupby(['Week_of_year']).count().reset_index()
    df_aux.columns = ['Week_of_year','qt_pedidos_semana']
    fig = px.line(df_aux,x='Week_of_year',y='qt_pedidos_semana')
    
    return fig

def orders_by_delivery_week(df1):
    #Função retorna um grafico tipo line, Quantidade de entregadores unicos x semana
    cols = ['ID','Week_of_year']
    df_aux1 = df1.loc[:,cols].groupby('Week_of_year').count().reset_index()  #quantidade de pedidos por semana
    df_aux1.columns=['Week_of_year', 'Qpedidos']
    cols = ['Delivery_person_ID','Week_of_year']
    df_aux2= df1.loc[:,cols].groupby('Week_of_year').nunique().reset_index() #quantidade entreg unicos x semana
    df_aux = pd.merge(df_aux1,df_aux2,how='inner')
    df_aux['Order_by_delivery'] = df_aux['Qpedidos'] / df_aux['Delivery_person_ID']
    fig=px.line(df_aux,x='Week_of_year',y='Order_by_delivery')
    
    return fig


def country_maps(df1):
#função que grafica e posiciona no mapa mundi a ubição das cidades de entrega 
    cols = ['City','Delivery_location_latitude','Delivery_location_longitude','Road_traffic_density']
    df_aux = (df1.loc[:,cols]
              .groupby(['City','Road_traffic_density'])
              .median()
              .reset_index())
    mymap = folium.Map()

    
    for index,location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                      popup=location_info[['City','Road_traffic_density']],
                      tiles="OpenStreetMap").add_to(mymap)
        
    #old folium_static(mymap, width=1024, height=600)
    st_folium(mymap, width = 1024,height=600)
    #return none


# =================================================
#     ESTRUTURA LOGICA DO CODIGO
# =================================================
df1=clean_dfCury(df)

# -------------------------------------------------
#     STREAMLIT--- SIDEBAR
# -------------------------------------------------

st.header('Marketplace - Visão Empresa')

img_path = 'logo.png'
image = Image.open(img_path)

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

st.sidebar.markdown ("""---""")

# pie de sidebar
st.sidebar.markdown('### Powered by ComunidadeDS')

# -------------------------------------------------
# VINCULAÇÃO DOS ELEMENTOS DO SIDEBAR AO DATASET
# -------------------------------------------------

date_slider = np.datetime64(date_slider)  #conversao de dados

linhas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas,:]

linhas = df1['Road_traffic_density'].isin(transito_slider)
df1 = df1.loc[linhas,:]

# -------------------------------------------------
#     STREAMLIT --- LAYOUT CENTRAL
# -------------------------------------------------

tab1, tab2, tab3 = st.tabs(["Visão Gerencial", "Visão Tática", "Visão Geogrâfica"])
with tab1: 
    with st.container():
        #order_metric
        fig = metrics_orders_by_date(df1)
        st.plotly_chart(fig, use_container_width=True)  # plotly_chart() função propia do Streamlit
        
    with st.container():
        col1,col2 = st.columns(2)
        with col1:
            #traffic_order -- (%) Distribuição dos pedidos por tipo de tráfego
            fig = traffic_order(df1)
            st.plotly_chart(fig, use_container_width=True) 
            #plotly_chart() função propia do Streamlit use_container_wit=True)            
            
        with col2:
            #Comparação do volume de pedidos por cidade e por tipo de trâfego')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True) 
            #plotly_chart() função propia do Streamlit use_container_wit=True) 
            
with tab2:
    
    with st.container():
        #Orders_by_week
        fig = orders_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():    
        #Orders by Week - Entregadores Unicos.
        fig = orders_by_delivery_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
with tab3:
    #delivery location
    # como determinamos a localização central?
    country_maps(df1)
