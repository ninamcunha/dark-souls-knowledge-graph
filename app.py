
import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from openai import OpenAI
from relationship_types import RELATIONSHIP_TYPES

# Load OpenAI API client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Streamlit page settings
st.set_page_config(page_title="Dark Souls Knowledge Graph", layout="wide")
st.title("Dark Souls Knowledge Graph Explorer")

# Neo4j connection
uri = st.secrets["NEO4J_URI"]
user = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]

@st.cache_resource
def create_driver(uri, user, password):
    return GraphDatabase.driver(uri, auth=(user, password))

driver = create_driver(uri, user, password)

# Helper to run Cypher queries
@st.cache_data
def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        data = [record.data() for record in result]
    return pd.DataFrame(data)

# Query to build graph data
def build_query(limit):
    query = (
        "MATCH (n:Entity)-[r]->(m:Entity) "
        "RETURN n.id AS source, type(r) AS relation, m.id AS target "
        f"LIMIT {limit}"
    )
    return query

# Graph preview section
st.subheader("Graph Data Sample")
default_limit = 100
df = run_query(build_query(default_limit))
st.dataframe(df)

# Slider to control graph size
limit = st.slider("Number of relationships to visualize", 10, 500, 100, key="limit_slider")
df = run_query(build_query(limit))

# Build and render PyVis network graph
G = nx.from_pandas_edgelist(df, source="source", target="target", edge_attr="relation", create_using=nx.DiGraph())
net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)

for node in G.nodes():
    net.add_node(node, label=node, title=node)

for source, target, data in G.edges(data=True):
    net.add_edge(source, target, title=data["relation"], label=data["relation"])

net.repulsion()
net.save_graph("graph.html")

with open("graph.html", "r", encoding="utf-8") as HtmlFile:
    components.html(HtmlFile.read(), height=750)

# Natural Language Question Section
st.subheader("Ask a question about the Dark Souls graph")

question = st.text_input("Type your question (e.g., 'Which weapons are wielded by Black Knights?')")

# Generate Cypher query using GPT-4 and valid relation types
def generate_cypher_query(natural_question):
    relation_list = ", ".join(f"`{rel}`" for rel in RELATIONSHIP_TYPES)

    system_prompt = """
You are a Cypher expert translating natural language into Neo4j Cypher queries.

GRAPH STRUCTURE:
- Nodes are labeled `Entity` and have an `id` property.
- Edges use only the following relationship types: {relation_list}

RULES:
- Use only the above relationships. Do not invent others.
- Do not use relationships like "related_to", "associated_with", or "connected_to".

- If the question refers to a specific entity (e.g. "Black Knights"), use exact match:
  MATCH (a:Entity {{id: "Black Knights"}})-[:wield]->(b:Entity)

- If the question refers to a category (e.g. "shields"), use partial match:
  MATCH (a:Entity)-[r]->(b:Entity) WHERE toLower(a.id) CONTAINS "shield"

If unsure, fall back to:
  MATCH (a:Entity {{id: "X"}})-[r]->(b:Entity) RETURN type(r), b.id

Only return the Cypher query. Do not explain.
""".strip().replace("{relation_list}", relation_list)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": natural_question}
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()

# Run QA from input
if question:
    with st.spinner("Generating Cypher query..."):
        try:
            cypher_query = generate_cypher_query(question)
            st.code(cypher_query, language="cypher")

            with driver.session() as session:
                result = session.run(cypher_query)
                data = [record.data() for record in result]

            if data:
                st.dataframe(pd.DataFrame(data))
            else:
                st.warning("No results found.")
        except Exception as e:
            st.error(f"Failed to execute query: {e}")
