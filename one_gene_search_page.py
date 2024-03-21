import streamlit as st
import one_gene_search, data_loader
import pandas as pd
import re

def create_header(gene_name=None):
    st.image('images/logo.png', width=100)
    if gene_name:
        st.title(f"One Gene Search: '{gene_name}'")
    else:
        st.title('One Gene Search')

def draw_initial_one_gene_search_page():
    gene_name = st.text_input('Enter the gene name', value=st.session_state['gene_name'], key="gene_input")
    if st.button('Search'):
        st.session_state['one_gene_search_pressed'] = True
        st.session_state['gene_name'] = gene_name  
        st.rerun()
    
def create_one_gene_search_bar():
    threshold_key = 'threshold_gene_search'

    if 'one_gene_search_pressed' not in st.session_state:
        st.session_state['one_gene_search_pressed'] = False
        
    if 'gene_name' not in st.session_state:
        st.session_state['gene_name'] = ""
        
    if not st.session_state['one_gene_search_pressed']:
        draw_initial_one_gene_search_page()
    else:
        _, error_message = data_loader.check_gene_name(st.session_state['gene_name'])
        
        if len(error_message) != 0:
            st.error(error_message)
        else:
            # box plot
            one_gene_search.show_box_plot(st.session_state['gene_name'], z_score=False)
            st.subheader(f"**Protein interactions around '{st.session_state['gene_name']}'**")

            # threshold 및 group 선택
            sample_class = ['no specific group', 'Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                            'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                            'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']
            group = st.selectbox('Choose a sample group for annotation', sample_class, key='group_search', index=0)
            
            if group != 'no specific group':
                if 'threshold' not in st.session_state:
                    st.session_state['threshold'] = 0.9  # 기본 임계값으로 0.9를 설정
                
                valid_threshold = data_loader.get_threshold(threshold_key, group)
            
                # Apply 버튼은 항상 표시
                _, col2 = st.columns([8, 1])
                with col2:
                    apply_clicked = st.button('Apply')

                if len(valid_threshold) == 2:
                    if valid_threshold is not None:
                        one_gene_search.show_network_diagram(st.session_state['gene_name'], group, valid_threshold)
            
            if group == 'no specific group':
                one_gene_search.show_network_diagram(st.session_state['gene_name'], group)
                
            one_gene_search.show_edge_info()

        if st.button('Back'):
            st.session_state['one_gene_search_pressed'] = False
            st.session_state['gene_name'] = ""  
            st.experimental_rerun()

def write_one_gene_search_page():
    if 'one_gene_search_pressed' in st.session_state and st.session_state['one_gene_search_pressed']:
        create_header(st.session_state['gene_name'])
    else:
        create_header()
        
    create_one_gene_search_bar()