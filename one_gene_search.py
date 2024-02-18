import pandas as pd
import plotly.express as px
from pyvis.network import Network
import streamlit.components.v1 as components
import streamlit as st
import os
import re
from itertools import combinations

'''
    Box Plot
'''

@st.cache_data
def load_data(file_path, name):
    df = pd.read_csv(file_path, sep='\t')
    one_gene_df = df[df['Gene name'] == name].drop('Gene name', axis=1).T
    one_gene_df.columns = [name]
    return one_gene_df

@st.cache_data
def custom_sort_key(file_name):
    """
    파일 이름을 기반으로 정렬하기 위한 사용자 정의 키 함수.
    먼저 조직 이름으로 정렬하고, 그 다음 LH, OH, OD 순서로 정렬한다.
    """
    for prefix in ['GeneExpression_', 'GeneExpressionZ_']:
        if file_name.startswith(prefix):
            file_name = file_name[len(prefix):]
            break

    parts = file_name.replace('.txt', '').split('_')
    tissue = parts[0]  # 조직 이름
    condition = parts[1]  # 상태

    # 순서 정의
    condition_order = {'LH': 1, 'OH': 2, 'OD': 3}

    return (tissue, condition_order.get(condition, 99))
def plot_data(combined_df):
    fig = px.box(combined_df, x='file', y='value', color='file', 
                 labels={'value': 'Expression Level', 'file': 'Tissue [Disease status]'})
    fig.update_layout(showlegend=False)  
    st.plotly_chart(fig, use_container_width=True)
    
def show_box_plot(name, z_score=False):
    st.subheader('Box Plot')

    st.write("""
    <style>
        div.stRadio > div {
            display: flex;
            justify-content: flex-start;
            flex-direction: row;
            padding: 0.75rem 0;
        }
        div.stRadio > div > label {
            background-color: #e1e1e1; /* 밝은 회색 배경 */
            color: #333; /* 어두운 글자색 */
            padding: 5px 20px; /* 패딩 축소 */
            border-radius: 15px; /* 더 둥근 모서리 */
            border: 2px solid #e1e1e1; /* 테두리 색상 일치 */
            margin: 0 2px; /* 여백 유지 */
            transition: all 0.3s; /* 부드러운 전환 효과 */
            cursor: pointer; /* 마우스 오버 시 커서 변경 */
        }
        div.stRadio > div > label:hover {
            background-color: #c8c8c8; /* 호버 시 배경색 */
            border-color: #c8c8c8; /* 호버 시 테두리 색상 */
        }
        div.stRadio > div > label:active {
            color: red; /* 클릭 시 글자색 */
        }
        div.stRadio > div > label > input[type="radio"] {
            display: none; /* 라디오 버튼 숨김 */
        }
        div.stRadio > div > label > input[type="radio"]:checked + div {
            color: red; /* 선택된 항목
        }
    </style>
    """, unsafe_allow_html=True)

    # 라디오 버튼으로 변환 옵션 선택
    transform = st.radio(
        "Expression transform:", 
        ['Raw', 'Z-Score'], 
        index=int(st.session_state.get('z_score', False))
    )

    # 선택된 변환 옵션에 따라 세션 상태를 설정
    st.session_state['z_score'] = transform == 'Z-Score'

    # 데이터 경로 설정
    folder_path = './data/Gene Expression/' + ('Z_Score' if st.session_state['z_score'] else 'Raw')
    
    files = os.listdir(folder_path)
    sorted_files = sorted(files, key=custom_sort_key)

    dfs = []

    for file in sorted_files:
        file_path = os.path.join(folder_path, file)
        df = load_data(file_path, name)
        if not df.empty:
            if 'Z_Score' in folder_path :
                clean_file_name = file.replace('GeneExpressionZ_', '').replace('_', ' [')[:-4] + ']'
                melted_df = df.melt(var_name='sample', value_name='value')
                melted_df['file'] = clean_file_name  
                dfs.append(melted_df)
                
            else:
                clean_file_name = file.replace('GeneExpression_', '').replace('_', ' [')[:-4] + ']'
                # melt 함수를 사용하여 long-format 데이터로 변환
                melted_df = df.melt(var_name='sample', value_name='value')
                melted_df['file'] = clean_file_name  # 파일명을 열에 추가
                # Raw인 경우 숫자열에만 2의 거듭제곱 연산을 적용
                numeric_columns = melted_df.select_dtypes(include=['number']).columns
                melted_df[numeric_columns] = 2 ** melted_df[numeric_columns]
                dfs.append(melted_df) 

    # 결합된 데이터프레임 생성
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        plot_data(combined_df)
    else:
        st.error(f"No data available for {name} in any of the files.")

