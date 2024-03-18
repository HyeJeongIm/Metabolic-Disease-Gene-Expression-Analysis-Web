import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pyvis.network import Network
import streamlit.components.v1 as components
from itertools import combinations 
from one_gene_search import custom_sort_key
from one_gene_search import group_format
import requests
from bs4 import BeautifulSoup
import re

'''
    heatmap
'''
@st.cache_data(show_spinner=False)
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

def show_heatmap(genes_list, base_path):
    st.subheader('Heatmap')

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
        max_genes_display = 40
        if len(genes_list) > max_genes_display:
            heatmap_height = max_genes_display * gene_height
            show_gene_labels = False
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
                        zmin=-3,
                        zmax=3,
                        colorbar=dict(
                            title="z-score",
                            title_side="right",
                            tickvals=[-3, 0, 3],
                            ticktext=['-3', '0', '3']
                        ) if i == len(sorted_files) else None,  # Only add colorbar to last trace
                    ),
                    row=row, col=col
                )

                if col == 1 and show_gene_labels:
                    fig.update_yaxes(row=row, col=col)
                else:
                    fig.update_yaxes(showticklabels=False, row=row, col=col, visible=False)
                    fig.update_xaxes(visible=False)
            except FileNotFoundError:
                st.error(f'File not found: {file}')
            except KeyError:
                st.error(f'One or more genes not found in file: {file}')

        extra_space_per_row = 50
        total_height = heatmap_height * rows + extra_space_per_row * (rows - 1)

        fig.update_layout(
            width=900,
            height=max(total_height, 600),
            title_text='Expression heatmaps',
            showlegend=False,
        )

        fig.update_xaxes(showticklabels=False)
        st.plotly_chart(fig)
    else:
        st.error('Please enter at least one gene name.')

'''
    network
'''
@st.cache_data(show_spinner=False)
def load_network_data():
    folder_path = './data/Gene-Gene Interaction/BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'
    cols_to_load = ['Official Symbol Interactor A', 'Official Symbol Interactor B']
    df_interactions = pd.read_csv(folder_path, sep='\t', usecols=cols_to_load)
    
    return df_interactions

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

