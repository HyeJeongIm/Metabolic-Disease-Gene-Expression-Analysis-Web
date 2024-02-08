import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np

def create_header():
    st.title('DEG Analysis')

def create_search_area():
    # selectbox를 위한 값 선언
    sample_class = ['AdiposeLH', 'AdiposeOH', 'AdiposeOD',
              'LiverLH', 'LiverOH', 'LiverOD',
              'MuscleLH', 'MuscleOH', 'MuscleOD']
    p_value = [0.05, 0.01, 0.001]
    fold_change = [1.5, 2, 3]
    pathway = ['Pathway', 'Go', 'Hallmark']

    # search box들
    sample_choice = st.multiselect('Choose two groups', sample_class, max_selections=2, key='sample_input')
    p_value_choice = st.selectbox('Choose the p-value', p_value, key='p_value_input')
    fold_change_choice = st.selectbox('Choose the Fold-change', fold_change, key='fold_change_input')
    pathway_choice = st.multiselect('Choose the pathway', pathway, key='pathway_input')

    if st.button('Search'):
        plot_pca(sample_choice)
        plot_volcano(sample_choice, p_value_choice, fold_change_choice)

    # session_state 때문에 죽여둠
    # if st.button('Search'):
    #     st.session_state['search_pressed'] = True
        
    # 검색이 수행된 후에만 수행
    # if 'search_pressed' in st.session_state and st.session_state['search_pressed']:
    #     plot_pca(sample_choice)
    #     plot_volcano(sample_choice, p_value_choice, fold_change_choice)

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
    # Volcano에 사용할 데이터 파일 불러오기
    result_path = f'./data/DEG Result/DEGResult_{sample_choice[0]}_VS_{sample_choice[1]}.txt'
    
    # 데이터 파일 존재하지 않을 때
    if not os.path.exists(result_path):
        result_path = f'./data/DEG Result/DEGResult_{sample_choice[1]}_VS_{sample_choice[0]}.txt'

        # csv로 읽기
        data_result = pd.read_csv(result_path, sep='\t')
        df = pd.DataFrame(data_result)

        # p-value에 -log10 적용하기
        df['FDR-adjusted p-value'] = -np.log10(df['FDR-adjusted p-value'])

        # Log2 Fold change 값 변경하기
        df['Log2FoldChange'] = 1/ (2**(df['Log2FoldChange']))
        df['Log2FoldChange'] = -np.log2(df['Log2FoldChange'])
    else:
        # csv로 읽기
        data_result = pd.read_csv(result_path, sep='\t')
        df = pd.DataFrame(data_result)

        # p-value에 -log10 적용하기
        df['FDR-adjusted p-value'] = -np.log10(df['FDR-adjusted p-value'])

    # threshold 설정
    threshold_fold = -np.log2(fold_change_choice)
    threshold_p = -np.log10(p_value_choice)

    df['Class'] = 'NoDiff'
    df.loc[(df['Log2FoldChange'] > -threshold_fold) & (df['FDR-adjusted p-value'] > threshold_p), 'Class'] = 'Fold up'
    df.loc[(df['Log2FoldChange'] < threshold_fold) & (df['FDR-adjusted p-value'] > threshold_p), 'Class'] = 'Fold down'

    # Volcano 그리기
    st.subheader(f'Volcano Plot')
    st.write(f'Criteria: {sample_choice[0]}')
    fig = px.scatter(
        data_frame=df, 
        x='Log2FoldChange', 
        y='FDR-adjusted p-value',  
        color='Class',
        color_discrete_map={'NoDiff': 'lightgray', 'Fold up': '#f48db4', 'Fold down': '#9cd3d3'},
        color_discrete_sequence = px.colors.qualitative.Pastel1,
        hover_data={'Class': False},
        )
    fig.add_shape(
        dict(
            type='line',
            x0=threshold_fold,
            x1=threshold_fold,
            y0=0,
            y1=max(df['FDR-adjusted p-value']),
            line=dict(color='gray', dash='dash')
        )
    )
    fig.add_shape(
    dict(
        type='line',
        x0=-threshold_fold,
        x1=-threshold_fold,
        y0=0,
        y1=max(df['FDR-adjusted p-value']),
        line=dict(color='gray', dash='dash')
        )
    )
    fig.add_shape(
    dict(
        type='line',
        x0=min(df['Log2FoldChange']),
        x1=max(df['Log2FoldChange']),
        y0=threshold_p,
        y1=threshold_p,
        line=dict(color='gray', dash='dash')
        )
    )
    fig.update_layout(
        xaxis_title="Log2 fold change",
        yaxis_title="-Log10 adjusted P",
        # showlegend=False,
    )
    st.plotly_chart(fig)

    show_table(df)

def show_table(df):
    filtered_df = df[df['Class'].isin(['Fold up', 'Fold down'])]
    filtered_df= filtered_df.sort_values(by='FDR-adjusted p-value', ascending=True)

    st.dataframe(filtered_df.style.apply(color_rows, axis=1), width=1000)

def color_rows(row):
    if row['Class'] == 'Fold up':
        return ['background-color: #f48db4'] * len(row)
    elif row['Class'] == 'Fold down':
        return ['background-color: #9cd3d3'] * len(row)
    else:
        return [''] * len(row)


def write_deg_page():
    create_header()
    create_search_area()