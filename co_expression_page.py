import streamlit as st
import co_expression
import pandas as pd
import data_loader
def create_header():
    st.title('Co-expression Network Analysis')


def create_search_bar():
    if 'co_pressed' not in st.session_state:
        st.session_state['co_pressed'] = False

    if not st.session_state['co_pressed']:
        sample_class = ['Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                        'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                        'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']
        selected_groups = st.multiselect('Choose one or two sample group for annotation', sample_class, key='co_input', max_selections=2)

        threshold_str = st.text_input('Enter threshold of absolute correlation coefficient (minimum: 0.5)', value=0.5, key='co_threshold')

        samples = data_loader.co_group_format(selected_groups)

        st.session_state['samples'] = samples
        st.session_state['threshold_str'] = threshold_str

        if st.button('Search'):
            st.session_state['co_pressed'] = True
            st.experimental_rerun()
    else:
        try:
            threshold = float(st.session_state['threshold_str'])
            if threshold < 0.5:
                st.error('Please try a higher correlation threshold.')
            co_expression.show_correlation(st.session_state['samples'], threshold)
        except ValueError:
            st.error('Please enter a valid float number.') 
    
        if st.button('Back'):
            st.session_state['co_pressed'] = False  
            st.experimental_rerun()

def write_co_page():
    create_header()
    create_search_bar()