import streamlit as st
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots



def create_header():
    st.title('Multiple Gene Expression')
        
def show_heatmap(genes_list, base_path):
    if genes_list:
        file_list = os.listdir(base_path)
        file_list = [file for file in file_list if file.endswith('.txt')]

        total_files = len(file_list)
        cols = 3  
        rows = (total_files + cols - 1) // cols

        fig = make_subplots(
            rows=rows, 
            cols=cols, 
            subplot_titles=file_list,
            horizontal_spacing=0.005,  # 간격 조정
            vertical_spacing=0.05

        )

        for i, file in enumerate(file_list, start=1):
            file_path = os.path.join(base_path, file)
            try:
                df = pd.read_csv(file_path, sep='\t', index_col='Gene name')
                heatmap_data = df.loc[genes_list]

                fig.add_trace(
                    go.Heatmap(
                        z=heatmap_data.values, 
                        x=heatmap_data.columns.tolist(), 
                        y=heatmap_data.index.tolist(), 
                        colorscale='Purples',
                    ),
                    row=(i-1)//cols + 1, col=(i-1)%cols + 1
                )
            except FileNotFoundError:
                st.error(f'File not found: {file}')
            except KeyError:
                st.error(f'One or more genes not found in file: {file}')

        fig.update_layout(
            width=900, 
            height=300 * rows, 
            title_text='Heatmaps for All Files in Z_Score Directory',
            showlegend=False
        )

        fig.update_xaxes(showticklabels=False)
        st.plotly_chart(fig)

    else:
        st.error('Please enter at least one gene name.')
        
def write_gene_list_page():    
    create_header()
    
    genes_input = st.text_area('Enter gene names:')
    genes_list = [gene.strip() for gene in genes_input.split('\n') if gene]
    
    st.write(f"Number of genes entered: {len(genes_list)}")  # Debug print
    base_path = 'data/Gene Expression/Z_Score'

    if st.button('Search'):
        show_heatmap(genes_list, base_path)
