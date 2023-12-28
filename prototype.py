import pandas as pd
import numpy as np

# streamlit
import streamlit as st
from streamlit_option_menu import option_menu

## Load data
from sklearn.datasets import load_iris

# library
import matplotlib.pyplot as plt
import seaborn as sns

def draw_heatmap_plot(iris_df):
    numeric_data = iris_df.select_dtypes(include=[np.number])

    st.subheader('Heatmap: Correlation Matrix of Numeric Features')
    fig1, ax1 = plt.subplots()
    sns.heatmap(numeric_data.corr(), annot=True, fmt=".2f", cmap='viridis', ax=ax1)
    st.pyplot(fig1)

    st.subheader('Heatmap: Covariance Matrix of Numeric Features')
    fig2, ax2 = plt.subplots()
    sns.heatmap(numeric_data.cov(), annot=True, fmt=".2f", cmap='coolwarm', ax=ax2)
    st.pyplot(fig2)

# 두 변수 간의 관계를 나타내는 그래프 
def draw_scatter_plot(iris_df):
    st.subheader('Scatter Plot: Sepal Dimensions')
    fig, ax = plt.subplots()
    sns.scatterplot(x='sepal_length', y='sepal_width', hue='species', data=iris_df, ax=ax)
    st.pyplot(fig)

    st.subheader('Scatter Plot: Petal Dimensions')
    fig, ax = plt.subplots()
    sns.scatterplot(x='petal_length', y='petal_width', hue='species', data=iris_df, ax=ax)
    st.pyplot(fig)
    
    st.subheader('Scatter Plot: Sepal Dimensions')
    fig = sns.pairplot(iris_df, hue='species', vars=['sepal_length', 'sepal_width'])
    st.pyplot(fig)

    st.subheader('Scatter Plot: Petal Dimensions')
    fig = sns.pairplot(iris_df, hue='species', vars=['petal_length', 'petal_width'])
    st.pyplot(fig)
    
def draw_diagram(iris_df):
    pass
    
# 집단 간 차이를 확인하고자 할 때 유용
def draw_bar_plot(iris_df):
    st.subheader('Bar Plot: Sepal Length by Species')
    fig, ax = plt.subplots()
    sns.barplot(x='species', y='sepal_length', data=iris_df, ax=ax)
    st.pyplot(fig)

    st.subheader('Bar Plot: Petal Length by Species')
    fig, ax = plt.subplots()
    sns.barplot(x='species', y='petal_length', data=iris_df, ax=ax)
    st.pyplot(fig)

    st.subheader('Horizontal Bar Plot: Petal Length by Species')
    fig, ax = plt.subplots()
    iris_df.groupby('species')['petal_length'].mean().plot(kind='barh', color='teal', ax=ax)
    st.pyplot(fig)
        
def draw_dataframe(iris_df):
    # st.header('1. DataFrame')
    # st.text(': Return table / dataframe')

    st.subheader('01. 5개의 col을 보여줍니다.')
    st.table(iris_df.head())

    st.subheader('02. 스크롤을 포함한 전체 dataframe을 보여줍니다.')
    st.dataframe(iris_df)
    
    #
    st.subheader('03. Interactive Table: Display Selected Number of Rows')
    number = st.number_input('Select number of rows to view', min_value=1, max_value=150, step=1)
    st.dataframe(iris_df.head(number))
    

## 04. analysis page
def write_analysis_page(iris_df):
    # 탭 생성
    tab_titles = ['Table', 'Bar_plot', 'Diagram', 'Scatter', 'Heatmap']
    tabs = st.tabs(tab_titles)
    
    with tabs[0]:
        st.header('Table')
        draw_dataframe(iris_df)
    
    with tabs[1]:
        st.header('Bar_plot')
        draw_bar_plot(iris_df)

    with tabs[2]:
        st.header('Diagram')
        # st.line_chart(data)
        
    with tabs[3]:
        st.header('Scatter')
        draw_scatter_plot(iris_df)
    
    with tabs[4]:
        st.header('Heatmap')
        draw_heatmap_plot(iris_df)

## 03. data page
def write_data_display(iris_df):
    st.write("""
            #### 다음은 사용된 Dataset에 대한 간단한 설명입니다.
            ## Dataset: IRIS

            - \# of raw = 150

            - \# of col = 5 (_꽃받침의 길이, 꽃받침의 너비, 꽃잎의 길이, 꽃잎의 너비, 꽃의 종류_)
                - target = 꽃의 종류
                    - 0: setosa 
                    - 1: versicolor  
                    - 2: virginica  
    
    """)
    
    st.write('#### IRIS dataset을 DataFrame으로 그린 결과입니다.')
    draw_dataframe(iris_df)

## 02. user page
def write_user_page(iris_df):
    
    # select box
    st.subheader('01. Species')
    option = st.selectbox('하나만 선택 가능',
					  ('Human', 'Mouse'))
    
    # multi select box
    st.subheader('02. Developmental Stage')
    options = st.multiselect('여러 개 선택 가능',
						['ICM', 'TE', 'test1', 'test2'],
						['ICM', 'TE'])

    st.write('전체 선택 목록: ')
    for index, j in enumerate(options):
        st.write(index,'. ', j)
        
## 01. main page
def write_main_page():
    st.title('Metabolic Disease Gene Expression Analysis Web')
    st.markdown(" 이 웹 어플리케이션은 **Streamlit**을 활용하여 간단한 시각화 툴을 그려보는 것을 테스트 합니다.")
    st.markdown("\n") 
    st.markdown("왼쪽 Menu tab을 이용하여 사용자가 원하는 page를 선택할 수 있습니다.")
    st.markdown("\n")
    st.markdown("간단한 시각화 결과는 _*Analysis page*_ 를 확인해주세요.")

## layout
def create_layout(iris):
    container = st.sidebar.container()
    container.image('./images/logo.png', width=75)
    with st.sidebar:
        page = option_menu("Menu", ["Main", "User Inputs", "Data Display", 'Analysis'],
                            icons=['house', 'person', 'bar-chart', 'clipboard-data'],
                            menu_icon="app-indicator", default_index=0,
                            styles={
            "container": {"padding": "4!important", "background-color": "#a0a0a0"},
            "icon": {"color": "white", "font-size": "25px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"10px", "--hover-color": "#a0a0a0"},
            "nav-link-selected": {"background-color": "#014f9e"},
        }
        )       
    
    ## iris dataset    
    iris_df = pd.DataFrame(iris.data, columns=iris.feature_names)
    iris_df['target'] = iris['target']
    iris_df['target'] = iris_df['target'].apply(lambda x: 'setosa' if x == 0 else ('versicolor' if x == 1 else 'virginica'))
    iris_df.rename({'sepal length (cm)': 'sepal_length',
           'sepal width (cm)': 'sepal_width',
           'petal length (cm)': 'petal_length',
           'petal width (cm)': 'petal_width',
           'target': 'species'          
          }, inplace=True,axis=1)
    
    if page == 'Main':
        write_main_page()
    if page == 'User Inputs':
        write_user_page(iris_df)
    elif page == 'Data Display':
        write_data_display(iris_df)
    elif page == 'Analysis':
        st.title('Chart Type')
        write_analysis_page(iris_df)

def main():
    iris = load_iris()
    create_layout(iris)
    print()


if __name__ == "__main__":
    main()

# '''

# ## Header/Subheader
# st.header('This is header')
# st.subheader('This is subheader')

# ## Text
# st.text('Hello Streamlit! 이 글은 튜토리얼 입니다.')
# '''