'''
    Interaction Network Diagram
'''        
def plot_initial_pyvis(df, gene_name):
    net = Network(notebook=True, directed=False)
    # 이미 추가된 노드를 추적하기 위함
    seen_nodes = set()  

    unique_edges = df.drop_duplicates(subset=['Official Symbol Interactor A', 'Official Symbol Interactor B'])

    for _, row in unique_edges.iterrows():
        src, dst = row['Official Symbol Interactor A'], row['Official Symbol Interactor B']

        for node in [src, dst]:
            if node not in seen_nodes:
                if node == gene_name:
                    net.add_node(node, label=node, title=node, color='Orange', size=25)
                else:
                    net.add_node(node, label=node, title=node, color='grey', size=15)
                seen_nodes.add(node)

        net.add_edge(src, dst, color='lightgrey')

    net.show_buttons(filter_=['physics'])
    net.show("pyvis_net_graph.html")

    HtmlFile = open('pyvis_net_graph.html', 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, width=670, height=1070) 
    
# 유전자 상호작용 데이터를 로드하는 함수
def load_interaction_data(gene_name):
    # 가정: 'data/Gene-Gene Interaction/BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt' 경로에 데이터가 있음
    df = pd.read_csv('data/Gene-Gene Interaction/BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt', sep='\t')
    interactions = df[(df['Official Symbol Interactor A'] == gene_name) | (df['Official Symbol Interactor B'] == gene_name)]
    print(interactions)
    return interactions        
@st.cache_data
def load_network_data(gene_name):
    file_path = 'data\Gene-Gene Interaction\BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'
    df = pd.read_csv(file_path, sep='\t')
    interactions = df[((df['Official Symbol Interactor A'] == gene_name) | 
                    (df['Official Symbol Interactor B'] == gene_name))][['Official Symbol Interactor A', 'Official Symbol Interactor B']]

    return interactions 

# 데이터 로드 및 필터링 함수
def load_group_data(group, gene_name, threshold):
    file_path = f'data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_{group}_0.5.txt'
    if not os.path.exists(file_path):
        st.error(f"File {file_path} does not exist.")
        return pd.DataFrame()
    
    df = pd.read_csv(file_path, sep='\t')
    # 유전자 쌍 중 하나가 gene_name과 일치하고 상관계수가 threshold 이상인 행을 필터링
    filtered_df = df[((df['Gene'] == gene_name) | (df['Gene.1'] == gene_name)) & (df['Correlation coefficient'].abs() >= threshold)]
    return filtered_df

