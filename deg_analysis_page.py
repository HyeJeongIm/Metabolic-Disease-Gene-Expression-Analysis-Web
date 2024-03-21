import streamlit as st
import deg_analysis
import data_loader

def create_header():
    st.title('DEG Analysis')

def create_search_area():
    if 'deg_pressed' not in st.session_state:
        st.session_state['deg_pressed'] = False

    if not st.session_state['deg_pressed']:
        # selectbox를 위한 값 선언
        sample_class = ['Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']
        p_value = [0.05, 0.01, 0.001]
        fold_change = [1.5, 2, 3]
        pathway = ['Pathway', 'GO', 'Hallmark']

        # search box들
        sample_choice = st.multiselect('Choose two groups', sample_class, max_selections=2, key='sample_input')
        p_value_choice = st.selectbox('Choose the p-value', p_value, key='p_value_input')
        fold_change_choice = st.selectbox('Choose the Fold-change', fold_change, key='fold_change_input')
        pathway_choice = st.multiselect('Choose the pathway', pathway, key='pathway_input')
        
        samples = data_loader.format_sample(sample_choice)
    
        st.session_state['deg_sample'] = samples
        st.session_state['deg'] = data_loader.format_sample_original(samples)
        st.session_state['p_value'] = p_value_choice
        st.session_state['fold'] = fold_change_choice
        st.session_state['pathway'] = pathway_choice

        if st.button('Search'):
            st.session_state['deg_pressed'] = True
            st.rerun()
    else:
        st.success(f'''
                First sample group : {st.session_state['deg'][0]} \n
                Second sample group : {st.session_state['deg'][1]} \n
                P-value : {st.session_state['p_value']} \n
                Fold 2 change : {st.session_state['fold']} \n
                Pathway Enrichment : {st.session_state['pathway']}
               ''')

        deg_analysis.plot_pca(st.session_state['deg_sample'])
        deg_analysis.plot_volcano(st.session_state['deg_sample'], st.session_state['p_value'], st.session_state['fold'])
        deg_analysis.plot_pathway(st.session_state['deg_sample'][0], st.session_state['deg_sample'][1], st.session_state['p_value'], st.session_state['fold'], st.session_state['pathway'])

        if st.button('Back'):
            st.session_state['deg_pressed'] = False
            st.experimental_rerun()

def write_deg_page():
    create_header()
    create_search_area()