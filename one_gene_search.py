import pandas as pd
import plotly.express as px
from pyvis.network import Network
import streamlit.components.v1 as components
import streamlit as st
import os

def load_data(file_path, name):
    df = pd.read_csv(file_path, sep='\t')
    one_gene_df = df[df['Gene name'] == name].drop('Gene name', axis=1).T
    one_gene_df.columns = [name]
    return one_gene_df

def load_network_data(file_path, name):
    data = pd.read_csv(file_path, sep='\t')
    df = pd.DataFrame(data)

    df_interaction = df[['Official Symbol Interactor A', 'Official Symbol Interactor B']]

    result = df_interaction[(df_interaction['Official Symbol Interactor A'] == name) | (df_interaction['Official Symbol Interactor B'] == name)]

    return result, name

def plot_data(combined_df):
    fig = px.box(combined_df, x='file', y='value', color='file', 
                 labels={'value': 'Expression Level', 'file': 'Sample'})
    fig.update_layout(showlegend=False)  
    st.plotly_chart(fig, use_container_width=True)
    
def plot_pyvis(df, gene_name):
    net = Network(
        notebook=True,
        directed=False,
        )
    
    # 중복 제거
    unique_edges = df[['Official Symbol Interactor A', 'Official Symbol Interactor B']].drop_duplicates()
    
    for _, row in unique_edges.iterrows():
        src = row['Official Symbol Interactor A']
        dst = row['Official Symbol Interactor B']

        # 찾는 유전자 빨간색으로 표현하기
        if src == gene_name:
            net.add_node(src, label=src, title=src, color='red')
        else:
            net.add_node(src, label=src, title=src)
        if dst == gene_name:
            net.add_node(dst, label=dst, title=dst, color='red')
        else:
            net.add_node(dst, label=dst, title=dst)

        net.add_edge(src, dst, color='black')

    net.show_buttons(filter_=['physics'])
    net.show("pyvis_net_graph.html")

    # html 파일 페이지에 나타내기
    HtmlFile = open('pyvis_net_graph.html', 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, width=670, height=1070)

def show_box_plot(name, z_score=False):
    st.subheader('Box Plot')
    
    if st.button('Raw'):
        st.session_state['z_score'] = False
    if st.button('Z-Score'):
        st.session_state['z_score'] = True
        
    if z_score or st.session_state.get('z_score'):
        folder_path = './data/Gene Expression/Z_Score'
    else:
        folder_path = './data/Gene Expression/Raw'
    files = os.listdir(folder_path)

    dfs = []

    for file in files:
        file_path = os.path.join(folder_path, file)
        df = load_data(file_path, name)
        if not df.empty:
            if 'Z_Score' in folder_path :
                clean_file_name = file.replace('GeneExpressionZ_', '')[:-4]  
                melted_df = df.melt(var_name='sample', value_name='value')
                melted_df['file'] = clean_file_name  
                dfs.append(melted_df)
                
            else:
                clean_file_name = file.replace('GeneExpression_', '')[:-4]  # 확장자 제외
                # melt 함수를 사용하여 long-format 데이터로 변환
                melted_df = df.melt(var_name='sample', value_name='value')
                melted_df['file'] = clean_file_name  # 파일명을 열에 추가
                dfs.append(melted_df) 

    # 결합된 데이터프레임 생성
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        plot_data(combined_df)
    else:
        st.error(f"No data available for {name} in any of the files.")
      
def show_network_diagram(gene_name):
    st.subheader('Network Diagram')

    file_path = 'data\Gene-Gene Interaction\BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'

    df_inter, name = load_network_data(file_path, gene_name)
 
    plot_pyvis(df_inter, name)