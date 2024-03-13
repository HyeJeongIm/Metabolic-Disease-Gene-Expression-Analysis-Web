import streamlit as st
import re 
import gene_list

def create_header():
    st.title('Multiple Gene Expression')
def create_search_bar():
    base_path = 'data/Gene Expression/Z_Score'

    genes_input = st.text_area('Enter gene names:')
    genes_list = re.split('[ ,\t\n]+', genes_input.strip())

    # 빈 문자열인 경우 빈 리스트로 초기화
    if genes_input.strip() == '':
        genes_list = []
    st.write(f"Number of genes entered: {len(genes_list)}")

    if st.button('Search'):
        st.session_state['pressed'] = True
        st.session_state['gene_list'] = genes_list
        st.session_state['create_network_pressed'] = False

    if 'pressed' in st.session_state and st.session_state['pressed']:
        gene_list.show_heatmap(st.session_state['gene_list'], base_path)

        st.subheader(f"**Protein interactions between input Genes**")

        sample_class = ['no specific group', 'Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                        'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                        'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']

        group = st.selectbox('Choose a sample group for annotation', sample_class, key='group', index=0)
        threshold = str_to_float(default=0.9)

        gene_list.show_network_diagram(st.session_state['gene_list'], group, threshold)

        
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