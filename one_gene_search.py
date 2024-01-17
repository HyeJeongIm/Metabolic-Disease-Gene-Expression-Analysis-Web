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

def plot_data(df, name):
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))  # 3x3 그리드로 설정
    axes = axes.flatten()
    
    for i, (ax, (file, data)) in enumerate(zip(axes, df.items())):
        sns.boxplot(data=data, ax=ax)
        ax.set_title(f"Box Plot of {file}")
        ax.set_ylabel("Expression Level")

    for j in range(i+1, 9):
        fig.delaxes(axes[j])
        
    st.pyplot(fig)

def create_box_plot_page(name):
    folder_path = './data/Gene Expression'
    files = os.listdir(folder_path)
    dfs = {}  
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        df = load_data(file_path, name)
        if not df.empty:
            dfs[file[:-4]] = df  # 파일 확장자를 제외한 이름을 키로 사용

    # 모든 데이터프레임을 그리드에 표시
    if dfs:
        plot_data(dfs, name)
    else:
        st.error(f"No data available for {name} in any of the files.")