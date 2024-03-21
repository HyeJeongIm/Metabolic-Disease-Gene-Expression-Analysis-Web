import streamlit as st
from streamlit_option_menu import option_menu
import main_page, one_gene_search_page, gene_list_page, deg_page, co_expression_page

st.set_page_config(
    page_title="Metabolic Disease",
    page_icon="./images/favicon.ico",
    layout="centered"
)

def create_layout():
    with st.sidebar:
        page = option_menu("Menu", ["Main", "Gene Search" , "Gene List Search", "DEG Analysis", "Co-expression", 'Reference'],
                            icons=['house', 'list-columns', 'clipboard-data', 'bar-chart', 'arrow-repeat', 'clipboard'],
                            menu_icon="app-indicator", default_index=0,
                            styles={
            "container": {"padding": "4!important", "background-color": "#fafafa"},
            "icon": {"color": "black", "font-size": "25px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"10px", "--hover-color": "#fafafa"},
            "nav-link-selected": {"background-color": "#014f9e", "icon-color": "white"},
        }
        )
        
    if page == 'Main':
        main_page.write_main_page()
    elif page == 'Gene Search':
        one_gene_search_page.write_one_gene_search_page()
    elif page == 'Gene List Search':
        gene_list_page.write_gene_list_page()
    elif page == 'DEG Analysis':
        deg_page.write_deg_page()
    elif page == 'Co-expression':
        co_expression_page.write_co_page()
    elif page == 'Reference':
        pass

def main():
    create_layout()    

if __name__ == "__main__":
    main()