# library
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# streamlit
import streamlit as st
from streamlit_option_menu import option_menu

# file load
import os

# network diagram
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

def load_data(file_path, name):
    
    df = pd.read_csv(file_path, sep='\t')
    
    one_gene_df = df[df['Gene name'] == name].drop('Gene name', axis=1).T
    one_gene_df.columns = [name]

    return one_gene_df

def plot_data(df, file, name):

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df)
    plt.ylabel("Expression Level")
    
    st.pyplot(plt)
    
def create_box_plot_page(name):
    folder_path = './data/Gene Expression'
    
    files = os.listdir(folder_path)
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        df = load_data(file_path, name)
        st.subheader("Box Plot of " + file[:-4] + "_" + name)

        plot_data(df, file[:-4], name)

def load_network_data(file_path, name):
    
    df = pd.read_csv(file_path, sep='\t')
    
    filtered_df_A = df[df['Official Symbol Interactor A'] == name]
    interactor_b_values = filtered_df_A['Official Symbol Interactor B'].tolist()
    
    filtered_df_B = df[df['Official Symbol Interactor B'] == name]
    interactor_a_values = filtered_df_B['Official Symbol Interactor A'].tolist()
    
    interactor_list = list(set(interactor_a_values + interactor_b_values))
    
    return interactor_list

def create_network_page(gene_name):
    file_path = 'data\Gene-Gene Interaction\BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'
    
    # 상호작용 유전자 리스트
    interactor_list = load_network_data(file_path, gene_name)
    
    # NetworkX 그래프 생성
    G = nx.Graph()

    # 중심 유전자를 그래프에 추가
    G.add_node(gene_name, size=15, color='red')

    for interactor in interactor_list:
        G.add_node(interactor, size=15, color='blue')
        G.add_edge(gene_name, interactor)

    # PyVis 네트워크 생성
    nt = Network('700px', '300px', notebook=True)  # 스트림릿에서는 notebook 모드를 True로 설정
    nt.from_nx(G)
    nt.show('gene_network.html')

    # Streamlit 앱에 네트워크 표시
    HtmlFile = open('gene_network.html', 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, width=10000, height=5000)
 
def network_page():
    if 'stage' not in st.session_state:
        st.session_state.stage = 0

    def set_state(i):
        st.session_state.stage = i

    if st.session_state.stage == 0:
        st.button('유전자 1개 검색', on_click=set_state, args=[1])
        
    if st.session_state.stage >= 1:
        st.markdown("## 🧬 유전자를 입력해주세요")
        st.markdown(
        """
        <style>
        .stTextInput > div > div > input {
            border: 4px solid #ff4b4b; /* 빨간색 테두리 적용 */
        }
        </style>
        """,
        unsafe_allow_html=True,
        )
        
        name = st.text_input('', on_change=set_state, args=[2], key="gene_input")

        col1, col2 = st.columns([1, 4])
        with col1:
            st.button('Back', on_click=set_state, args=[0])
            st.button('Next', on_click=set_state, args=[2])   
            
    if st.session_state.stage == 2:
        
        create_network_page(name)
        st.button('Back', on_click=set_state, args=[1])    

def write_main_page():
    
    if 'stage' not in st.session_state:
        st.session_state.stage = 0

    def set_state(i):
        st.session_state.stage = i

    if st.session_state.stage == 0:
        st.button('유전자 1개 검색', on_click=set_state, args=[1])
        
    if st.session_state.stage >= 1:
        st.markdown("## 🧬 유전자를 입력해주세요")
        st.markdown(
        """
        <style>
        .stTextInput > div > div > input {
            border: 4px solid #ff4b4b; /* 빨간색 테두리 적용 */
        }
        </style>
        """,
        unsafe_allow_html=True,
        )
        
        name = st.text_input('', on_change=set_state, args=[2], key="gene_input")

        col1, col2 = st.columns([1, 4])
        with col1:
            st.button('Back', on_click=set_state, args=[0])
            st.button('Next', on_click=set_state, args=[2])    

    if st.session_state.stage == 2:
        
        create_box_plot_page(name)
        st.button('Back', on_click=set_state, args=[1])


def create_layout():
    with st.sidebar:
        page = option_menu("Menu", ["Main", "User Inputs", "Data Display", 'Analysis'],
                            icons=['house', 'person', 'bi bi-robot', 'bi bi-robot'],
                            menu_icon="app-indicator", default_index=0,
                            styles={
            "container": {"padding": "4!important", "background-color": "#fafafa"},
            "icon": {"color": "black", "font-size": "25px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"10px", "--hover-color": "#fafafa"},
            "nav-link-selected": {"background-color": "#08c7b4"},
        }
        )
        
    if page == 'Main':
        write_main_page()
        pass
    if page == 'Network Diagram':
        pass
    elif page == 'Data Display':
        network_page()
    elif page == 'Analysis':
        pass

def main():
    create_layout()    

if __name__ == "__main__":
    main()

