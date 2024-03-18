import streamlit as st
import pandas as pd
import base64
import os
from pyvis.network import Network
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
import re

@st.cache_data(show_spinner=False)
def load_data(file_path, threshold):
    df = pd.read_csv(file_path, sep='\t')
    return df[df['Correlation coefficient'].abs() >= threshold]

@st.cache_data(show_spinner=False)
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
        <div style="margin-top: 10px;">
            Use your mouse wheel to zoom in or zoom out.
        </div>
    </div>
    """
    components.html(legend_html, height=100)

# 1개 그룹 선택 
def create_network(df):
    net = Network(height='750px', width='100%', bgcolor='#ffffff', font_color='black')
    for index, row in df.iterrows():
        gene1 = row['Gene1']
        gene2 = row['Gene2']
        weight = row['Correlation coefficient']
        
        # 상관계수 값에 따라 엣지 색상 결정
        edge_color = 'red' if weight > 0 else 'blue'
        
        net.add_node(gene1, label=gene1, color='grey', title=gene1)
        net.add_node(gene2, label=gene2, color='grey', title=gene2)
        net.add_edge(gene1, gene2, title=str(weight), value=abs(weight), color=edge_color)

        st.session_state['node'] = net.get_nodes()
        st.session_state['edge'] = net.get_edges()
    return net

def show_network(filtered_df):
    if not filtered_df.empty:
        net = create_network(filtered_df)
        file_name = "network.html"
        net.save_graph(file_name)
        HtmlFile = open(file_name, 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height=800)
        HtmlFile.close()
    else:
        st.error('No data to display.')
        
# def show_network(file_path, threshold):
#     filtered_df = load_data(file_path, threshold)
#     if not filtered_df.empty:
#         net = create_network(filtered_df, file_path)
#         file_name = f"{file_path.split('/')[-1].split('.')[0]}_network.html"
#         net.save_graph(file_name)
#         HtmlFile = open(file_name, 'r', encoding='utf-8')
#         source_code = HtmlFile.read() 
#         components.html(source_code, height=800)
#         HtmlFile.close()
#     else:
#         st.error('No data to display.')
        
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

        st.session_state['node'] = net.get_nodes()
        st.session_state['edge'] = net.get_edges()
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
        <div style="margin-top: 10px;">
            Use your mouse wheel to zoom in or zoom out.
        </div>
    </div>
    """
    components.html(legend_html, height=100)  
    
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

    gene_column = {
        'Gene' : 'Gene1',
        'Gene.1' : 'Gene2',
    }
    
    st.write(f"### Group: {format_group_name(selected_groups[0])}")
    df_green = df_green.rename(columns=gene_column)
    st.dataframe(df_green.style.apply(color_rows, axis=1), width=600, hide_index=True)
    st.write(f"### Group: {format_group_name(selected_groups[1])}")
    df_orange = df_orange.rename(columns=gene_column)
    st.dataframe(df_orange.style.apply(color_rows, axis=1), width=600, hide_index=True)
    st.write(f"### Group: Both")
    df_black = df_black.rename(columns=gene_column)
    st.dataframe(df_black.style.apply(color_rows, axis=1), width=600, hide_index=True)
    
def color_rows(row):
    styles = []

    if row['color'] == 'black':
        styles.append('background-color: black; color: white')  # 흰색 텍스트
    elif row['color'] == 'orange':
        styles.append('background-color: orange; color: black')  # 검정색 텍스트
    elif row['color'] == 'green':
        styles.append('background-color: green; color: white')  # 흰색 텍스트

    return styles * len(row)    

