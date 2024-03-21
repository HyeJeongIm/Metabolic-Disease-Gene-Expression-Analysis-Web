import pandas as pd
import plotly.express as px
from pyvis.network import Network
import streamlit.components.v1 as components
import streamlit as st
import os
import data_loader

'''
    Box Plot
'''
def plot_data(combined_df):
    fig = px.box(combined_df, x='file', y='value', color='file', 
                 labels={'value': 'Expression Level', 'file': 'Tissue [Disease status]'})
    fig.update_layout(showlegend=False)  
    st.plotly_chart(fig, use_container_width=True)
    
def show_box_plot(name, z_score):
    st.subheader('Box Plot')
    
    transform = st.selectbox(
        "Expression levels in",
        ['RMA-Normalized', 'Z-Score'],
        index=0 if not z_score else 1,  
        key="data_transformation_selectbox"
    )

    # 데이터 경로 설정
    folder_path = './data/Gene Expression/' + ('Z_Score' if transform == 'Z-Score' else 'Raw')
    
    files = os.listdir(folder_path)
    sorted_files = sorted(files, key=data_loader.custom_sort_key)

    dfs = []

    for file in sorted_files:
        file_path = os.path.join(folder_path, file)
        df = data_loader.load_Gene_Expression_Z(file_path, name)
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

def plot_initial_pyvis(df, gene_name):
    net = Network(notebook=True, directed=False)
    seen_nodes = set()  

    for _, row in df.iterrows():
        src, dst = row['Official Symbol Interactor A'], row['Official Symbol Interactor B']

        for node in [src, dst]:
            if node not in seen_nodes:
                net.add_node(node, label=node, title=node, color='orange' if node == gene_name else 'grey', size=25 if node == gene_name else 15)
                seen_nodes.add(node)

        net.add_edge(src, dst, color='lightgrey')

    net.show("pyvis_net_graph.html")
    HtmlFile = open("pyvis_net_graph.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, width=670, height=610)

    st.session_state['node'] = net.get_nodes()
    st.session_state['edge'] = net.get_edges()

def plot_colored_network(df_interactions, df_correlation, gene_name):
    # with st.spinner('It may takes few minutes'):
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

        net.show("one_gene_search_graph.html")

        HtmlFile = open('one_gene_search_graph.html', 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        st.components.v1.html(source_code, width=670, height=610)

def show_network_diagram(gene_name, group, threshold=0.9):
    with st.spinner('It may takes a few minutes'):
            df_interactions = data_loader.load_interaction_data(gene_name)

            if len(df_interactions) > 6170 and len(df_interactions) < 4900000:
                # (Edges to draw: XXXX, )
                st.error(f'''
                        \n
                        Sorry, we can\'t draw a network with more than 6,170 edges. (Edges to draw: {format(len(df_interactions), ',')})\n
                        Please try a higher correlation threshold.\n
                        Data that needs to be drawn can be downloaded via the Download button. \n
                        ''', icon="🚨")
                st.markdown("""<br>""" * 2, unsafe_allow_html=True)
            elif len(df_interactions) > 4900000:
                st.error(f'''
                        \n
                        Sorry, we can\'t draw a network with more than 6,170 edges. (Edges to draw: {format(len(df_interactions), ',')})\n
                        Also, we can't make data file with more than 4,900,000 edges.\n
                        Please try a higher correlation threshold.\n
                        ''', icon="🚨")
            else:
                if group == 'no specific group':
                    with st.spinner('It may takes a few minutes'):
                        plot_initial_pyvis(df_interactions, gene_name)
                else:
                    with st.spinner('It may takes a few minutes'):
                        formatted_group = data_loader.group_format(group)
                        try:
                            df_correlation = data_loader.load_correlation_data(formatted_group, threshold[0])
                            show_legend()
                            plot_colored_network(df_interactions, df_correlation, gene_name)
                        except FileNotFoundError:
                            st.error(f"No data file found for the group '{group}' with the selected threshold. Please adjust the threshold or choose a different group.")

'''
    edge info
'''
def show_edge_info():
    node = st.session_state.get('node', [])
    if not node:
        st.warning("No gene data available.")
        return

    gene_list = ', '.join([f"'{gene}'" for gene in node])

    st.subheader(f"**Identification of genes associated with {gene_list}**")
    
    edges = []
    edge = st.session_state.get('edge', [])
    for item in edge:
        if item['to'] == st.session_state['gene_name']:
            edges.append(f"{item['to']} - {item['from']}")
        else:
            edges.append(f"{item['from']} - {item['to']}")

    edge_options = ['Choose the interaction which you want to see information.'] + sorted(edges)
    gene_list_1 = st.selectbox("", edge_options, index=0)

    if gene_list_1 == 'Choose the interaction which you want to see information.':
        return  
    elif gene_list_1 != 'Choose the interaction which you want to see information.':  
        parts = gene_list_1.split(' - ')
        first = parts[0]
        to = parts[1]

        interactions_1 = data_loader.load_edge_data(first, to)
        interactions_final = interactions_1[(interactions_1['Official Symbol Interactor B'] == to) | (interactions_1['Official Symbol Interactor A'] == to)]
        interactions_final['Link Title'] = interactions_final['Publication Source Number'].apply(data_loader.get_link_title)

        if not interactions_final.empty:
            st.write(f"Interaction edge information: {gene_list_1}")
            st.dataframe(
                interactions_final,
                hide_index=True,
                column_config={
                    'Publication Source Number' : st.column_config.LinkColumn(display_text='🔗')
                }
            )
        else:
            st.write(interactions_final)