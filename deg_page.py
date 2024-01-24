import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def create_header():
    st.title('DEG Analysis')

def create_search_area():
    # selectbox를 위한 값 선언
    sample_class = [
        'AdiposeLH', 'AdiposeOH', 'AdiposeOD',
        'LiverLH', 'LiverOH', 'LiverOD',
        'MuscleLH', 'MuscleOH', 'MuscleOD',
        ]
    p_value = [0.05, 0.01, 0.001]
    fold_change = ['1.5 fold', '2 fold', '3 fold']
    pathway = ['Pathway', 'Go', 'Hallmark']

    # search box들
    sample_choice = st.multiselect('Choose the samples', sample_class, key='sample_input')
    p_value_choice = st.selectbox('Choose the p-value', p_value, key='p_value_input')
    fold_change_choice = st.selectbox('Choose the Fold-change', fold_change, key='fold_change_input')
    pathway_choice = st.selectbox('Choose the pathway', pathway, key='pathway_input')

    if st.button('Search'):
        st.session_state['search_pressed'] = True

    if 'search_pressed' in st.session_state and st.session_state['search_pressed']:
        plot_pca(sample_choice)

def plot_pca(sample_choice):
    # PCA에 사용할 데이터 파일 불러오기
    coordinate_path = f'./data/PCA/PCACoordinate_{sample_choice[0]}_VS_{sample_choice[1]}.txt'
    data_coordinate = pd.read_csv(coordinate_path, sep='\t')

    variance_path = f'./data/PCA/PCAVarianceExplained_{sample_choice[0]}_VS_{sample_choice[1]}.txt'
    data_variance = pd.read_csv(variance_path, sep='\t', header=None)

    pc1 = round(data_variance[0][0], 1)
    pc2 = round (data_variance[1][0], 1)

    # PCA 그리기
    st.subheader('PCA Plot')
    fig = px.scatter(
        data_frame=data_coordinate, 
        x='1st PC (X-axis)', 
        y='2nd PC (Y-axis)', 
        labels={'1st PC (X-axis)': f'PC1 ({pc1}% variance)', '2nd PC (Y-axis)': f'PC2 ({pc2}% variance)'},
        color='SampleGroup', 
        symbol='SampleGroup',
        color_discrete_sequence = px.colors.qualitative.Pastel1,
        )
    st.plotly_chart(fig)

        
def write_deg_page():
    create_header()
    create_search_area()