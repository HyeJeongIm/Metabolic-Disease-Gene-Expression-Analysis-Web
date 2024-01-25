import streamlit as st
import pandas as pd
import plotly.express as px
import os

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
        plot_pca(sample_choice)
        plot_volcano(sample_choice, p_value_choice, fold_change_choice)

def plot_pca(sample_choice):
    # PCA에 사용할 데이터 파일 불러오기
    coordinate_path = f'./data/PCA/PCACoordinate_{sample_choice[0]}_VS_{sample_choice[1]}.txt'
    variance_path = f'./data/PCA/PCAVarianceExplained_{sample_choice[0]}_VS_{sample_choice[1]}.txt'

    # 데이터 파일 존재하지 않으면 경로 다시 설정
    if not os.path.exists(coordinate_path) and not os.path.exists(variance_path):
        coordinate_path = f'./data/PCA/PCACoordinate_{sample_choice[1]}_VS_{sample_choice[0]}.txt'
        variance_path = f'./data/PCA/PCAVarianceExplained_{sample_choice[1]}_VS_{sample_choice[0]}.txt'
    
    # csv로 읽기
    data_coordinate = pd.read_csv(coordinate_path, sep='\t')
    data_variance = pd.read_csv(variance_path, sep='\t', header=None)

    # variance값 반올림
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

def plot_volcano(sample_choice, p_value_choice, fold_change_choice):
    st.write(sample_choice)
    st.write(p_value_choice)
    st.write(fold_change_choice)
        
def write_deg_page():
    create_header()
    create_search_area()