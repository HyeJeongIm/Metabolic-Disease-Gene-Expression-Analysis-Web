# library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

def load_data(file_path, name):
    
    df = pd.read_csv(file_path, sep='\t')
    
    one_gene_df = df[df['Gene name'] == name].drop('Gene name', axis=1).T
    one_gene_df.columns = [name]

    return one_gene_df

def plot_data(df, file, name):

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df)
    plt.ylabel("Expression Level")
    
    st.pyplot(plt)

def create_box_plot_page(name):
    folder_path = './data/Gene Expression'
    
    files = os.listdir(folder_path)
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        df = load_data(file_path, name)
        st.subheader("Box Plot of " + file[:-4] + "_" + name)

        plot_data(df, file[:-4], name)