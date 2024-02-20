import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
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
        plot_pathway(sample_choice[0], sample_choice[1], p_value_choice, fold_change_choice, pathway_choice)

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

    df['DEG Group'] = 'No significant change'
    df.loc[(df['Log2FoldChange'] > -threshold_fold) & (df['FDR-adjusted p-value'] > threshold_p), 'DEG Group'] = 'Up-regulated'
    df.loc[(df['Log2FoldChange'] < threshold_fold) & (df['FDR-adjusted p-value'] > threshold_p), 'DEG Group'] = 'Down-regulated'

    # Volcano 그리기
    st.subheader(f'Volcano Plot')

    # 기준 수정
    group = sample_choice[0][:-2] + ' [' + sample_choice[0][-2:] + ']'
    st.write(f'Group: {group}')
    fig = px.scatter(
        data_frame=df, 
        x='Log2FoldChange', 
        y='FDR-adjusted p-value',  
        color='DEG Group',
        color_discrete_map={'No significant change': 'lightgray', 'Up-regulated': '#f48db4', 'Down-regulated': '#9cd3d3'},
        color_discrete_sequence = px.colors.qualitative.Pastel1,
        hover_data={'DEG Group': False},
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
        xaxis_title="Log<sub>2</sub> (fold change)",
        yaxis_title="-Log<sub>10</sub> (adjusted P)",
    )
    st.plotly_chart(fig)

    show_table(df)
    plot_heatmap(df, sample_choice)

def show_table(df):
    st.write('DEG List')

    filtered_df = df[df['DEG Group'].isin(['Up-regulated', 'Down-regulated'])]
    filtered_df = filtered_df.drop(columns=['DEG Group'])
    filtered_df= filtered_df.sort_values(by='FDR-adjusted p-value', ascending=True)

    # p-value 값 다시 가져오기
    filtered_df['FDR-adjusted p-value'] = 10**(-filtered_df['FDR-adjusted p-value'])

    # p-value를 지수 형식으로 변환
    filtered_df['FDR-adjusted p-value'] = filtered_df['FDR-adjusted p-value'].apply(lambda x: format(x, '.6e'))

    # 인덱스 재설정 및 인덱스 값 조정
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.index += 1
    
    # 컬럼명 변경
    filtered_df = filtered_df.rename(columns={'Log2FoldChange' : 'Log₂ Fold-change', 'FDR-adjusted p-value' : 'P-value'})

    st.dataframe(filtered_df.style.apply(color_rows, axis=1), width=600, hide_index=True)

def color_rows(row):
    if row['Log₂ Fold-change'] > 0:
        return ['background-color: #f48db4'] * len(row)
    elif row['Log₂ Fold-change'] < 0:
        return ['background-color: #9cd3d3'] * len(row)
    else:
        return [''] * len(row)
    
def plot_heatmap(df, sample_choice):
    st.subheader('Heatmap')

    # 데이터프레임 전처리
    filtered_df = df[df['DEG Group'].isin(['Up-regulated', 'Down-regulated'])]
    filtered_df = filtered_df.rename(columns={'Gene' : 'Gene name'})
    filtered_df = filtered_df.sort_values(by='DEG Group', ascending=True)

    # 파일 경로 일반화
    modified_path = sample_choice[0][:-2] + '_' + sample_choice[0][-2:]
    file_path = f'./data/Gene Expression/Z_Score/GeneExpressionZ_{modified_path}.txt'

    heatmap_data = pd.read_csv(file_path, sep='\t')
    df_heatmap = pd.DataFrame(heatmap_data)

    # 히트맵 그릴 데이터프레임
    merged_df = pd.merge(df_heatmap, filtered_df, on='Gene name', how='inner')
    merged_df = merged_df.drop(columns=['Log2FoldChange', 'FDR-adjusted p-value'])
    # merged_df.set_index('Gene name', inplace=True)
    merged_df = merged_df.sort_values(by='DEG Group', ascending=True)

    colorscale = [
            [0, "blue"],
            [1/6, "blue"],
            [1/2, "white"],
            [5/6, "red"],
            [1, "red"]
        ]

    # 히트맵 그리기
    fig = go.Figure(data=go.Heatmap(
        z=merged_df.drop(columns=['Gene name']).values,
        x=merged_df.columns[1:],
        y=merged_df['Gene name'],
        colorscale=colorscale
    ))

    # 레이아웃 설정
    fig.update_layout(
        xaxis_title='Samples',
        yaxis_title='Gene name',
        height=800,
        width=800
    )
    st.plotly_chart(fig)


def plot_pathway(group1, group2, p_value, fold_change, categories):
    base_path = "data/DEG Pathway Enrichment Result/"
    file_suffix = f"{group1}_VS_{group2}_p{p_value}_fc{fold_change}"

    def format_group_name(name):
        # 그룹 이름의 마지막 2글자를 대괄호로 묶어서 반환
        if len(name) > 2:
            return f"{name[:-2]} [{name[-2:]}]"
        else:
            return name

    # 결과를 category별로 그룹화하여 표시하기 위해 순서 변경
    for group_label in ["All", group1, group2]:
        if group_label == "All":
            st.write(f"## {group_label} Group")
        else:
            st.write(f"## {format_group_name(group_label)} Group")
        for category in categories:
            file_path = f"{base_path}DEGPathwayEnrichment_{file_suffix}_{group_label}.txt"
            try:
                data = []  
                with open(file_path, 'r') as file:
                    for line in file:
                        parts = line.strip().split('\t')
                        if len(parts) >= 8:
                            data.append(parts[:8])
                columns = data[0]  # 첫 줄을 컬럼명으로 사용
                df = pd.DataFrame(data[1:], columns=columns)  
                df = df.drop(columns=['Size (overlapping with base)'])  # 'Size (overlapping with base)' 컬럼 제외

                st.write(f"### Category: {category}")
                st.dataframe(
                    df, 
                    hide_index=True, 
                    column_config={
                        'URL': st.column_config.LinkColumn('URL')
                })
            except FileNotFoundError:
                st.error(f"File not found: {file_path}")

### 같은 category에 대해 "All", group1, group2 순서대로 결과를 표시
# def plot_pathway(group1, group2, p_value, fold_change, categories):
#     base_path = "data/DEG Pathway Enrichment Result/"
#     file_suffix = f"{group1}_VS_{group2}_p{p_value}_fc{fold_change}"
#     group_labels = ["All", group1, group2]

#     for category in categories:
#         for group_label in group_labels:
#             file_path = f"{base_path}DEGPathwayEnrichment_{file_suffix}_{group_label}.txt"
#             try:
#                 data = []  # 데이터를 저장할 리스트
#                 with open(file_path, 'r') as file:
#                     for line in file:
#                         parts = line.strip().split('\t')
#                         # 첫 8개 컬럼만 추출 (더 많은 컬럼이 있으면 무시)
#                         if len(parts) >= 8:
#                             data.append(parts[:8])
#                 columns = data[0]
#                 df = pd.DataFrame(data[1:], columns=columns)
#                 df = df.drop(columns=['Size (overlapping with base)'])  # Size 컬럼 제외
#                 st.write(f"### {category} Enrichment for {group_label}")
#                 st.dataframe(df)  # 데이터 프레임 표시
#             except FileNotFoundError:
#                 st.error(f"File not found: {file_path}")  

def write_deg_page():
    create_header()
    create_search_area()