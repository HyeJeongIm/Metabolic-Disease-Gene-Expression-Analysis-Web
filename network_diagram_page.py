import streamlit as st
import one_gene_network_diagram
 
def network_page():
    if 'stage' not in st.session_state:
        st.session_state.stage = 0

    def set_state(i):
        st.session_state.stage = i

    if st.session_state.stage == 0:
        st.button('유전자 1개 검색', on_click=set_state, args=[1])
        
    if st.session_state.stage >= 1:
        st.markdown("## 🧬 유전자를 입력해주세요")
        st.markdown(
        """
        <style>
        .stTextInput > div > div > input {
            border: 4px solid #ff4b4b; /* 빨간색 테두리 적용 */
        }
        </style>
        """,
        unsafe_allow_html=True,
        )
        
        name = st.text_input('', on_change=set_state, args=[2], key="gene_input")

        col1, col2 = st.columns([1, 4])
        with col1:
            st.button('Back', on_click=set_state, args=[0])
            st.button('Next', on_click=set_state, args=[2])   
            
    if st.session_state.stage == 2:
        
        one_gene_network_diagram.create_network_page(name)
        st.button('Back', on_click=set_state, args=[1])  