import streamlit as st
import one_gene_network_diagram, main_page

def create_search_bar_network():
    with st.expander("Search"):
        gene_name = st.text_input('Enter the gene name', key="gene_input")
        
        if st.button('Search'):
            st.session_state['search_pressed'] = True
            st.session_state['gene_name'] = gene_name
        
        # 검색이 수행된 후에만 박스 플롯 페이지 생성 함수를 호출
        if 'search_pressed' in st.session_state and st.session_state['search_pressed']:
            one_gene_network_diagram.create_network_page(st.session_state['gene_name'])

        if st.button('Back'):
            if 'search_pressed' in st.session_state:
                st.session_state['search_pressed'] = False
                st.session_state['gene_name'] = '' 
                st.experimental_rerun()  


def network_page():
    main_page.create_header()
    create_search_bar_network()