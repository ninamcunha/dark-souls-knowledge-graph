import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import openai
from neo4j import GraphDatabase
from relationship_types import RELATIONSHIP_TYPES

# 🔐 Load OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 🔧 Streamlit page setup
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

# 🧠 Run Cypher query
@st.cache_data
def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        return pd.DataFrame([record.data() for record in result])

# 📦 Base query for graph preview
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

# 🎛️ Slider to control number of edges
limit = st.slider("Number of relationships to visualize", 10, 500, 100, key="limit_slider")
df = run_query(build_query(limit))

# 🌐 Draw PyVis network
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

# 💬 Question Section
st.subheader("💬 Ask a question about the Dark Souls graph")

question = st.text_input("Type your question (e.g., 'Which weapons are effective against dragons?')")

# 🔍 Generate Cypher query using GPT-4 and valid relation types
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
- If the user's question mentions a general category like "shields", "swords", or "knights", do NOT assume it is the exact node id.
  Use partial match:
    WHERE toLower(n.id) CONTAINS "shield"

If unsure, use:
  MATCH (a:Entity {{id: 'X'}})-[r]->(b:Entity) RETURN type(r), b.id

OUTPUT:
Only return a single Cypher query. Do NOT explain.
    """.strip()

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": natural_question}
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()

# ✨ Generate interpretation for the result
def interpret_results(question, df_result):
    user_prompt = f"""
You are an expert in Dark Souls and knowledge graphs. Your job is to interpret Cypher query results based on the following question and table:

QUESTION:
{question}

RESULTS:
{df_result.to_markdown(index=False)}

Explain in clear, concise English what this result reveals.
Do not restate the question. Use bullet points if needed.
    """.strip()

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a concise analyst and writer."},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()

# ▶️ If question is submitted
if question:
    with st.spinner("Generating Cypher query..."):
        try:
            cypher_query = generate_cypher_query(question)
            st.code(cypher_query, language="cypher")

            df_result = run_query(cypher_query)

            if not df_result.empty:
                st.dataframe(df_result)

                # Optional: Update network graph from results
                if {"source", "target", "relation"}.issubset(df_result.columns):
                    G = nx.from_pandas_edgelist(df_result, source="source", target="target", edge_attr="relation", create_using=nx.DiGraph())
                    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
                    for node in G.nodes():
                        net.add_node(node, label=node, title=node)
                    for source, target, data in G.edges(data=True):
                        net.add_edge(source, target, title=data["relation"], label=data["relation"])
                    net.repulsion()
                    net.save_graph("graph_query.html")
                    with open("graph_query.html", "r", encoding="utf-8") as HtmlFile:
                        st.markdown("### 🧭 Graph View of the Answer")
                        components.html(HtmlFile.read(), height=750)

                # Show interpretation
                interpretation = interpret_results(question, df_result)
                st.markdown("### 🧠 Interpretation")
                st.markdown(interpretation)
            else:
                st.warning("No results found.")

        except Exception as e:
            st.error(f"Failed to execute query: {e}")
