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
    group_colors = {group_names[0]: 'green', group_names[1]: 'orange', 'overlap': 'black'}
    
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
    </div>
    """
    components.html(legend_html, height=55)

# 1개 그룹 선택 
def create_network(df, file_name):
    net = Network(height='750px', width='100%', bgcolor='#ffffff', font_color='black')
    for index, row in df.iterrows():
        gene1 = row['Gene']
        gene2 = row['Gene.1']
        weight = row['Correlation coefficient']
        
        # 상관계수 값에 따라 엣지 색상 결정
        edge_color = 'red' if weight > 0 else 'blue'
        
        net.add_node(gene1, label=gene1, color='grey', title=gene1)
        net.add_node(gene2, label=gene2, color='grey', title=gene2)
        net.add_edge(gene1, gene2, title=str(weight), value=abs(weight), color=edge_color)
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
        color = row['color']  # 엣지 색상 지정
        
        # 노드 색상을 'lightgrey'로 고정
        net.add_node(gene1, label=gene1, title=f"{gene1}: {weight}", color='grey')
        net.add_node(gene2, label=gene2, title=f"{gene2}: {weight}", color='grey')
        # 엣지 색상 적용
        net.add_edge(gene1, gene2, title=f"{weight}", value=abs(weight), color=color)
    return net

'''
    2개 그룹 선택
'''
def show_group_legend(group_names):
    # 그룹 이름 형식 변경: "Muscle_OD" -> "Muscle [OD]"
    formatted_group_names = [name.replace("_", " [") + "]" if "_" in name else name for name in group_names]

    legend_html = f"""
    <div style="position: fixed; top: 10px; right: 10px; background-color: white; padding: 10px; border-radius: 10px; border: 1px solid #e1e4e8;">
        <div style="display: inline-block; margin-right: 20px;">
            <svg width="40" height="10"><line x1="0" y1="5" x2="40" y2="5" style="stroke:green; stroke-width:2"></line></svg>
            {formatted_group_names[0]} (green)
        </div>
        <div style="display: inline-block; margin-right: 20px;">
            <svg width="40" height="10"><line x1="0" y1="5" x2="40" y2="5" style="stroke:orange; stroke-width:2"></line></svg>
            {formatted_group_names[1]} (orange)
        </div>
        <div style="display: inline-block;">
            <svg width="40" height="10"><line x1="0" y1="5" x2="40" y2="5" style="stroke:black; stroke-width:2"></line></svg>
            Overlap (black)
        </div>
    </div>
    """
    components.html(legend_html, height=55)  
    
def show_combined_network(selected_groups, threshold):
    combined_df = load_group_data(selected_groups, threshold)
    
    if not combined_df.empty:
        net = create_group_network(combined_df)
        net_html = net.generate_html()
        components.html(net_html, height=800)
    else:
        st.error('No data to display based on the selected threshold.')
        
def color_rows(s):
    return ['color: white'] * len(s)

def format_group_name(name):
        # 그룹 이름의 마지막 2글자를 대괄호로 묶어서 반환
        if len(name) > 2:
            name = f"{name[:-2]} [{name[-2:]}]".replace("_", " ")
            return name
        else:
            return name
        
def show_df(selected_groups, threshold):
    combined_df = load_group_data(selected_groups, threshold)
    # 인덱스를 리셋하고, 기존 인덱스를 제거합니다.
    combined_df.reset_index(drop=True, inplace=True)
    # 색상별로 데이터프레임 분리
    df_black = combined_df[combined_df['color'] == 'black']
    df_green = combined_df[combined_df['color'] == 'green']
    df_orange = combined_df[combined_df['color'] == 'orange']
    print(df_black.columns)
    
    st.write(f"### Group: {format_group_name(selected_groups[0])}")
    st.dataframe(df_black.style.apply(color_rows, axis=1), width=600, hide_index=True)
    st.write(f"### Group: {format_group_name(selected_groups[1])}")
    st.dataframe(df_green.style.apply(color_rows, axis=1), width=600, hide_index=True)
    st.write(f"### Group: Both")
    st.dataframe(df_orange.style.apply(color_rows, axis=1), width=600, hide_index=True)
    
def color_rows(row):
    styles = []

    if row['color'] == 'black':
        styles.append('background-color: black; color: white')  # 흰색 텍스트
    elif row['color'] == 'orange':
        styles.append('background-color: orange; color: black')  # 검정색 텍스트
    elif row['color'] == 'green':
        styles.append('background-color: green; color: white')  # 흰색 텍스트

    return styles * len(row)
    
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
                show_legend()
                show_network(file_path, threshold)
            else:
                st.error(f"File for {group} does not exist.")
        elif len(selected_groups) == 2:
            show_group_legend(selected_groups)
            show_combined_network(selected_groups, threshold)
            show_df(selected_groups, threshold)
        else:
            st.error("Please select one or two groups.")