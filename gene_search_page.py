import streamlit as st
import one_gene_search

def create_header():
    st.image('images/logo.png', width=100)
    st.title('One Gene Search')

def create_search_bar():

    gene_name = st.text_input('Enter the gene name', key="gene_input")

    if st.button('Search'):
        st.session_state['search_pressed'] = True
        st.session_state['gene_name'] = gene_name
    
    # 검색이 수행된 후에만 수행
    if 'search_pressed' in st.session_state and st.session_state['search_pressed']:
        one_gene_search.show_box_plot(st.session_state['gene_name'], z_score=False)
        st.subheader(f"**Protein interactions around '{gene_name}'**")

        # threshold 및 group 선택
        sample_class = ['no specific group', 'Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                        'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                        'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']

        group = st.selectbox('Choose a sample group for annotation', sample_class, key='group', index=0)
        threshold = str_to_float(default=0.9)
        one_gene_search.show_network_diagram(st.session_state['gene_name'], group, threshold)
        
def str_to_float(default=0.9):
    threshold_str = st.text_input('Enter threshold value', value=str(default))
    try:
        return float(threshold_str)
    except ValueError:
        st.error("Please enter a valid float number for the threshold.")
        return default       
    
def write_main_page():
    create_header()
    create_search_bar()
