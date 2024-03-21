import streamlit as st
import gene_list
import data_loader
import re

def create_header():
    st.title('Multiple Gene Expression')

def draw_initial_gene_list_page():
    genes_input = st.text_area('Enter gene names:')
    genes_list = re.split('[ ,\t\n]+', genes_input.strip())
    if genes_input.strip() == '':
        genes_list = []
    st.write(f"Number of genes entered: {len(genes_list)}")
    if st.button('Search', key='search_multiple_genes'):
        st.session_state['pressed'] = True
        st.session_state['gene_list'] = genes_list
        st.rerun()
    
def create_search_bar():
    base_path = 'data/Gene Expression/Z_Score'
    if 'pressed' not in st.session_state:
        st.session_state['pressed'] = False
    if 'gene_list' not in st.session_state:
        st.session_state['gene_list'] = []

    threshold_key = 'threshold_gene_list_search'  # gene list 페이지 전용 키

    if not st.session_state['pressed']:
        draw_initial_gene_list_page()
    else:
        valid_genes, error_message = data_loader.check_gene_names(st.session_state['gene_list'])

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
            valid_threshold = data_loader.get_threshold(threshold_key, group)  
            
            _, col2 = st.columns([8, 1])
            with col2:
                st.button('Apply')

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
        
def write_gene_list_page():    
    create_header()
    create_search_bar()