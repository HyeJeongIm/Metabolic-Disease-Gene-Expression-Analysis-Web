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

    return result

def plot_data(combined_df):
    fig = px.box(combined_df, x='file', y='value', color='file', 
                 labels={'value': 'Expression Level', 'file': 'Sample'})
    fig.update_layout(showlegend=False)  
    st.plotly_chart(fig, use_container_width=True)
    
def plot_pyvis(df):
    net = Network(
        notebook=True,
        directed=False,
        )
    
    sources = df['Official Symbol Interactor A']
    targets = df['Official Symbol Interactor B']

    edge_data = zip(sources, targets)

    for e in edge_data:
        src = e[0]
        dst = e[1]

        net.add_node(src, src, title=src)
        net.add_node(dst, dst, title=dst)
        net.add_edge(src, dst)

    net.show_buttons(filter_=['physics'])
    net.show("pyvis_net_graph.html")

    HtmlFile = open('pyvis_net_graph.html', 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, width=670, height=1050)

def show_box_plot(name):
    st.subheader('Box Plot')

    folder_path = './data/Gene Expression'
    files = os.listdir(folder_path)
    
    dfs = []
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        df = load_data(file_path, name)
        if not df.empty:
            # 'GeneExpression_' 접두사를 제거하고 'file' 열 추가
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

    df_inter = load_network_data(file_path, gene_name)
 
    plot_pyvis(df_inter)