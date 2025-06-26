import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from openai import OpenAI
from relationship_types import RELATIONSHIP_TYPES

# 🔐 Load OpenAI API client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 🔧 Streamlit page settings
st.set_page_config(page_title="Dark Souls Knowledge Graph", layout="wide")
st.title("🕹️ Dark Souls Knowledge Graph Explorer")

# 🔌 Neo4j connection
uri = st.secrets["NEO4J_URI"]
user = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]

@st.cache_resource
def create_driver(uri, user, password):
    return GraphDatabase.driver(uri, auth=(user, password))

driver = create_driver(uri, user, password)

# 🧠 Helper to run Cypher queries
@st.cache_data
def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        data = [record.data() for record in result]
    return pd.DataFrame(data)

# 📦 Query to build graph data
def build_query(limit):
    return f"""
    MATCH (n:Entity)-[r]->(m:Entity)
    RETURN n.id AS source, type(r) AS relation, m.id AS target
    LIMIT {limit}
    """

# 📊 Graph preview section
st.subheader("📄 Graph Data Sample")
default_limit = 100
df = run_query(build_query(default_limit))
st.dataframe(df)

# 🎛️ Slider to control graph size
limit = st.slider("Number of relationships to visualize", 10, 500, 100, key="limit_slider")
df = run_query(build_query(limit))

# 🌐 Build and render PyVis network graph
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

# 💬 Natural Language Question Section
st.subheader("💬 Ask a question about the Dark Souls graph")

question = st.text_input("Type your question (e.g., 'Which weapons are effective against dragons?')")

# 🧠 Generate Cypher query using GPT-4 and valid relation types
def generate_cypher_query(natural_question):
    relation_list = ", ".join(f"`{rel}`" for rel in RELATIONSHIP_TYPES)

    system_prompt = f"""
You are a Cypher assistant that ONLY generates Cypher queries for a Neo4j graph.

GRAPH STRUCTURE:
- Nodes are labeled `Entity` and each has an `id` property.
- Edges are labeled with REAL RELATIONSHIP TYPES. Valid types are: {relation_list}

❌ Forbidden types: related_to, associated_with, connected_to, is_related_to, is_associated_with, has_relation, has_association
✅ Only use exact types from the list above.

SPECIAL CASES:
- If the user's question mentions a **general category** like "shields", "swords", or "knights", do NOT assume it is the exact node id.
  Instead, use a partial match:
    WHERE toLower(n.id) CONTAINS "shield"
- This ensures broader coverage across similar node names.

EXAMPLES:
- ❌ WRONG: MATCH (a:Entity {{id: "shields"}})-[r]->(b)
- ✅ CORRECT: MATCH (a:Entity)-[r]->(b) WHERE toLower(a.id) CONTAINS "shield"

If unsure, fall back to:
  MATCH (a:Entity {{id: 'X'}})-[r]->(b:Entity) RETURN type(r), b.id

YOUR TASK:
- Read the user's natural language question
- Identify the intent
- Translate it into a valid Cypher query using ONLY the allowed relationships

OUTPUT:
Only return a single Cypher query. DO NOT add explanations.
    """.strip()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": natural_question}
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()

# ▶️ Run QA from input
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
