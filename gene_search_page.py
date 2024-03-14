import streamlit as st
import one_gene_search

def create_header():
    st.image('images/logo.png', width=100)
    st.title('One Gene Search')

'''
    test
'''

'''
v0
'''
# def create_search_bar():

#     gene_name = st.text_input('Enter the gene name', key="gene_input")

#     if st.button('Search'):
#         st.session_state['search_pressed'] = True
#         st.session_state['gene_name'] = gene_name
    
#     # 검색이 수행된 후에만 수행
#     if 'search_pressed' in st.session_state and st.session_state['search_pressed']:
#         one_gene_search.show_box_plot(st.session_state['gene_name'], z_score=False)
#         st.subheader(f"**Protein interactions around '{gene_name}'**")

#         # threshold 및 group 선택
#         sample_class = ['no specific group', 'Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
#                         'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
#                         'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']

#         group = st.selectbox('Choose a sample group for annotation', sample_class, key='group', index=0)
#         threshold = str_to_float(default=0.9)
#         one_gene_search.show_network_diagram(st.session_state['gene_name'], group, threshold)


'''
 v1
    유전자 이름 삭제
    맨 아래 back button 생성
    이전페이지로 넘어감
'''


def create_search_bar():

    if 'search_pressed' not in st.session_state:
        st.session_state['search_pressed'] = False
        
    # 'gene_name'을 관리하기 위한 session_state 초기화
    if 'gene_name' not in st.session_state:
        st.session_state['gene_name'] = ""
        
    if not st.session_state['search_pressed']:
        gene_name = st.text_input('Enter the gene name', value=st.session_state['gene_name'], key="gene_input")
        if st.button('Search'):
            st.session_state['search_pressed'] = True
            st.session_state['gene_name'] = gene_name  
            st.experimental_rerun()
    else:
        # 'Search'가 수행된 후의 로직
        
        # box plot
        one_gene_search.show_box_plot(st.session_state['gene_name'], z_score=False)
        st.subheader(f"**Protein interactions around '{st.session_state['gene_name']}'**")

        # threshold 및 group 선택
        sample_class = ['no specific group', 'Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                        'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                        'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']
        group = st.selectbox('Choose a sample group for annotation', sample_class, key='group', index=0)
        threshold = str_to_float(default=0.9)

        one_gene_search.show_network_diagram(st.session_state['gene_name'], group, threshold)

        if st.button('Back'):
            st.session_state['search_pressed'] = False
            st.session_state['gene_name'] = ""  
            st.experimental_rerun()


'''
 v2
    search -> back으로 변경
    back 눌렀을 때, 유전자 이름 남아있음
'''
# def create_search_bar():

#     if 'search_pressed' not in st.session_state:
#         st.session_state['search_pressed'] = False
        
#     # 'gene_name'을 관리하기 위한 session_state 초기화
#     if 'gene_name' not in st.session_state:
#         st.session_state['gene_name'] = ""
        
#     gene_name = st.text_input('Enter the gene name', key="gene_input")
    
#     if st.session_state['search_pressed']:
#         # 'Back' 버튼을 표시하고, 클릭 시 'search_pressed' 상태를 False로 변경
#         if st.button('Back'):
#             st.session_state['search_pressed'] = False
#             st.session_state['gene_name'] = ""  # gene_name을 초기화
#             st.experimental_rerun()
#     else:
#         if st.button('Search'):
#             st.session_state['search_pressed'] = True
#             st.session_state['gene_name'] = gene_name  
#             st.experimental_rerun()  # 'Search' 버튼 클릭 시 페이지를 다시 로드하여 상태 업데이트 반영
    
#     # 검색이 수행된 후에만 수행되는 코드
#     if st.session_state['search_pressed']:
#         one_gene_search.show_box_plot(st.session_state['gene_name'], z_score=False)
#         st.subheader(f"**Protein interactions around '{st.session_state['gene_name']}'**")  # gene_name 변수 대신 session_state 내용을 사용

#         # threshold 및 group 선택
#         sample_class = ['no specific group', 'Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
#                         'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
#                         'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']

#         group = st.selectbox('Choose a sample group for annotation', sample_class, key='group', index=0)
#         threshold = str_to_float(default=0.9)  # 이 함수의 정의가 누락되어 있어 가정한 함수명
#         one_gene_search.show_network_diagram(st.session_state['gene_name'], group, threshold)

        
def str_to_float(default=0.9):
    threshold_str = st.text_input('Enter threshold value', value=str(default))
    try:
        return float(threshold_str)
    except ValueError:
        st.error("Please enter a valid float number for the threshold.")
        return default       
    
def write_main_page():
    create_header()
    create_search_bar()
