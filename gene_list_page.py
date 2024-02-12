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

        # 파일 이름을 원하는 형식으로 변환
        modified_file_list = [
            file.replace('GeneExpressionZ_', '').replace('_', ' [')[:-4] + ']' if file.endswith('.txt') else file
            for file in sorted_files
            if file.endswith('.txt')
        ]

        total_files = len(modified_file_list)
        cols = 3  
        rows = (total_files + cols - 1) // cols

        fig = make_subplots(
            rows=rows, 
            cols=cols, 
            subplot_titles=modified_file_list,
            horizontal_spacing=0.005,  # 간격 조정
            vertical_spacing=0.05
        )

        for i, file in enumerate(file_list, start=1):
            file_path = os.path.join(base_path, file)
            try:
                df = pd.read_csv(file_path, sep='\t', index_col='Gene name')
                heatmap_data = df.loc[genes_list]

                fig.add_trace(
                    go.Heatmap(
                        z=heatmap_data.values, 
                        x=heatmap_data.columns.tolist(), 
                        y=heatmap_data.index.tolist(), 
                        colorscale='Purples',
                        colorbar_tickvals=[],  # 컬러바의 틱 값을 빈 리스트로 설정하여 숫자를 제거
                        colorbar_ticktext=[]   # 컬러바의 틱 텍스트를 빈 리스트로 설정하여 숫자를 제거
                    ),
                    row=(i-1)//cols + 1, col=(i-1)%cols + 1
                )
            except FileNotFoundError:
                st.error(f'File not found: {file}')
            except KeyError:
                st.error(f'One or more genes not found in file: {file}')

        fig.update_layout(
            width=900, 
            height=300 * rows, 
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

        # NetworkX 그래프 생성
        net = Network(
            notebook=True,
            directed=False,
        )

        for gene_pair in combinations(genes_list, 2):
            # gene_pair의 상호 작용을 데이터프레임에 추가
            interactions = df[((df['Official Symbol Interactor A'] == gene_pair[0]) & (df['Official Symbol Interactor B'] == gene_pair[1])) |
                            ((df['Official Symbol Interactor A'] == gene_pair[1]) & (df['Official Symbol Interactor B'] == gene_pair[0]))]
            if not interactions.empty:
                # 노드 추가
                net.add_node(gene_pair[0], label=gene_pair[0], title=gene_pair[0], size=15)
                net.add_node(gene_pair[1], label=gene_pair[1], title=gene_pair[1], size=15)
                # 엣지 추가
                net.add_edge(gene_pair[0], gene_pair[1], color='skyblue')

    # 네트워크 그리기
    net.show_buttons(filter_=['physics'])
    net.show("pyvis_net_graph.html")

    # html 파일 페이지에 나타내기
    HtmlFile = open('pyvis_net_graph.html', 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, width=670, height=1070)

def write_gene_list_page():    
    create_header()
    
    genes_input = st.text_area('Enter gene names:')
    # 여러 구분자 처리
    genes_list = re.split('[ ,\t\n]+', genes_input.strip())
    
    
    st.write(f"Number of genes entered: {len(genes_list)}")  # Debug print
    base_path = 'data/Gene Expression/Z_Score'

    if st.button('Search'):
        show_heatmap(genes_list, base_path)
        show_interaction(genes_list)