# 네트워크 생성 및 시각화 함수
def create_and_show_network(df, gene_name):
    net = Network(notebook=True, height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    for _, row in df.iterrows():
        src = row['Gene']
        dst = row['Gene.1']
        weight = row['Correlation coefficient']
        color = "red" if weight > 0 else "blue"
        
        net.add_node(src, label=src, color=color)
        net.add_node(dst, label=dst, color=color)
        net.add_edge(src, dst, title=f"Correlation: {weight}", color=color)
    
    net.show("network.html")
    return net
# 네트워크 다이어그램을 업데이트하는 함수
def update_network_diagram(df, gene_name, group, threshold):
    # 가정: 상관관계 데이터 파일 경로 패턴
    file_path = f'data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_{group}_0.5.txt'
    df_correlation = pd.read_csv(file_path, sep='\t')

    net = Network(notebook=True, directed=False)
    
    for _, row in df.iterrows():
        src = row['Official Symbol Interactor A']
        dst = row['Official Symbol Interactor B']

        src_color = dst_color = 'blue'  # 기본 색상
        edge_color = 'blue'
        size = 15

        # 상관관계 데이터에 따라 색상 업데이트
        if src == gene_name or dst == gene_name:
            size = 20  # 주요 유전자 크기 증가

        correlation_row = df_correlation[(df_correlation['Gene A'] == src) & (df_correlation['Gene B'] == dst) & (df_correlation['Correlation'].abs() >= threshold)]
        if not correlation_row.empty:
            correlation_value = correlation_row.iloc[0]['Correlation']
            if correlation_value > 0:
                src_color = dst_color = edge_color = 'red'  # 양의 상관관계
            else:
                src_color = dst_color = edge_color = 'green'  # 음의 상관관계

        net.add_node(src, label=src, title=src, color=src_color, size=size)
        net.add_node(dst, label=dst, title=dst, color=dst_color, size=size)
        net.add_edge(src, dst, color=edge_color)

    net.show("updated_network.html")
    HtmlFile = open("updated_network.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, width=800, height=600)
def show_network_diagram(gene_name):
    df_interactions = load_network_data(gene_name)
    
    # threshold 및 group 선택
    sample_class = ['Adipose_LH', 'Adipose_OH', 'Adipose_OD',
                    'Liver_LH', 'Liver_OH', 'Liver_OD',
                    'Muscle_LH', 'Muscle_OH', 'Muscle_OD']
    group = st.selectbox('Choose one group', sample_class, key='sample_input')
    threshold = st.number_input('Enter threshold:', min_value=0.0, value=0.5, step=0.01)
    
    # group 및 threshold를 선택하면 그려짐
    if st.button('Create Group Network'):
        update_network_diagram(df_interactions, gene_name, group, threshold)
    else: 
        plot_initial_pyvis(df_interactions, gene_name)

    # group = st.selectbox("Select a group:", ["Adipose_LH", "Adipose_OH", "Adipose_OD", "Liver_LH", "Liver_OH", "Liver_OD", "Muscle_LH", "Muscle_OH", "Muscle_OD"])
    # threshold = st.slider("Select a correlation threshold:", 0.0, 1.0, 0.5, 0.01)   
        # st.subheader('Network Diagram')

    # file_path = 'data\Gene-Gene Interaction\BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'
    # df_inter, name = load_network_data(file_path, gene_name)
    # plot_pyvis(df_inter, name)
    # # threshold 및 group 선택
    # sample_class = ['Adipose_LH', 'Adipose_OH', 'Adipose_OD',
    #                 'Liver_LH', 'Liver_OH', 'Liver_OD',
    #                 'Muscle_LH', 'Muscle_OH', 'Muscle_OD']
    # selected_groups = st.selectbox('Choose one group', sample_class, key='sample_input')
    # threshold = st.number_input('Enter threshold:', min_value=0.0, value=0.5, step=0.01)
    # if st.button('Create Network'):
    #     if gene_name and selected_groups:
    #         filtered_df = load_group_data(selected_groups, gene_name, threshold)
    #         if not filtered_df.empty:
    #             net = create_and_show_network(filtered_df, gene_name)
    #             # 네트워크를 HTML로 시각화
    #             HtmlFile = open("network.html", 'r', encoding='utf-8')
    #             source_code = HtmlFile.read()
    #             st.components.v1.html(source_code, height=800)
    #         else:
    #             st.error("No matching data found with the given threshold.")
    #     else:
    #         st.error("Please enter a gene name and select a group.")
    # else:        
