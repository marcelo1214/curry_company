# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import folium
import pandas as pd
import streamlit as st
import datetime as dt
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide' )

# ---------------------------------
# Funções
# ---------------------------------
def top_delivers( df1, top_asc ):
    df2 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
               .groupby( ['City', 'Delivery_person_ID'] )
               .mean()
               .sort_values( ['City', 'Time_taken(min)'], ascending=top_asc ).reset_index() )

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop=True )

    return df3
            
            
def clean_code( df1 ): 
    """ Esta funcao tem a responsabilidade de limpar o dataframe 
    
        Tipos de limpeza:
        1. Removação dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Removação dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )
        
        Input: Dataframe
        Output: Dataframe
    """
    
    # 1. convertando a coluna Age de texto para numero
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # 2. convertando a coluna Ratings de texto para numero decimal ( float )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # 3. convertando a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # 4. convertendo multiple_deliveries de texto para numero inteiro ( int )
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # 6. Removendo os espacos dentro de strings/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 7. Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)']  = df1['Time_taken(min)'].astype( int )
    
    return df1


# Import dataset
df = pd.read_csv( 'food_delivery_train.csv' )

# cleaning dataset
df1 = clean_code( df )


# =======================================
# Barra Lateral
# =======================================
st.header( 'Marketplace - Visão Entregadores' )

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual data deseja analisar?',
    value=dt.datetime(2022, 4, 13),
    min_value=dt.datetime(2022, 2, 11),
    max_value=dt.datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

st.sidebar.markdown( """---""" )


traffic_options = st.sidebar.multiselect( 
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'], 
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """---""" )
weather_options = st.sidebar.multiselect( 
    'Quais as condições do clima',
    ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'], 
    default=['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'] )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '#### Created by Marcelo Brandão' )

# Filtro de data
linhas_selecionadas = df1['Order_Date'] <  date_slider 
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]


# Filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin( weather_options )
df1 = df1.loc[linhas_selecionadas, :]

# =======================================
# Layout no Streamlit
# =======================================
#tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

#with tab1:
with st.container():
    st.markdown( """---""" )
    st.title( 'Overall Metrics' )

    col1, col2, col3, col4 = st.columns( 4, gap='large' )
    with col1:
        # A maior idade dos entregadores
        maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
        col1.metric( 'Maior de idade', maior_idade )


    with col2:
        # A menor idade dos entregadores
        menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
        col2.metric( 'Menor idade', menor_idade )

    with col3:
        # A maior idade dos entregadores
        melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
        col3.metric( 'Melhor condição', melhor_condicao )

    with col4:
        # A menor idade dos entregadores
        pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
        col4.metric( 'Pior condição', pior_condicao )

with st.container():
    st.markdown( """---""" )
    st.title( 'Avaliacoes' )

    col1, col2 = st.columns( 2 )
    with col1:
        st.markdown( '##### Avalicao média por Entregador' )
        df_avg_ratings_per_deliver = ( df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                          .groupby( 'Delivery_person_ID' )
                                          .mean()
                                          .reset_index() )
        st.dataframe( df_avg_ratings_per_deliver )

    with col2:
        st.markdown( '##### Avaliacao média por transito' )
        df_avg_std_rating_by_traffic = ( df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                            .groupby( 'Road_traffic_density')
                                            .agg( {'Delivery_person_Ratings': ['mean', 'std' ]} ) )

        # mudanca de nome das colunas
        df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

        # reset do index
        df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
        st.dataframe( df_avg_std_rating_by_traffic )



        st.markdown( '##### Avaliacao média por clima' )
        df_avg_std_rating_by_weather = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                            .groupby( 'Weatherconditions')
                                            .agg( {'Delivery_person_Ratings': ['mean', 'std']} ) )

        # mudanca de nome das colunas
        df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']

        # reset do index
        df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
        st.dataframe( df_avg_std_rating_by_weather )


with st.container():
    st.markdown( """---""" )
    st.title( 'Velocidade de Entrega' )

    col1, col2 = st.columns( 2 )

    with col1:
        st.markdown( '##### Top Entregadores mais rapidos' )
        df3 = top_delivers( df1, top_asc=True )
        st.dataframe( df3 )

    with col2:
        st.markdown( '##### Top Entregadores mais lentos' )
        df3 = top_delivers( df1, top_asc=False )
        st.dataframe( df3 )