import streamlit as st
import re 
import gene_list
import pandas as pd

def create_header():
    st.title('Multiple Gene Expression')
    
def check_gene_names(genes_list, path):
    # Reading the file
    df = pd.read_csv(path, delimiter='\t')  
    all_genes = pd.concat([df['Gene'], df['Gene.1']]).unique()  

    # Checking for mismatches
    mismatches = [gene for gene in genes_list if gene not in all_genes]

    if mismatches:
        error_message = f"Gene names not found: {', '.join(mismatches)}"
        valid_genes = [gene for gene in genes_list if gene not in mismatches]
    else:
        error_message = ""
        valid_genes = genes_list

    return valid_genes, error_message

def create_search_bar():
    base_path = 'data/Gene Expression/Z_Score'

    if 'pressed' not in st.session_state:
        st.session_state['pressed'] = False
    if 'gene_list' not in st.session_state:
        st.session_state['gene_list'] = []
    # if 'threshold' not in st.session_state:
    #     st.session_state['threshold'] = 0.9
    
    if not st.session_state['pressed']:
        genes_input = st.text_area('Enter gene names:')
        genes_list = re.split('[ ,\t\n]+', genes_input.strip())

        if genes_input.strip() == '':
            genes_list = []

        st.write(f"Number of genes entered: {len(genes_list)}")
        
        if st.button('Search', key='search_multiple_genes'):
            st.session_state['pressed'] = True
            st.session_state['gene_list'] = genes_list
            st.experimental_rerun()

    else:
        path = 'data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_Adipose_LH_0.5.txt'
        valid_genes, error_message = check_gene_names(st.session_state['gene_list'], path.replace('\\', '/'))

        if error_message:
            st.error(error_message)
        else:
            st.session_state['gene_list'] = valid_genes
                
            gene_list.show_heatmap(st.session_state['gene_list'], base_path)
            st.subheader(f"**Protein interactions between input Genes**")

            sample_class = ['no specific group', 'Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
                            'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
                            'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']

            group = st.selectbox('Choose a sample group for annotation', sample_class, key='group', index=0)
            
            if 'threshold' not in st.session_state:
                st.session_state['threshold'] = 0.9  # 기본 임계값으로 0.9를 설정
                
            valid_threshold = get_threshold(group) 

            _, col2 = st.columns([8, 1])
            with col2:
                apply_clicked = st.button('Apply')

            if len(valid_threshold) == 2:
                if valid_threshold[0] is not None:
                    gene_list.show_network_diagram(st.session_state['gene_list'], valid_threshold[1], valid_threshold[0])
            
        if st.button('Back'):
            st.session_state['pressed'] = False
            st.session_state['gene_list'] = ""  
            st.experimental_rerun()
            
def get_threshold(group):
    threshold_str = st.text_input('Enter threshold of absolute correlation coefficient (minimum: 0.5)', value=str(st.session_state.get('threshold', 0.9)), key='co_threshold')
    try:
        threshold = float(threshold_str)
        if threshold < 0.5 and group =='no specific group':
            return [threshold, group]
        elif threshold < 0.5:
            st.error('Please try a higher correlation threshold.')
            return 'None'
        else:
            return [threshold, group]  
    except ValueError:
        st.error('Please enter a valid float number.')
        return None 
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


# def create_search_bar():
#     base_path = 'data/Gene Expression/Z_Score'

#     genes_input = st.text_area('Enter gene names:')
#     genes_list = re.split('[ ,\t\n]+', genes_input.strip())

#     if genes_input.strip() == '':
#         genes_list = []

#     st.write(f"Number of genes entered: {len(genes_list)}")

#     if st.button('Search'):
#         st.session_state['pressed'] = True
#         st.session_state['gene_list'] = genes_list
#         st.session_state['create_network_pressed'] = False

#         path = 'data/Gene-Gene Expression Correlation/Correlation Higher Than 0.5/GeneGene_HighCorrelation_Adipose_LH_0.5.txt'
#         valid_genes, error_message = check_gene_names(genes_list, path.replace('\\', '/'))  

#         if error_message:
#             st.error(error_message)

#         st.session_state['gene_list'] = valid_genes

#     if 'pressed' in st.session_state and st.session_state['pressed']:
#         gene_list.show_heatmap(st.session_state['gene_list'], base_path)

#         st.subheader(f"**Protein interactions between input Genes**")

#         sample_class = ['no specific group', 'Adipose [LH]', 'Adipose [OH]', 'Adipose [OD]',
#                         'Liver [LH]', 'Liver [OH]', 'Liver [OD]',
#                         'Muscle [LH]', 'Muscle [OH]', 'Muscle [OD]']

#         group = st.selectbox('Choose a sample group for annotation', sample_class, key='group', index=0)
#         threshold = str_to_float(default=0.9)

#         gene_list.show_network_diagram(st.session_state['gene_list'], group, threshold)

        
def write_gene_list_page():    
    create_header()
    create_search_bar()

def str_to_float(default=0.9):
    threshold_str = st.text_input('Enter threshold value', value=str(default))
    try:
        return float(threshold_str)
    except ValueError:
        st.error("Please enter a valid float number for the threshold.")
        return default 