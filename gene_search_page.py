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
        sample_class = ['Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                        'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                        'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']

        group = st.selectbox('Choose a sample group for annotation', sample_class, key='group')
        threshold = str_to_float()
        one_gene_search.show_network_diagram(st.session_state['gene_name'], group, threshold)
        
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
def write_main_page():
    create_header()
    create_search_bar()
