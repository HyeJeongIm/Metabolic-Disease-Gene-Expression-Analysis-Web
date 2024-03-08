import pandas as pd
import plotly.express as px
from pyvis.network import Network
import streamlit.components.v1 as components
import streamlit as st
import os

#### node도 바뀌는 코드 
# def update_network_diagram(df, gene_name, group, threshold):
#     # 가정: 상관관계 데이터 파일 경로 패턴
#     file_path = f'data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_{group}_0.5.txt'
#     df_correlation = pd.read_csv(file_path, sep='\t')

#     net = Network(notebook=True, directed=False)

#     for _, row in df.iterrows():
#         src = row['Official Symbol Interactor A']
#         dst = row['Official Symbol Interactor B']

#         src_color = dst_color = 'blue'  # 기본 색상
#         edge_color = 'blue'
#         size = 15

#         # 상관관계 데이터에 따라 색상 업데이트
#         if src == gene_name or dst == gene_name:
#             size = 20  # 주요 유전자 크기 증가

#         correlation_row = df_correlation[(df_correlation['Gene'] == src) & (df_correlation['Gene.1'] == dst) & (df_correlation['Correlation coefficient'].abs() >= threshold)]
#         if not correlation_row.empty:
#             correlation_value = correlation_row.iloc[0]['Correlation coefficient']
#             if correlation_value > 0:
#                 src_color = dst_color = edge_color = 'red'  # 양의 상관관계
#             else:
#                 src_color = dst_color = edge_color = 'green'  # 음의 상관관계

#         net.add_node(src, label=src, title=src, color=src_color, size=size)
#         net.add_node(dst, label=dst, title=dst, color=dst_color, size=size)
#         net.add_edge(src, dst, color=edge_color)

#     net.show("updated_network.html")
#     HtmlFile = open("updated_network.html", 'r', encoding='utf-8')
#     source_code = HtmlFile.read() 
#     components.html(source_code, width=800, height=600)

'''
    Box Plot
'''

@st.cache_data(show_spinner=False)
def load_data(file_path, name):
    df = pd.read_csv(file_path, sep='\t')
    one_gene_df = df[df['Gene name'] == name].drop('Gene name', axis=1).T
    one_gene_df.columns = [name]
    return one_gene_df

