import streamlit as st
import pandas as pd
import networkx as nx
import os
from pyvis.network import Network
import streamlit.components.v1 as components
from itertools import combinations

def create_header():
    st.title('Co-Expression Network Analysis')

@st.cache_data
def load_data(file_path, threshold):
    df = pd.read_csv(file_path, sep='\t')
    return df[df['Correlation coefficient'].abs() >= threshold]

@st.cache_data
def load_group_data(group_names, threshold):
    combined_df = pd.DataFrame()
    # 각 그룹별로 색상 지정
    group_colors = {group_names[0]: 'blue', group_names[1]: 'red', 'overlap': 'green'}
    
    group_data = {}
    for group in group_names:
        file_path = f'data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_{group}_0.5.txt'
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, sep='\t')
            filtered_df = df[df['Correlation coefficient'].abs() >= threshold]
            group_data[group] = filtered_df[['Gene', 'Gene.1']].apply(frozenset, axis=1).to_list()
            filtered_df['color'] = group_colors[group]
            combined_df = pd.concat([combined_df, filtered_df], ignore_index=True)
        else:
            st.error(f'파일이 존재하지 않습니다: {file_path}')
            return pd.DataFrame()

    # 겹치는 유전자 쌍을 찾아서 색상을 변경
    if len(group_names) == 2:
        overlap = set(group_data[group_names[0]]).intersection(set(group_data[group_names[1]]))
        for idx, row in combined_df.iterrows():
            if frozenset([row['Gene'], row['Gene.1']]) in overlap:
                combined_df.at[idx, 'color'] = group_colors['overlap']
    
    return combined_df

def create_network(df, file_name):
    net = Network(height='750px', width='100%', bgcolor='#ffffff', font_color='black')
    for index, row in df.iterrows():
        gene1 = row['Gene']
        gene2 = row['Gene.1']
        weight = row['Correlation coefficient']
        net.add_node(gene1, label=gene1, title=gene1)
        net.add_node(gene2, label=gene2, title=gene2)
        net.add_edge(gene1, gene2, title=str(weight), value=abs(weight))
    return net

def show_network(file_path, threshold):
    filtered_df = load_data(file_path, threshold)
    if not filtered_df.empty:
        net = create_network(filtered_df, file_path)
        file_name = f"{file_path.split('/')[-1].split('.')[0]}_network.html"
        net.save_graph(file_name)
        HtmlFile = open(file_name, 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height=800)
        HtmlFile.close()
    else:
        st.error('No data to display.')
        
def create_group_network(df, bgcolor='#ffffff', font_color='black'):
    net = Network(height='750px', width='100%', bgcolor=bgcolor, font_color=font_color)
    for index, row in df.iterrows():
        gene1 = row['Gene']
        gene2 = row['Gene.1']
        weight = row['Correlation coefficient']
        
        color = row['color']
        net.add_node(gene1, label=gene1, title=f"{gene1}: {weight}", color=color)
        net.add_node(gene2, label=gene2, title=f"{gene2}: {weight}", color=color)
        net.add_edge(gene1, gene2, title=f"{weight}", value=abs(weight), color=color)
    return net

def show_combined_network(selected_groups, threshold):
    combined_df = load_group_data(selected_groups, threshold)
    
    if not combined_df.empty:
        net = create_group_network(combined_df)
        net_html = net.generate_html()
        components.html(net_html, height=800)
    else:
        st.error('No data to display based on the selected threshold.')

def write_co_page():
    create_header()
    sample_class = ['Adipose_LH', 'Adipose_OH', 'Adipose_OD',
                    'Liver_LH', 'Liver_OH', 'Liver_OD',
                    'Muscle_LH', 'Muscle_OH', 'Muscle_OD']
    selected_groups = st.multiselect('Choose one or two groups', sample_class, key='sample_input')
    threshold = st.number_input('Enter threshold:', min_value=0.0, value=0.5, step=0.01)

    if st.button('Create Network'):
        if len(selected_groups) == 1:
            group = selected_groups[0]
            file_path = os.path.join('data', 'Gene-Gene Expression Correlation', 'Correlation Higher Than 0.5', f'GeneGene_HighCorrelation_{group}_0.5.txt')
            if os.path.isfile(file_path):
                show_network(file_path, threshold)
            else:
                st.error(f"File for {group} does not exist.")
        elif len(selected_groups) == 2:
            show_combined_network(selected_groups, threshold)
        else:
            st.error("Please select one or two groups.")