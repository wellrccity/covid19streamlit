import pandas as pd
import plotly.express as px
import streamlit as st 
import base64
import io

# Carrega o dataset
df = pd.read_csv('https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv')

# Renomeia as colunas da tabela
df = df.rename(columns={'newDeaths': 'Novos óbitos',
                        'newCases': 'Novos casos',
                        'deaths_per_100k_inhabitants': 'Óbitos por 100 mil habitantes',
                        'totalCases_per_100k_inhabitants': 'Casos por 100 mil habitantes'})

# Cria uma lista de estados para a seleção do usuário
estados = list(df['state'].unique())

# Adiciona uma barra lateral para a seleção do usuário
state = st.sidebar.selectbox('Selecione o estado:', estados)
colunas = ['Novos óbitos', 'Novos casos', 'Óbitos por 100 mil habitantes', 'Casos por 100 mil habitantes']
column = st.sidebar.selectbox('Selecione o tipo de informação:', colunas)

# Adiciona opções para selecionar o período desejado
min_date = pd.to_datetime(df['date'].min())
max_date = pd.to_datetime(df['date'].max())
start_date = st.sidebar.date_input('Data de início:', min_date)
end_date = st.sidebar.date_input('Data final:', max_date)

# Filtra as linhas do dataframe para o estado selecionado e o período selecionado
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)
mask = (df['state'] == state) & (pd.to_datetime(df['date']) >= start_date) & (pd.to_datetime(df['date']) <= end_date)
df = df.loc[mask]

# Verifica se o usuário selecionou um estado e um tipo de informação
if not state or not column:
    st.warning('Por favor, selecione um estado e um tipo de informação.')
else:
    # Cria um gráfico de linha do tipo de informação selecionado para o estado selecionado
    fig = px.line(df, x='date', y=column, title=column + ' - ' + state)
    fig.update_layout(xaxis_title='Data', yaxis_title=column.upper(), title={'x': 0.5})

# Adiciona opções para selecionar o tipo de gráfico desejado
tipos_grafico = ['Gráfico de linha', 'Gráfico de barras']
tipo_grafico = st.sidebar.selectbox('Selecione o tipo de gráfico:', tipos_grafico)
if tipo_grafico == 'Gráfico de barras':
    fig = px.bar(df, x='date', y=column, title=column + ' - ' + state)
    fig.update_layout(xaxis_title='Data', yaxis_title=column.upper(), title={'x': 0.5})

# Adiciona um botão para baixar os dados em formato CSV ou Excel
download_formato = st.sidebar.selectbox('Selecione o formato de download:', ['CSV', 'Excel'])
if st.sidebar.button('Baixar dados'):
    if download_formato == 'CSV':
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{state}_{column}.csv">Download CSV</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)
    elif download_formato == 'Excel':
        excel_io = io.BytesIO()
        excel_writer = pd.ExcelWriter(excel_io, engine='xlsxwriter')
        df.to_excel(excel_writer, index=False)
        excel_writer.save()
        excel_io.seek(0)
        b64 = base64.b64encode(excel_io.read()).decode()
        href = f'<a href="data:file/excel;base64,{b64}" download="{state}_{column}.xlsx">Download Excel</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)

# Mostra o gráfico
st.title('Dados COVID - Brasil')
st.write('Nessa aplicação, o usuário tem a opção de escolher o estado, o tipo de informação e o período para mostrar o gráfico. Utilize o menu lateral para alterar a mostragem.')
st.plotly_chart(fig, use_container_width=True)

st.caption('Os dados foram obtidos a partir do site: https://github.com/wcota/covid19br')

