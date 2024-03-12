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

        sample_class = ['Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                        'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                        'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']
        group = st.selectbox('Choose a sample group for annotation', sample_class, key='group_list_input')
        threshold = str_to_float()

        if st.button('Apply'):
            st.session_state['create_network_pressed'] = True
        else:
            st.session_state['create_network_pressed'] = False

        gene_list.show_network_diagram(st.session_state['gene_list'], group, threshold)
        
def write_gene_list_page():    
    create_header()
    create_search_bar()

def str_to_float():
    while True:
        input_text = st.text_input('Enter threshold of absolute correlation coefficient', value='0.5')

        if input_text.strip():  # 입력이 비어 있지 않은 경우
            if all(char.isdigit() or char == '.' for char in input_text) and input_text.count('.') <= 1:  # 입력이 숫자 또는 소수점으로만 이루어져 있고, 소수점이 하나 이하인 경우
                input_float = float(input_text)
                return input_float
            else:
                st.error('Please enter a valid float number')
        else:
            st.error('Please enter a value')  # 입력이 비어 있는 경우