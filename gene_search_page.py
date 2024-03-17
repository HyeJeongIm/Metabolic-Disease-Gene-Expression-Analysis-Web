import streamlit as st
import one_gene_search
import pandas as pd
import re

def create_header(gene_name=None):
    st.image('images/logo.png', width=100)
    if gene_name:
        st.title(f"One Gene Search: '{gene_name}'")
    else:
        st.title('One Gene Search')

'''
 v1
    유전자 이름 삭제
    맨 아래 back button 생성
    이전페이지로 넘어감
'''
def check_gene_name(gene_name, path):
    df = pd.read_csv(path, sep='\t') 
    # Assuming 'Gene name' is the column title, adjust if it's named differently
    if gene_name in df['Gene name'].values:
        error_message = ""
        valid_gene = gene_name
    else:
        error_message = f"Gene name not found: {gene_name}"
        valid_gene = gene_name
        
    return valid_gene, error_message

def create_search_bar():
    threshold_key = 'threshold_gene_search'

    if 'search_pressed' not in st.session_state:
        st.session_state['search_pressed'] = False
        
    if 'gene_name' not in st.session_state:
        st.session_state['gene_name'] = ""
        
    if not st.session_state['search_pressed']:
        gene_name = st.text_input('Enter the gene name', value=st.session_state['gene_name'], key="gene_input")
        if st.button('Search'):
            st.session_state['search_pressed'] = True
            st.session_state['gene_name'] = gene_name  
            st.experimental_rerun()
    else:
        path = 'data/Gene Expression/Raw/GeneExpression_Adipose_LH.txt'
        _, error_message = check_gene_name(st.session_state['gene_name'], path)
        
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
                
                valid_threshold = get_threshold(threshold_key, group)
            
                # Apply 버튼은 항상 표시
                _, col2 = st.columns([8, 1])
                with col2:
                    apply_clicked = st.button('Apply')

                if len(valid_threshold) == 2:
                    if valid_threshold is not None:
                        one_gene_search.show_network_diagram(st.session_state['gene_name'], group, valid_threshold)
            
            if group == 'no specific group':
                one_gene_search.show_network_diagram(st.session_state['gene_name'], group)
                
            one_gene_search.show_edge_info(st.session_state['gene_name'])

        if st.button('Back'):
            st.session_state['search_pressed'] = False
            st.session_state['gene_name'] = ""  
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
    
def write_main_page():
    if 'search_pressed' in st.session_state and st.session_state['search_pressed']:
        create_header(st.session_state['gene_name'])
    else:
        create_header()
    create_search_bar()
