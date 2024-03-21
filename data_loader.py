import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re 

def check_gene_name(gene_name):
    path = 'data/Gene Expression/Raw/GeneExpression_Adipose_LH.txt'

    df = pd.read_csv(path, sep='\t') 
    if gene_name in df['Gene name'].values:
        error_message = ""
        valid_gene = gene_name
    else:
        error_message = f"Gene name not found: {gene_name}"
        valid_gene = gene_name
        
    return valid_gene, error_message

@st.cache_data(show_spinner=False)
def check_gene_names(genes_list):
    path = 'all_genes_list.txt'
    
    with open(path, 'r') as file:
        all_genes = set(file.read().splitlines())  
    
    valid_genes = [gene for gene in genes_list if gene in all_genes]
    mismatches = [gene for gene in genes_list if gene not in all_genes]
    error_message = "Gene names not found: " + ', '.join(mismatches) if mismatches else ""
    return valid_genes, error_message

def get_threshold(threshold_key, group):
    default_threshold = 0.9
    if threshold_key not in st.session_state:
        st.session_state[threshold_key] = default_threshold
    threshold_str = st.text_input('Enter threshold of absolute correlation coefficient (minimum: 0.5)', value=str(st.session_state.get('threshold', 0.9)), key='co_threshold')
    if not re.match(r'^\d+(\.\d{1,2})?$', threshold_str):
        st.error('Please enter a valid float number in x.xx format.')
        return [group]
    else:
        try:
            threshold = float(threshold_str)

            if threshold < 0.5 and group =='no specific group':
                return [threshold, group]
            elif threshold < 0.5:
                st.error('Please try a higher correlation threshold.')
                return [group]  
            else:
                return [threshold, group]  
        except ValueError:
            if group == 'no specific group':
                return [0, group]
            st.error('Please enter a valid float number.')
            return [group] 
        
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

def group_format(sample_class):
    start_idx = sample_class.find("[")  # "["의 인덱스 찾기
    end_idx = sample_class.find("]")  # "]"의 인덱스 찾기
    if start_idx != -1 and end_idx != -1:  # "["와 "]"가 모두 존재하는 경우
        sample_class = sample_class[:start_idx-1] + '_' + sample_class[start_idx+1:end_idx]

    return sample_class

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

'''
    data
'''

@st.cache_data(show_spinner=False)
def load_Gene_Expression_Z(file_path, name):
    df = pd.read_csv(file_path, sep='\t')
    one_gene_df = df[df['Gene name'] == name].drop('Gene name', axis=1).T
    one_gene_df.columns = [name]
    return one_gene_df

# 하나의 유전자에 대한 interaction
@st.cache_data(show_spinner=False)
def load_interaction_data(gene_name):
    file_path = 'data/Gene-Gene Interaction/BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'
    cols_to_load = ['Official Symbol Interactor A', 'Official Symbol Interactor B'] 
    df = pd.read_csv(file_path, sep='\t', usecols=cols_to_load)
    interactions = df[(df['Official Symbol Interactor A'] == gene_name) | 
                      (df['Official Symbol Interactor B'] == gene_name)]
    return interactions.drop_duplicates()

@st.cache_data(show_spinner=False)
def load_gene_list_interaction_data():
    folder_path = './data/Gene-Gene Interaction/BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'
    cols_to_load = ['Official Symbol Interactor A', 'Official Symbol Interactor B']
    df_interactions = pd.read_csv(folder_path, sep='\t', usecols=cols_to_load)
    
    return df_interactions

# threshold 이상인 값을 갖는 interaction
@st.cache_data(show_spinner=False)
def load_correlation_data(group, threshold):
    file_path = f'data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_{group}_0.5.txt'

    cols_to_load = ['Gene', 'Gene.1', 'Correlation coefficient']
    dtype_spec = {'Gene': str, 'Gene.1': str, 'Correlation coefficient': float}

    df_correlation = pd.read_csv(file_path, sep='\t', usecols=cols_to_load, dtype=dtype_spec)
    df_correlation_filtered = df_correlation[df_correlation['Correlation coefficient'].abs() >= threshold]
    
    return df_correlation_filtered 

@st.cache_data(show_spinner=False)
def load_edge_data(gene1, gene2):
    file_path = './data/Gene-Gene Interaction/BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'
    cols_to_load = ['Official Symbol Interactor A', 'Official Symbol Interactor B', 'Experimental System Type', 'Author', 'Publication Source']
    df = pd.read_csv(file_path, sep='\t', usecols=cols_to_load)
    
    condition1 = ((df['Official Symbol Interactor A'] == gene1) & (df['Official Symbol Interactor B'] == gene2))
    condition2 = ((df['Official Symbol Interactor A'] == gene2) & (df['Official Symbol Interactor B'] == gene1))
    interactions = df[condition1 | condition2]
    
    base_url_pubmed = 'https://pubmed.ncbi.nlm.nih.gov/'
    base_url_doi = 'https://doi.org/'
    interactions['Publication Source Number'] = interactions['Publication Source'].apply(lambda x: base_url_pubmed + x.replace('PUBMED:', '') + '/' if 'PUBMED:' in x else base_url_doi + x)