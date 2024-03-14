import streamlit as st
import one_gene_search
import pandas as pd
def create_header():
    st.image('images/logo.png', width=100)
    st.title('One Gene Search')
    

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
def check_gene_name(gene_name, path):
    df = pd.read_csv(path, sep='\t') 
    # Assuming 'Gene name' is the column title, adjust if it's named differently
    if gene_name in df['Gene name'].values:
        error_message = ""
        valid_gene = gene_name
    else:
        error_message = f"Gene name not found: {gene_name}"
        valid_gene = gene_name
        
    return valid_gene, error_message

def create_search_bar():
    threshold_key = 'threshold_gene_search'

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
        path = 'data/Gene Expression/Raw/GeneExpression_Adipose_LH.txt'
        _, error_message = check_gene_name(st.session_state['gene_name'], path)
        if len(error_message) != 0:
            st.error(error_message)
        else:
            # box plot
            one_gene_search.show_box_plot(st.session_state['gene_name'], z_score=False)
            st.subheader(f"**Protein interactions around '{st.session_state['gene_name']}'**")

            # threshold 및 group 선택
            sample_class = ['no specific group', 'Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                            'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                            'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']
            group = st.selectbox('Choose a sample group for annotation', sample_class, key='group_search', index=0)

            if 'threshold' not in st.session_state:
                st.session_state['threshold'] = 0.9  # 기본 임계값으로 0.9를 설정
                
            valid_threshold = get_threshold(threshold_key, group)
            
            # Apply 버튼은 항상 표시
            _, col2 = st.columns([8, 1])
            with col2:
                apply_clicked = st.button('Apply')

            if len(valid_threshold) == 2:
                if valid_threshold is not None:
                    one_gene_search.show_network_diagram(st.session_state['gene_name'], group, valid_threshold)

            # one_gene_search.show_network_diagram(st.session_state['gene_name'], group, st.session_state['threshold'])

        if st.button('Back'):
            st.session_state['search_pressed'] = False
            st.session_state['gene_name'] = ""  
            st.experimental_rerun()

# def get_threshold():
#     threshold_str = st.text_input('Enter threshold of absolute correlation coefficient (minimum: 0.5)', value=str(st.session_state.get('threshold', 0.9)), key='co_threshold')
#     try:
#         threshold = float(threshold_str)
#         if threshold < 0.5:
#             st.error('Please try a higher correlation threshold.')
#             return None  
#         else:
#             st.session_state['threshold'] = threshold  
#             return threshold  
#     except ValueError:
#         st.error('Please enter a valid float number.')
#         return None  

def get_threshold(threshold_key, group):
    default_threshold = 0.9
    if threshold_key not in st.session_state:
        st.session_state[threshold_key] = default_threshold
    threshold_str = st.text_input('Enter threshold of absolute correlation coefficient (minimum: 0.5)', value=str(st.session_state.get('threshold', 0.9)), key='co_threshold')
    try:
        threshold = float(threshold_str)
        if threshold < 0.5 and group =='no specific group':
            return [threshold, group]
        elif threshold < 0.5:
            st.error('Please try a higher correlation threshold.')
            return [group]  
        else:
            return [threshold, group]  
    except ValueError:
        if group == 'no specific group':
            return [0, group]
        st.error('Please enter a valid float number.')
        return [group] 

'''
    v1-1
        threshold 0.4 일때 그래프 안그려지도록 해야함 
'''
# def create_search_bar():
#     if 'search_pressed' not in st.session_state:
#         st.session_state['search_pressed'] = False
        
#     # 'gene_name'을 관리하기 위한 session_state 초기화
#     if 'gene_name' not in st.session_state:
#         st.session_state['gene_name'] = ""
        
#     if not st.session_state['search_pressed']:
#         gene_name = st.text_input('Enter the gene name', value=st.session_state['gene_name'], key="gene_input")
#         if st.button('Search'):
#             st.session_state['search_pressed'] = True
#             st.session_state['gene_name'] = gene_name  
#             st.experimental_rerun()
#     else:
#         # 'Search'가 수행된 후의 로직
        
#         # box plot
#         one_gene_search.show_box_plot(st.session_state['gene_name'], z_score=False)
#         st.subheader(f"**Protein interactions around '{st.session_state['gene_name']}'**")

#         # threshold 및 group 선택
#         sample_class = ['no specific group', 'Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
#                         'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
#                         'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']
#         group = st.selectbox('Choose a sample group for annotation', sample_class, key='group', index=0)
        
#         if 'threshold' not in st.session_state:
#             st.session_state['threshold'] = 0.9  # 기본 임계값으로 0.9를 설정
#         threshold = get_threshold()

#         if threshold is None:
#             return
#         one_gene_search.show_network_diagram(st.session_state['gene_name'], group, st.session_state['threshold'])

#         if st.button('Back'):
#             st.session_state['search_pressed'] = False
#             st.session_state['gene_name'] = ""  
#             st.experimental_rerun()

# def str_to_float(default=0.9):
#     threshold_str = st.text_input('Enter threshold of absolute correlation coefficient (minimum: 0.5)', value=str(default))
#     try:
#         threshold = float(threshold_str)
#         if threshold < 0.5:
#             st.error("Please try a higher correlation threshold. 0.5 이상의 값을 입력해주세요.")
#             exit()
#         return threshold
#     except ValueError:
#         st.error("Please enter a valid float number. 유효한 실수 값을 입력해주세요.")
#         return None
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


# def get_threshold():
#     threshold_str = st.text_input('Enter threshold of absolute correlation coefficient (minimum: 0.5)', value=str(st.session_state.get('threshold', 0.9)), key='co_threshold')
#     try:
#         threshold = float(threshold_str)
#         if threshold < 0.5:
#             st.error('Please try a higher correlation threshold.')
#             return None  # 유효하지 않은 경우 None을 반환합니다.
#         else:
#             st.session_state['threshold'] = threshold  # 유효한 값을 st.session_state에 저장합니다.
#             return threshold  # 유효한 threshold 값 반환
#     except ValueError:
#         st.error('Please enter a valid float number.')
#         return None  # 변환에 실패한 경우 None을 반환합니다.
# # 기존의 str_to_float 함수를 사용하지 않고, 직접 threshold 값을 처리하는 방식
# def get_threshold(default=0.9):
#     threshold_str = st.text_input('Enter threshold of absolute correlation coefficient (minimum: 0.5)', value=str(st.session_state['threshold']), key='co_threshold')
#     try:
#         threshold = float(threshold_str)
#         if threshold < 0.5:
#             st.error('Please try a higher correlation threshold.')
#         else:
#             st.session_state['threshold'] = threshold  # 유효한 값을 st.session_state에 저장
#     except ValueError:
#         st.error('Please enter a valid float number.') 
# def str_to_float(default=0.9):
#     threshold_str = st.text_input('Enter threshold value', value=str(default))
#     try:
#         return float(threshold_str)
#     except ValueError:
#         st.error("Please enter a valid float number for the threshold.")
#         return default       
    
def write_main_page():
    create_header()
    create_search_bar()
