import streamlit as st
import one_gene_search

def create_header():
    st.image('images/logo.png', width=100)
    st.title('Metabolic Disease Gene Expression Analysis Web')

def create_data_statistics():
    st.subheader('Data statistics')
    st.image('images/test_image.jpg')

def show_main_image():
    st.image('./images/main_image.png')
    
def write_main_page():
    create_header()
    show_main_image()
    create_data_statistics()