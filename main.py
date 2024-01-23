import streamlit as st
from streamlit_option_menu import option_menu
import main_page

def create_layout():
    # 사이드 바 로고
    container = st.sidebar.container()
    container.image('./images/logo.png', width=75)
    with st.sidebar:
        page = option_menu("Menu", ["Main", "User Inputs", "Network Diagram", 'Analysis'],
                            icons=['house', 'person', 'bar-chart', 'clipboard-data'],
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
        pass
    if page == 'User Inputs':
        pass
    elif page == 'Network Diagram':
        pass
    elif page == 'Analysis':
        pass

def main():
    create_layout()    

if __name__ == "__main__":
    main()
    
    