import streamlit as st
from streamlit_option_menu import option_menu
import main_page, gene_list_page, deg_page, co_page

def create_layout():
    with st.sidebar:
        page = option_menu("Menu", ["Main", "Gene List", "DEG Analysis", "Co-expression", 'Analysis'],
                            icons=['house', 'list-columns', 'clipboard-data', 'bar-chart'],
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
    elif page == 'Gene List':
        gene_list_page.write_gene_list_page()
    elif page == 'DEG Analysis':
        deg_page.write_deg_page()
    elif page == 'Co-expression':
        co_page.write_co_page()
    elif page == 'Analysis':
        pass

def main():
    create_layout()    

if __name__ == "__main__":
    main()
    
    