import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pyvis.network import Network
import streamlit.components.v1 as components
from itertools import combinations
import re 
from one_gene_search import custom_sort_key

@st.cache_data
def custom_sort_key(file_name):
    """
    파일 이름을 기반으로 정렬하기 위한 사용자 정의 키 함수.
    먼저 조직 이름으로 정렬하고, 그 다음 LH, OH, OD 순서로 정렬한다.
    """
    for prefix in ['GeneExpressionZ_']:
        if file_name.startswith(prefix):
            file_name = file_name[len(prefix):]
            break

    parts = file_name.replace('.txt', '').split('_')
    tissue = parts[0]  # 조직 이름
    condition = parts[1]  # 상태

    # 순서 정의
    condition_order = {'LH': 1, 'OH': 2, 'OD': 3}

    return (tissue, condition_order.get(condition, 99))

def create_header():
    st.title('Multiple Gene Expression')
        
def show_heatmap(genes_list, base_path):
    if genes_list:
        file_list = os.listdir(base_path)
        sorted_files = sorted(file_list, key=custom_sort_key)

        modified_file_list = [
            file.replace('GeneExpressionZ_', '').replace('_', ' [')[:-4] + ']' if file.endswith('.txt') else file
            for file in sorted_files
            if file.endswith('.txt')
        ]

        total_files = len(modified_file_list)
        cols = 3
        rows = (total_files + cols - 1) // cols

        gene_height = 20
        max_genes_display = 40  # 최대로 표시할 유전자 수
        if len(genes_list) > max_genes_display:
            heatmap_height = max_genes_display * gene_height
            show_gene_labels = False  # 유전자 이름 표시 여부
        else:
            heatmap_height = len(genes_list) * gene_height
            show_gene_labels = True

        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=modified_file_list,
            horizontal_spacing=0.005,
            vertical_spacing=0.05
        )
        colorscale = [
            [0, "blue"],
            [1/6, "blue"],
            [1/2, "white"],
            [5/6, "red"],
            [1, "red"]
        ]

        for i, file in enumerate(sorted_files, start=1):
            if not file.endswith('.txt'):
                continue
            file_path = os.path.join(base_path, file)
            try:
                df = pd.read_csv(file_path, sep='\t', index_col='Gene name')
                heatmap_data = df.loc[genes_list]

                row = (i-1) // cols + 1
                col = (i-1) % cols + 1
                fig.add_trace(
                    go.Heatmap(
                        z=heatmap_data.values,
                        x=heatmap_data.columns.tolist(),
                        y=heatmap_data.index.tolist() if show_gene_labels else [],
                        colorscale=colorscale,
                        colorbar=dict(tickvals=[], ticktext=[]),
                    ),
                    row=row, col=col
                )

                if col == 1 and show_gene_labels:
                    fig.update_yaxes(row=row, col=col)
                else:
                    fig.update_yaxes(showticklabels=False, row=row, col=col)

            except FileNotFoundError:
                st.error(f'File not found: {file}')
            except KeyError:
                st.error(f'One or more genes not found in file: {file}')

        total_height = heatmap_height * rows

        fig.update_layout(
            width=900,
            height=max(total_height, 600),  
            title_text='Heatmaps for All Files in Z_Score Directory',
            showlegend=False,
        )

        fig.update_xaxes(showticklabels=False)
        st.plotly_chart(fig)
    else:
        st.error('Please enter at least one gene name.')

def show_interaction(genes_list):
    with st.spinner('그래프를 그리는 중입니다...'):
        folder_path = './data/Gene-Gene Interaction/BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'
        data = pd.read_csv(folder_path, sep='\t')
        df = pd.DataFrame(data)

        net = Network(notebook=True, directed=False)

        # 그룹 선택 및 threshold 입력
        sample_class = ['Adipose_LH', 'Adipose_OH', 'Adipose_OD', 'Liver_LH', 'Liver_OH', 'Liver_OD', 'Muscle_LH', 'Muscle_OH', 'Muscle_OD']
        group = st.selectbox('Choose one group', sample_class, key='sample_input')
        threshold = st.number_input('Enter threshold:', min_value=0.0, value=0.5, step=0.01)

        # Correlation 데이터 로드
        df_correlation_filtered = load_correlation_data(group, threshold)

        for gene_pair in combinations(genes_list, 2):
            interactions = df[((df['Official Symbol Interactor A'] == gene_pair[0]) & (df['Official Symbol Interactor B'] == gene_pair[1])) |
                            ((df['Official Symbol Interactor A'] == gene_pair[1]) & (df['Official Symbol Interactor B'] == gene_pair[0]))]
            if not interactions.empty:
                net.add_node(gene_pair[0], label=gene_pair[0], title=gene_pair[0], size=15, color='grey')
                net.add_node(gene_pair[1], label=gene_pair[1], title=gene_pair[1], size=15, color='grey')

                correlation = df_correlation_filtered[(df_correlation_filtered['Gene'] == gene_pair[0]) & (df_correlation_filtered['Gene.1'] == gene_pair[1]) | (df_correlation_filtered['Gene'] == gene_pair[1]) & (df_correlation_filtered['Gene.1'] == gene_pair[0])]
                if not correlation.empty:
                    color = 'red' if correlation['Correlation coefficient'].values[0] > 0 else 'blue'
                else:
                    color = 'lightgrey'  

                net.add_edge(gene_pair[0], gene_pair[1], color=color)

        # 네트워크 그리기
        net.show_buttons(filter_=['physics'])
        net.show("pyvis_net_graph.html")

        HtmlFile = open('pyvis_net_graph.html', 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, width=670, height=1070)
    
def load_correlation_data(group, threshold):
    file_path = f'data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_{group}_0.5.txt'
    df_correlation = pd.read_csv(file_path, sep='\t')
    df_correlation_filtered = df_correlation[df_correlation['Correlation coefficient'].abs() >= threshold]
    return df_correlation_filtered

def write_gene_list_page():    
    create_header()
    
    genes_input = st.text_area('Enter gene names:')
    genes_list = re.split('[ ,\t\n]+', genes_input.strip())
    
    st.write(f"Number of genes entered: {len(genes_list)}")  # Debug print
    base_path = 'data/Gene Expression/Z_Score'

    if st.button('Search'):
        show_heatmap(genes_list, base_path)
        show_interaction(genes_list)
