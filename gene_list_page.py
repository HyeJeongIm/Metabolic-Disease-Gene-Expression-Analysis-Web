import streamlit as st
import re 
import gene_list
import pandas as pd

def create_header():
    st.title('Multiple Gene Expression')
    
@st.cache_data(show_spinner=False)
def check_gene_names(genes_list):
    path = 'data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_Adipose_LH_0.5.txt'
    df = pd.read_csv(path, delimiter='\t', usecols=['Gene', 'Gene.1'])
    all_genes = pd.concat([df['Gene'], df['Gene.1']]).unique()

    genes_series = pd.Series(genes_list).unique()
    valid_genes = pd.Series(list(set(genes_series) & set(all_genes)))
    mismatches = list(set(genes_series) - set(all_genes))

    error_message = f"Gene names not found: {', '.join(mismatches)}" if mismatches else ""

    return valid_genes.tolist(), error_message


def create_search_bar():
    base_path = 'data/Gene Expression/Z_Score'
    if 'pressed' not in st.session_state:
        st.session_state['pressed'] = False
    if 'gene_list' not in st.session_state:
        st.session_state['gene_list'] = []

    threshold_key = 'threshold_gene_list_search'  # gene list 페이지 전용 키
    default_threshold = 0.9

    if not st.session_state['pressed']:
        genes_input = st.text_area('Enter gene names:')
        genes_list = re.split('[ ,\t\n]+', genes_input.strip())
        if genes_input.strip() == '':
            genes_list = []
        st.write(f"Number of genes entered: {len(genes_list)}")
        if st.button('Search', key='search_multiple_genes'):
            st.session_state['pressed'] = True
            st.session_state['gene_list'] = genes_list
            st.rerun()
    else:
        valid_genes, error_message = check_gene_names(st.session_state['gene_list'])


        if error_message:
            st.error(error_message)
        st.session_state['gene_list'] = valid_genes
        gene_list.show_heatmap(st.session_state['gene_list'], base_path)
        st.subheader(f"**Protein interactions between input Genes**")

        sample_class = ['no specific group', 'Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                        'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                        'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']
        group = st.selectbox('Choose a sample group for annotation', sample_class, key='group', index=0)

        if group != 'no specific group':
            valid_threshold = get_threshold(threshold_key, group)  
            
            _, col2 = st.columns([8, 1])
            with col2:
                apply_clicked = st.button('Apply')

            if len(valid_threshold) == 2:
                if valid_threshold is not None:
                    gene_list.show_network_diagram(st.session_state['gene_list'], group, valid_threshold[0])
        else:
            gene_list.show_network_diagram(st.session_state['gene_list'], group)
            
        gene_list.show_edge_info()
        
        if st.button('Back'):
            st.session_state['pressed'] = False
            st.session_state['gene_list'] = []  
            st.experimental_rerun()

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
        
def write_gene_list_page():    
    create_header()
    create_search_bar()

def str_to_float(default=0.9):
    threshold_str = st.text_input('Enter threshold value', value=str(default))
    try:
        return float(threshold_str)
    except ValueError:
        st.error("Please enter a valid float number for the threshold.")
        return default 