@st.cache_data(show_spinner=False)
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

    # Markdown을 사용하여 굵은 텍스트로 라벨을 표시
    st.markdown("**Expression transform:**")

    # st.radio에서 라벨을 제거하고 옵션만 표시
    transform = st.radio(
        "",  # 라벨 부분을 비워둠
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
  
@st.cache_data(show_spinner=False)
def load_network_data(gene_name):
    file_path = 'data\Gene-Gene Interaction\BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'
    df = pd.read_csv(file_path, sep='\t')
    interactions = df[((df['Official Symbol Interactor A'] == gene_name) | 
                    (df['Official Symbol Interactor B'] == gene_name))][['Official Symbol Interactor A', 'Official Symbol Interactor B']]
    return interactions 

def plot_initial_pyvis(df, gene_name):
    with st.spinner('Drawing a grahp'):
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

        net.show("pyvis_net_graph.html")

        HtmlFile = open('pyvis_net_graph.html', 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        # components.html(source_code, width=670, height=1070)
        st.components.v1.html(source_code, width=670, height=610)

@st.cache_data(show_spinner=False)
def load_correlation_data(group, threshold):
    file_path = f'data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_{group}_0.5.txt'
    df_correlation = pd.read_csv(file_path, sep='\t')
    df_correlation_filtered = df_correlation[df_correlation['Correlation coefficient'].abs() >= threshold]
    return df_correlation_filtered   

def show_legend():
    legend_html = """
    <div style="position: fixed; top: 10px; right: 10px; background-color: white; padding: 10px; border-radius: 10px; border: 1px solid #e1e4e8;">
        <div style="display: inline-block; margin-right: 20px;">
            <svg width="40" height="10">
                <line x1="0" y1="5" x2="40" y2="5" style="stroke:red; stroke-width:2" />
            </svg>
            Positive correlation
        </div>
        <div style="display: inline-block;">
            <svg width="40" height="10">
                <line x1="0" y1="5" x2="40" y2="5" style="stroke:blue; stroke-width:2" />
            </svg>
            Negative correlation
        </div>
        <div style="margin-top: 10px;">
            Use your mouse wheel to zoom in or zoom out.
        </div>
    </div>
    """
    components.html(legend_html, height=100) 
    
def plot_colored_network(df_interactions, df_correlation, gene_name):
    with st.spinner('Drawing a graph'):
        net = Network(notebook=True, directed=False, cdn_resources='remote')
        seen_nodes = set()

        # 색상을 결정하는 로직 추가
        for _, interaction_row in df_interactions.iterrows():
            src, dst = interaction_row['Official Symbol Interactor A'], interaction_row['Official Symbol Interactor B']
            color = 'lightgrey'  # 기본 색상
            weight = None

            correlation_row = df_correlation[((df_correlation['Gene'] == src) & (df_correlation['Gene.1'] == dst)) | 
                                                ((df_correlation['Gene'] == dst) & (df_correlation['Gene.1'] == src))]

            if not correlation_row.empty:
                correlation = correlation_row.iloc[0]['Correlation coefficient']
                color = 'red' if correlation > 0 else 'blue'
                if color in ['red', 'blue']:
                    weight = correlation
            # create_network(correlation_row)
            # 노드 추가
            for node in [src, dst]:
                if node not in seen_nodes:
                    node_color = 'orange' if node == gene_name else 'grey'
                    net.add_node(node, label=node, title=node, color=node_color, size=15)
                    seen_nodes.add(node)

            # 상관관계에 따라 색상이 지정된 엣지 추가
            if weight is not None:
                net.add_edge(src, dst, color=color, value=abs(weight), title=f"{weight}")
            else:
                net.add_edge(src, dst, color=color)

        net.show("pyvis_net_graph.html")

        HtmlFile = open('pyvis_net_graph.html', 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        # components.html(source_code, width=670, height=1070)
        st.components.v1.html(source_code, width=670, height=610)


def show_network_diagram(gene_name):
    
    df_interactions = load_network_data(gene_name)
    
    st.subheader(f"**[ Protein interaction around '{gene_name}'** ]")

    # threshold 및 group 선택
    sample_class = ['Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                    'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                    'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']
    group = st.selectbox('Choose one group', sample_class, key='sample_input')
    threshold = st.number_input('Enter threshold of absolute correlation coefficient:', min_value=0.0, value=0.5, step=0.01)
    # 데이터를 찾기 위해서 그룹명 포매팅
    formatted_group = group_format(group)

    # group 및 threshold를 선택하면 그려짐
    if st.button('Create Group Network'):
        df_correlation = load_correlation_data(formatted_group, threshold)
        show_legend()
        plot_colored_network(df_interactions, df_correlation, gene_name)
    else: 
        plot_initial_pyvis(df_interactions, gene_name)

def group_format(sample_class):
    start_idx = sample_class.find("[")  # "["의 인덱스 찾기
    end_idx = sample_class.find("]")  # "]"의 인덱스 찾기
    if start_idx != -1 and end_idx != -1:  # "["와 "]"가 모두 존재하는 경우
        sample_class = sample_class[:start_idx-1] + '_' + sample_class[start_idx+1:end_idx]

    return sample_class

'''
    v3 (혹시 몰라서 남겨둠)
'''

# @st.cache_data(show_spinner=False)
# def load_network_data(gene_name):
#     file_path = 'data\Gene-Gene Interaction\BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'
#     df = pd.read_csv(file_path, sep='\t')
#     interactions = df[((df['Official Symbol Interactor A'] == gene_name) | 
#                     (df['Official Symbol Interactor B'] == gene_name))][['Official Symbol Interactor A', 'Official Symbol Interactor B']]
#     return interactions 

# @st.cache_data(show_spinner=False)
# def load_correlation_data(group, threshold):
#     file_path = f'data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_{group}_0.5.txt'
#     df_correlation = pd.read_csv(file_path, sep='\t')
#     df_correlation_filtered = df_correlation[df_correlation['Correlation coefficient'].abs() >= threshold]
#     return df_correlation_filtered  

# def plot_network(df, gene_name, network_type='initial', df_correlation=None):
#     # 네트워크 그리기 로직
#     net = Network(notebook=True, directed=False)
#     seen_nodes = set()

#     for _, row in df.iterrows():
#         src, dst = row['Official Symbol Interactor A'], row['Official Symbol Interactor B']
#         color = 'lightgrey'  # 기본 색상
#         weight = None
        
#         for node in [src, dst]:
#             if node not in seen_nodes:
#                 net.add_node(node, label=node, title=node, color='Orange' if node == gene_name else 'grey', size=25 if node == gene_name else 15)
#                 seen_nodes.add(node)

#         edge_color = 'lightgrey'
#         if network_type == 'correlation' and df_correlation is not None:
#             correlation_row = df_correlation[((df_correlation['Gene'] == src) & (df_correlation['Gene.1'] == dst)) | 
#                                              ((df_correlation['Gene'] == dst) & (df_correlation['Gene.1'] == src))]
#             if not correlation_row.empty:
#                 correlation = correlation_row.iloc[0]['Correlation coefficient']
#                 color = 'red' if correlation > 0 else 'blue'
#                 if color in ['red', 'blue']:
#                     weight = correlation
#             # create_network(correlation_row)
#             # 노드 추가
#             for node in [src, dst]:
#                 if node not in seen_nodes:
#                     node_color = 'orange' if node == gene_name else 'grey'
#                     net.add_node(node, label=node, title=node, color=node_color, size=15)
#                     seen_nodes.add(node)

#             # 상관관계에 따라 색상이 지정된 엣지 추가
#             if weight is not None:
#                 net.add_edge(src, dst, color=color, value=abs(weight), title=f"{weight}")
#             else:
#                 net.add_edge(src, dst, color=color)
#         else:
#             net.add_edge(src, dst, color=edge_color)

#     file_name = "correlation_network.html" if network_type == 'correlation' else "initial_network.html"
#     net.show(file_name)
#     HtmlFile = open(file_name, 'r', encoding='utf-8')
#     source_code = HtmlFile.read() 
#     st.components.v1.html(source_code, width=800, height=630)
    
# def show_correlation_network_options(df, gene_name):
#     sample_class = ['Adipose_LH', 'Adipose_OH', 'Adipose_OD', 'Liver_LH', 'Liver_OH', 'Liver_OD', 'Muscle_LH', 'Muscle_OH', 'Muscle_OD']
#     group = st.selectbox('Choose sample group', sample_class, key='group')
#     threshold = st.number_input('Enter threshold of absolute correlation coefficient', min_value=0.0, value=0.5, step=0.01, key='threshold')
#     if st.button('Show Correlation Network'):
#         df_correlation = load_correlation_data(group, threshold)
#         plot_network(df, gene_name, 'correlation', df_correlation)        
        
# def show_network_diagram(gene_name):
#     df_interactions = load_network_data(gene_name)  # Assuming this function is defined elsewhere
#     if 'create_clicked' not in st.session_state:
#         plot_network(df_interactions, gene_name)
#         if st.button('Create Correlation Network'):
#             st.session_state['create_clicked'] = True
#     if 'create_clicked' in st.session_state:
#         show_correlation_network_options(df_interactions, gene_name)