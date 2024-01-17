import streamlit as st
import one_gene_network_diagram, main_page

def create_search_bar_network():
    with st.expander("Search"):
        gene_name = st.text_input('Enter the gene name', key="gene_input")

def network_page():
    main_page.create_header()
    create_search_bar_network()