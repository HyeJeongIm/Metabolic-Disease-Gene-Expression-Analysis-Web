import streamlit as st
import one_gene_search

def create_header():
    st.image('images\logo.png', width=100)
    st.title('Metabolic Disease Gene Expression Analysis Web')

def create_search_bar():
    with st.expander("Search"):
        gene_name = st.text_input('Enter the gene name')

def create_advanced_search_bar():
    with st.expander("Advanced Search"):
        gene_name = st.text_input('Enter the gene name')

def create_tabs():
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["RNA expression", "DNA methylation", "Histone modification", "Chromatin accessibility", "DEGs analysis"])
    
    with tab1:
        st.write("RNA expression data visualization...")
    
    with tab2:
        st.write("DNA methylation data visualization...")

def create_data_statistics():
    st.subheader('Data statistics')
    st.image('images/test_image.jpg')

    
def write_main_page():
    create_header()
    create_search_bar()
    create_tabs()
    create_data_statistics()
    
    # if 'stage' not in st.session_state:
    #     st.session_state.stage = 0

    # def set_state(i):
    #     st.session_state.stage = i

    # if st.session_state.stage == 0:
    #     st.button('유전자 1개 검색', on_click=set_state, args=[1])
        
    # if st.session_state.stage >= 1:
    #     st.markdown("## 🧬 유전자를 입력해주세요")
    #     st.markdown(
    #     """
    #     <style>
    #     .stTextInput > div > div > input {
    #         border: 4px solid #ff4b4b; /* 빨간색 테두리 적용 */
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    #     )
        
    #     name = st.text_input('', on_change=set_state, args=[2], key="gene_input")

    #     col1, col2 = st.columns([1, 4])
    #     with col1:
    #         st.button('Back', on_click=set_state, args=[0])
    #         st.button('Next', on_click=set_state, args=[2])    

    # if st.session_state.stage == 2:
        
    #     one_gene_search.create_box_plot_page(name)
    #     st.button('Back', on_click=set_state, args=[1])
