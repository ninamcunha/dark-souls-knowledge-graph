import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import openai

# ✅ Load OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 🔧 Page config
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

# 🧠 Run Cypher queries
@st.cache_data
def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        data = [record.data() for record in result]
    return pd.DataFrame(data)

# 📦 Build Cypher query for graph display
def build_query(limit):
    return f"""
    MATCH (n:Entity)-[r]->(m:Entity)
    RETURN n.id AS source, type(r) AS relation, m.id AS target
    LIMIT {limit}
    """

# 📊 Graph preview
st.subheader("📄 Graph Data Sample")
default_limit = 100
df = run_query(build_query(default_limit))
st.dataframe(df)

# 🔧 Slider to control graph size
limit = st.slider("Number of relationships to visualize", 10, 500, 100, key="limit_slider")
df = run_query(build_query(limit))

# 🌐 Build graph with PyVis
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

# 💬 Natural Language to Cypher (GPT-4)
st.subheader("💬 Ask a question about the Dark Souls graph")

question = st.text_input("Type your question (e.g., 'Which weapons are effective against crowds?')")

def generate_cypher_query(natural_question):
    prompt = f"""
You are a helpful assistant. Translate the user's natural language question into a valid Cypher query for a Neo4j graph.

The graph structure is:
- Nodes have label `Entity` and an `id` property.
- All relationships use the generic label `RELATION` with a `type` property that describes the relationship (e.g., 'wield', 'symbolizes').

Always use the following pattern for relationships:
[:RELATION {{type: 'wield'}}]

Only return the Cypher query. No explanations.

Now translate this question:
{natural_question}
    """.strip()

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert Cypher assistant for a Neo4j knowledge graph."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

# ▶️ Run Cypher from user question
if question:
    with st.spinner("Generating Cypher query..."):
        cypher_query = generate_cypher_query(question)
        st.code(cypher_query, language="cypher")

        try:
            with driver.session() as session:
                result = session.run(cypher_query)
                data = [record.data() for record in result]

            if data:
                st.dataframe(pd.DataFrame(data))
            else:
                st.warning("No results found.")
        except Exception as e:
            st.error(f"Failed to execute query: {e}")
