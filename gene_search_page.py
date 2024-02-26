import streamlit as st
import one_gene_search

def create_header():
    st.image('images/logo.png', width=100)
    st.title('Metabolic Disease Gene Expression Analysis Web')

def create_search_bar():
    with st.expander("Search"):
        gene_name = st.text_input('Enter the gene name', key="gene_input")

        if st.button('Search'):
            st.session_state['search_pressed'] = True
            st.session_state['gene_name'] = gene_name
        
        # 검색이 수행된 후에만 수행
        if 'search_pressed' in st.session_state and st.session_state['search_pressed']:
            one_gene_search.show_box_plot(st.session_state['gene_name'], z_score=False)
            one_gene_search.show_network_diagram(st.session_state['gene_name'])

        # if st.button('Back'): 
        #     if 'search_pressed' in st.session_state:
        #         st.session_state['search_pressed'] = False
        #         st.session_state['gene_name'] = '' 
        #         st.experimental_rerun()  

def create_data_statistics():
    st.subheader('Data statistics')
    st.image('images/test_image.jpg')

def show_main_image():
    st.image('./images/main_image.png')
    
def write_main_page():
    create_header()
    create_search_bar()
    show_main_image()
    create_data_statistics()