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
import one_gene_search, one_gene_network_diagram

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