import streamlit as st
import re 
import gene_list

def create_header():
    st.title('Multiple Gene Expression')
    
def create_search_bar():
    base_path = 'data/Gene Expression/Z_Score'

    genes_input = st.text_area('Enter gene names:')
    genes_list = re.split('[ ,\t\n]+', genes_input.strip())
    st.write(f"Number of genes entered: {len(genes_list)}")  # Debug print
    
    if st.button('Search'):
        st.session_state['pressed'] = True
        st.session_state['gene_list'] = genes_list

    if 'pressed' in st.session_state and st.session_state['pressed']:
        gene_list.show_heatmap(st.session_state['gene_list'], base_path)
        gene_list.show_network_diagram(st.session_state['gene_list'])
        
def write_gene_list_page():    
    create_header()
    create_search_bar()