def show_correlation(samples, threshold):
    st.subheader("Co-expression Network")  

    if len(samples) == 1:
        with st.spinner('it may takes a few minutes'):
            group = samples[0]
            file_path = os.path.join('data', 'Gene-Gene Expression Correlation', 'Correlation Higher Than 0.5', f'GeneGene_HighCorrelation_{group}_0.5.txt')
        if os.path.isfile(file_path):
            with st.spinner('it may takes a few minutes'):
                filtered_df = load_data(file_path, threshold)
                filtered_df = filtered_df.rename(columns={'Gene': 'Gene1', 'Gene.1': 'Gene2'})
                
                if not filtered_df.empty:
                    if len(filtered_df) > 6170 and len(filtered_df) < 4900000:
                        # (Edges to draw: XXXX, )
                        st.error(f'''
                                \n
                                Sorry, we can\'t draw a network with more than 6,170 edges. (Edges to draw: {format(len(filtered_df), ',')})\n
                                Please try a higher correlation threshold.\n
                                Data that needs to be drawn can be downloaded via the Download button. \n
                                ''', icon="🚨")
                        st.markdown("""<br>""" * 2, unsafe_allow_html=True)
                        download_button(filtered_df)
                    elif len(filtered_df) > 4900000:
                        st.error(f'''
                                \n
                                Sorry, we can\'t draw a network with more than 6,170 edges. (Edges to draw: {format(len(filtered_df), ',')})\n
                                Also, we can't make data file with more than 4,900,000 edges.\n
                                Please try a higher correlation threshold.\n
                                ''', icon="🚨")
                    else:
                        show_legend()
                        with st.spinner('it may takes a few minutes'):
                            show_network(filtered_df)
                            download_button(filtered_df)
                            show_edge_info()
        else:
            st.error(f"File for {group} does not exist.")
            
    elif len(samples) == 2:
        with st.spinner('it may takes a few minutes'):
            pathes = []
            for i in range(len(samples)):
                sample_path = f'./data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_{samples[i]}_0.5.txt'
                pathes.append(sample_path)
            
            df_sample0 = load_data(pathes[0], threshold)
            df_sample1 = load_data(pathes[1], threshold)

            # merged_df 생성 부분
            merged_df = pd.merge(df_sample0, df_sample1, on=['Gene', 'Gene.1'], how='outer', suffixes=(f'_{samples[0]}', f'_{samples[1]}'))
            merged_df.fillna(0, inplace=True)
            merged_df = merged_df.rename(columns={'Gene': 'Gene1', 'Gene.1': 'Gene2'})
            
            # 컬럼 이름 변경 부분
            for col in merged_df.columns:
                if "Correlation coefficient" in col:
                    new_col_name = col.replace("Correlation coefficient_", "Correlation coefficient ")
                    new_col_name = new_col_name.replace("_", " [") + "]"
                    merged_df = merged_df.rename(columns={col: new_col_name})

        if len(merged_df) > 6170 and len(merged_df) < 4900000:
            # (Edges to draw: XXXX, )
            st.error(f'''
                    \n
                    Sorry, we can\'t draw a network with more than 6,170 edges. (Edges to draw: {format(len(merged_df), ',')})\n
                    Please try a higher correlation threshold.\n
                    Data that needs to be drawn can be downloaded via the Download button. \n
                    ''', icon="🚨")
            st.markdown("""<br>""" * 2, unsafe_allow_html=True)
            download_button(merged_df)
        elif len(merged_df) > 4900000:
            st.error(f'''
                    \n
                    Sorry, we can\'t draw a network with more than 6,170 edges. (Edges to draw: {format(len(merged_df), ',')})\n
                    Also, we can't make data file with more than 4,900,000 edges.\n
                    Please try a higher correlation threshold.\n
                    ''', icon="🚨")
        else:
            show_group_legend(samples)
            with st.spinner('it may takes a few minutes'):
                show_combined_network(samples, threshold)
                download_button(merged_df)
                show_edge_info()
            show_df(samples, threshold)
    else:
        st.error("Please select one or two groups.")        


# 데이터프레임 다운로드 함수
st.cache_data(show_spinner=False)
def download_button(df):
    # 데이터 프레임의 모든 원소에 대해 조건을 검사하고 값을 변경
    df = df.applymap(lambda x: '< 0.5' if x == 0 else x)

    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # CSV를 base64로 변환
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv" style="float: right; position: relative; top: -50px;"><button style="background-color: #FF4B4B; border: none; color: white; padding: 10px 12px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 12px;">Download CSV File</button></a>'
    st.markdown(href, unsafe_allow_html=True)

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

    gene_list = ', '.join([f"'{elemenet}'" for elemenet in node])

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