def plot_initial_pyvis(genes_list):
    df_interactions = load_network_data()
    net = Network(notebook=True, directed=False)

    interactions_set = set(map(frozenset, df_interactions.to_numpy()))

    added_nodes = set()

    for gene_pair in combinations(genes_list, 2):
        if frozenset(gene_pair) in interactions_set:
            # 중복된 노드 추가 방지
            for gene in gene_pair:
                if gene not in added_nodes:
                    net.add_node(gene, label=gene, title=gene, size=15, color='grey')
                    added_nodes.add(gene)
            # 엣지 추가
            net.add_edge(gene_pair[0], gene_pair[1], color='lightgrey')

    net.show("pyvis_net_graph.html")
    HtmlFile = open("pyvis_net_graph.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    st.components.v1.html(source_code, width=670, height=610)

    st.session_state['node'] = net.get_nodes()
    st.session_state['edge'] = net.get_edges()
        
def plot_colored_network(df_interactions, df_correlation_filtered, genes_list):
    net = Network(notebook=True, directed=False)
    
    for gene_pair in combinations(genes_list, 2):
            interactions = df_interactions[((df_interactions['Official Symbol Interactor A'] == gene_pair[0]) & (df_interactions['Official Symbol Interactor B'] == gene_pair[1])) |
                            ((df_interactions['Official Symbol Interactor A'] == gene_pair[1]) & (df_interactions['Official Symbol Interactor B'] == gene_pair[0]))]
            if not interactions.empty:
                net.add_node(gene_pair[0], label=gene_pair[0], title=gene_pair[0], size=15, color='grey')
                net.add_node(gene_pair[1], label=gene_pair[1], title=gene_pair[1], size=15, color='grey')

                correlation = df_correlation_filtered[(df_correlation_filtered['Gene'] == gene_pair[0]) & (df_correlation_filtered['Gene.1'] == gene_pair[1]) | (df_correlation_filtered['Gene'] == gene_pair[1]) & (df_correlation_filtered['Gene.1'] == gene_pair[0])]
                if not correlation.empty:
                    color = 'red' if correlation['Correlation coefficient'].values[0] > 0 else 'blue'
                    weight = abs(correlation['Correlation coefficient'].values[0])
                    net.add_edge(gene_pair[0], gene_pair[1], color=color, value=weight, title=f"{weight}")
                else:
                    color = 'lightgrey'  
                    net.add_edge(gene_pair[0], gene_pair[1], color=color)

    net.show("plot_colored_network.html")
    HtmlFile = open('plot_colored_network.html', 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    st.components.v1.html(source_code, width=670, height=610)

    if 'node' not in st.session_state:
        st.session_state['node'] = net.get_nodes()
    if 'edge' not in st.session_state:
        st.session_state['edge'] = net.get_edges()    
    
def show_network_diagram(genes_list, group, threshold=0.9):  
    if group == 'no specific group':
        with st.spinner('It may takes a few minutes'):
            plot_initial_pyvis(genes_list)
    else:
        with st.spinner('It may takes a few minutes'):
            formatted_group = group_format(group)
            try:
                df_correlation = load_correlation_data(formatted_group, threshold)
                show_legend()
                df_interactions = load_network_data()
                plot_colored_network(df_interactions, df_correlation, genes_list)
            except FileNotFoundError:
                st.error(f"No data file found for the group '{group}' with the selected threshold. Please adjust the threshold or choose a different group.")

def group_format(sample_class):
    start_idx = sample_class.find("[")  # "["의 인덱스 찾기
    end_idx = sample_class.find("]")  # "]"의 인덱스 찾기
    if start_idx != -1 and end_idx != -1:  # "["와 "]"가 모두 존재하는 경우
        sample_class = sample_class[:start_idx-1] + '_' + sample_class[start_idx+1:end_idx]

    return sample_class

@st.cache_data(show_spinner=False)
def load_edge_data(gene_name, gene_list):
    file_path = './data/Gene-Gene Interaction/BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'
    cols_to_load = ['Official Symbol Interactor A', 'Official Symbol Interactor B', 'Experimental System Type', 'Author', 'Publication Source']
    df = pd.read_csv(file_path, sep='\t', usecols=cols_to_load)
    
    interactions = df[((df['Official Symbol Interactor A'] == gene_name) & df['Official Symbol Interactor B'].isin(gene_list)) |
                      ((df['Official Symbol Interactor B'] == gene_name) & df['Official Symbol Interactor A'].isin(gene_list))]
    interactions = interactions.drop_duplicates()
    
    base_url = 'https://pubmed.ncbi.nlm.nih.gov/'
    interactions['Publication Source Number'] = base_url + interactions['Publication Source'].str.replace('PUBMED:', '') + '/'
    
    interactions = interactions[['Official Symbol Interactor A', 'Official Symbol Interactor B', 'Experimental System Type', 'Author', 'Publication Source', 'Publication Source Number']]

    return interactions

def show_edge_info():
    node = st.session_state.get('node', [])
    if not node:
        st.warning("No gene data available.")
        return

    gene_list = ', '.join([f"'{gene}'" for gene in node])

    st.subheader(f"**Identification of genes associated with {gene_list}**")

    node_options = ['Choose the gene which you want to see information.'] + sorted(node)
    gene_list_1 = st.selectbox("First gene", node_options, index=0)
    
    if gene_list_1 == 'Choose the gene which you want to see information.':
            return    
        
    edge = st.session_state.get('edge', [])
    opposite_genes = {interaction['to'] for interaction in edge if interaction['from'] == gene_list_1}
    opposite_genes.update({interaction['from'] for interaction in edge if interaction['to'] == gene_list_1})

    if not opposite_genes:
        st.info("No interactions found for the selected gene.")
        return
    
    st.success(f'You can choose from these genes: {", ".join(sorted(opposite_genes))}')
        
    gene_list_2 = st.text_input('Second gene ( Type the gene name which you want to see information. )')
    if gene_list_2.strip():  # 입력값이 있는지 확인
        gene_list_2 = re.split('[ ,\t\n]+', gene_list_2.strip())
        gene_list_2 = [s.replace("'", "").replace('"', '') for s in gene_list_2]
        gene_list_2_set = set(gene_list_2)
        invalid_genes = gene_list_2_set - opposite_genes  # set 연산을 사용하여 불일치하는 유전자 식별
        
        if invalid_genes:
            for gene_name in invalid_genes:
                st.error(f'Gene name "{gene_name}" is not valid. Please type valid gene names.')
                break

    _, col2 = st.columns([8, 1])
    with col2:
        apply_clicked = st.button('Show')
        
    if apply_clicked and gene_list_2:
        interactions_1 = load_edge_data(gene_list_1, list(opposite_genes))
        interactions_final = interactions_1[interactions_1['Official Symbol Interactor B'].isin(gene_list_2) | interactions_1['Official Symbol Interactor A'].isin(gene_list_2)]
        interactions_final['Link Title'] = interactions_final['Publication Source Number'].apply(get_link_title)

        if not interactions_final.empty:
            st.write(f"Interaction edge information: {gene_list_1} & {', '.join(gene_list_2)} ")
            st.dataframe(
                interactions_final,
                hide_index=True,
                column_config={
                    'Publication Source Number' : st.column_config.LinkColumn(display_text='🔗')
                }
            )
        else:
            st.write(interactions_final)
                
def get_link_title(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string
            title = title.replace('- PubMed', '')
            return title
    except Exception as e:
        print(f'Error fetching title for link {url}: {str(e)}')
    return None