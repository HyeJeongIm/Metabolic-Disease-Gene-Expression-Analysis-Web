import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def create_header():
    st.title('Multiple Gene Expression')

def show_heatmap(df, genes):
    
    if genes:
        df_filtered = df.set_index('Gene name').loc[genes, genes]
        plt.figure(figsize=(10, 8))
        sns.heatmap(df_filtered, annot=True, cmap='Purples')
        st.pyplot(plt)
    else:
        st.error('Please enter valid gene names.')
        
def write_gene_list_page():
    create_header()
    
    genes_input = st.text_area('Enter gene names:')
    genes_list = [gene.strip() for gene in genes_input.split('\n') if gene]
    
    file_path = 'data\Gene-Gene Expression Correlation\Full Correlation Matrix\GeneGeneCorrelation_Adipose_LH_Sample.txt'
    
    df = pd.read_csv(file_path, sep='\t')
    
    show_heatmap(df, genes_list)
