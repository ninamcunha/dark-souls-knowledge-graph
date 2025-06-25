import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# 1. Page config
st.set_page_config(page_title="Dark Souls Knowledge Graph", layout="wide")

st.title("🕹️ Dark Souls Knowledge Graph Explorer")

# 2. Neo4j connection setup
st.sidebar.subheader("Database Connection")

uri = st.sidebar.text_input("URI", "neo4j+s://<YOUR_INSTANCE>.databases.neo4j.io")
user = st.sidebar.text_input("Username", "neo4j")
password = st.sidebar.text_input("Password", type="password")

@st.cache(allow_output_mutation=True)
def create_driver(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver

if uri and user and password:
    driver = create_driver(uri, user, password)
    st.sidebar.success("✅ Connected to Neo4j")
else:
    st.sidebar.warning("Enter your database credentials")

# 3. Query
st.sidebar.subheader("Query Parameters")
limit = st.sidebar.slider("Number of relationships to visualize", 10, 500, 100)

cypher_query = f"""
MATCH (n:Entity)-[r]->(m:Entity)
RETURN n.id AS source, type(r) AS relation, m.id AS target
LIMIT {limit}
"""

# 4. Fetch data
@st.cache(allow_output_mutation=True)
def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        data = [record.data() for record in result]
    return pd.DataFrame(data)

if uri and user and password:
    df = run_query(cypher_query)

    st.subheader("Graph Data Sample")
    st.dataframe(df)

    # 5. Build NetworkX graph
    G = nx.from_pandas_edgelist(df, source="source", target="target", edge_attr="relation", create_using=nx.DiGraph())

    # 6. Pyvis Network
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)

    for node in G.nodes():
        net.add_node(node, label=node, title=node)

    for source, target, data in G.edges(data=True):
        net.add_edge(source, target, title=data['relation'], label=data['relation'])

    net.repulsion()

    # 7. Save and display graph
    net.save_graph("graph.html")
    HtmlFile = open("graph.html", 'r', encoding='utf-8')
    components.html(HtmlFile.read(), height=750)

else:
    st.warning("Please enter database connection info to run the app.")
