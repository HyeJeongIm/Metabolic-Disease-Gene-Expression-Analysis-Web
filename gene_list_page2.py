import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def create_header():
    st.title('Multiple Gene Expression')
        
def show_heatmap2(genes_list, df):
    if genes_list:
        try:
            heatmap_data = df.loc[genes_list]
            
            st.write(f"Shape of the heatmap data: {heatmap_data.shape}")  # Debug print
            
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values, 
                x=heatmap_data.columns.tolist(), 
                y=heatmap_data.index.tolist(), 
                colorscale='Purples'
            ))
            
            fig.update_layout(
                width=800, 
                height=1000, 
                xaxis=dict(side='bottom'),
                yaxis=dict(autorange='reversed')  
            )
            
            st.plotly_chart(fig)
            
        except KeyError as e:
            st.error(f'Gene not found: {e}')
    else:
        st.error('Please enter at least one gene name.')
        
def write_gene_list_page():    
    create_header()
    
    genes_input = st.text_area('Enter gene names:')
    genes_list = [gene.strip() for gene in genes_input.split('\n') if gene]
    
    st.write(f"Number of genes entered: {len(genes_list)}")  # Debug print
    
    groups = ['Adipose_LH', 'Adipose_OH', 'Adipose_OD',
              'Liver_LH', 'Liver_OH', 'Liver_OD',
              'Muscle_LH', 'Muscle_OH', 'Muscle_OD']
    selected_group = st.selectbox('Select a group:', groups)
    
    file_path = f'data/Gene Expression/Raw/GeneExpression_{selected_group}.txt'
    df = pd.read_csv(file_path, sep='\t', index_col='Gene name')
    
    if st.button('Search'):
        show_heatmap2(genes_list, df)
