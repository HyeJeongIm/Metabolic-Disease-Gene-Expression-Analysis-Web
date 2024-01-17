import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

def load_network_data(file_path, name):
    data = pd.read_csv(file_path, sep='\t')
    df = pd.DataFrame(data)

    df_interaction = df[['Official Symbol Interactor A', 'Official Symbol Interactor B']]

    result = df_interaction[(df_interaction['Official Symbol Interactor A'] == name) | (df_interaction['Official Symbol Interactor B'] == name)]

    return result

def plot_pyvis(df):
    net = Network(
        notebook=True,
        directed=False,
        )
    
    sources = df['Official Symbol Interactor A']
    targets = df['Official Symbol Interactor B']

    edge_data = zip(sources, targets)

    for e in edge_data:
        src = e[0]
        dst = e[1]

        net.add_node(src, src, title=src)
        net.add_node(dst, dst, title=dst)
        net.add_edge(src, dst)

    net.show_buttons(filter_=['physics'])
    net.show("pyvis_net_graph.html")

    # Streamlit 앱에 네트워크 표시
    HtmlFile = open('pyvis_net_graph.html', 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, width=1000, height=5000)

def create_network_page(gene_name):
    file_path = 'data\Gene-Gene Interaction\BIOGRID-ORGANISM-Homo_sapiens-4.4.229.tab3.txt'

    df_inter = load_network_data(file_path, gene_name)
 
    plot_pyvis(df_inter)