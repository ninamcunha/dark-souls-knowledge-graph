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

st.markdown("""
Welcome to the **Dark Souls Knowledge Graph Explorer**

This interactive tool allows you to explore the Dark Souls universe through a knowledge graph built from item descriptions and lore.

**Here’s what you can do:**
- Preview the dataset as a table of relationships.
- Explore a dynamic graph of up to 500 relationships.
- Ask questions in natural language and generate Cypher queries.
- View the results in a table and visual subgraph.
- Get an automatic interpretation of what the results mean.

Use the slider and input tools below to start exploring!
""")


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

st.markdown("## Mapping the Dark Souls Universe")

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

# Session state initialization
if "question_input" not in st.session_state:
    st.session_state["question_input"] = ""
if "selected_question" not in st.session_state:
    st.session_state["selected_question"] = ""
if "cypher_query" not in st.session_state:
    st.session_state["cypher_query"] = ""
if "query_result" not in st.session_state:
    st.session_state["query_result"] = None
if "clear_trigger" not in st.session_state:
    st.session_state["clear_trigger"] = False

# UI layout for inputs
st.session_state["question_input"] = st.text_input(
    "Type your question (e.g., 'Which weapons are wielded by Black Knights?')",
    value=st.session_state["question_input"]
)

st.markdown("Or pick from predefined questions:")
suggested_questions = [
    "Which weapons are wielded by Black Knights?",
    "What weapons are effective against specific enemy types?",
    "What skills are associated with specific weapons?",
    "What properties or affiliations do shields reveal?",
    "Who are the Black Knights related to?",
]
placeholder_option = "— Select a predefined question —"
selected_index = (
    suggested_questions.index(st.session_state["selected_question"]) + 1
    if st.session_state["selected_question"] in suggested_questions
    else 0
)
st.session_state["selected_question"] = st.selectbox(
    "Predefined question", [placeholder_option] + suggested_questions, index=selected_index
)

# Determine final question
final_question = st.session_state["question_input"] or (
    st.session_state["selected_question"] if st.session_state["selected_question"] != placeholder_option else ""
)

# Buttons
col1, col2 = st.columns([1, 1])
run_clicked = col1.button("Run Question")
clear_clicked = col2.button("Clear")

# Clear logic
if clear_clicked:
    st.session_state["question_input"] = ""
    st.session_state["selected_question"] = ""
    st.session_state["cypher_query"] = ""
    st.session_state["query_result"] = None
    st.session_state["clear_trigger"] = True

# Generate Cypher query
def generate_cypher_query(natural_question):
    relation_list = ", ".join(f"`{rel}`" for rel in RELATIONSHIP_TYPES)
    system_prompt = f"""
You are a Cypher expert translating natural language into Neo4j Cypher queries.

GRAPH STRUCTURE:
- Nodes are labeled `Entity` and have an `id` property.
- Edges use only the following relationship types: {relation_list}

RULES:
- Use only the exact relationships above. Do not invent or conjugate them.
  ❌ For example, do NOT use "wielded_by" if the real relation is "wield".
- Do not use generic terms like "related_to", "associated_with", "connected_to", etc.

WHEN RETURNING RESULTS:
- Always use: RETURN a.id AS source, type(r) AS relation, b.id AS target

WHEN MATCHING:
- If the question refers to a specific entity (e.g. "Black Knights"), use exact match:
  MATCH (a:Entity {{id: "Black Knights"}})-[r]->(b:Entity)

- If the question refers to a category (e.g. "shields"), use partial match:
  MATCH (a:Entity)-[r]->(b:Entity)
  WHERE toLower(a.id) CONTAINS "shield"

IF UNSURE:
Use fallback pattern with correct aliases:
  MATCH (a:Entity {{id: "X"}})-[r]->(b:Entity) RETURN a.id AS source, type(r) AS relation, b.id AS target

IMPORTANT:
Only return the Cypher query. Do not include explanations.
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


# Run logic
if run_clicked and final_question.strip():
    with st.spinner("Generating Cypher query..."):
        try:
            cypher_query = generate_cypher_query(final_question)
            st.session_state["cypher_query"] = cypher_query

            with driver.session() as session:
                result = session.run(cypher_query)
                st.session_state["query_result"] = [record.data() for record in result]

        except Exception as e:
            st.error(f"Failed to execute query: {e}")
elif run_clicked:
    st.warning("Please enter or select a question first.")

# Display results
if st.session_state["cypher_query"]:
    st.code(st.session_state["cypher_query"], language="cypher")

if st.session_state["query_result"]:
    st.dataframe(pd.DataFrame(st.session_state["query_result"]))

    # Graph visualization based on query result
    result_df = pd.DataFrame(st.session_state["query_result"])

    if {"source", "relation", "target"}.issubset(result_df.columns):
        st.markdown("### Subgraph Visualization from Query")

        # Build directed graph
        subgraph = nx.from_pandas_edgelist(
            result_df,
            source="source",
            target="target",
            edge_attr="relation",
            create_using=nx.DiGraph()
        )

        sub_net = Network(height="600px", width="100%", bgcolor="#1e1e1e", font_color="white", directed=True)

        for node in subgraph.nodes():
            sub_net.add_node(node, label=node, title=node)

        for source, target, data in subgraph.edges(data=True):
            sub_net.add_edge(source, target, title=data["relation"], label=data["relation"])

        sub_net.repulsion()
        sub_net.save_graph("subgraph.html")

        with open("subgraph.html", "r", encoding="utf-8") as HtmlFile:
            components.html(HtmlFile.read(), height=600)

        # ✅ Interpretation Section
        def generate_interpretation(df, question):
            df_sample = df.head(10).to_dict(orient="records")
            user_prompt = f"""
You are an expert in Dark Souls lore and graph analysis. Based on the question and the extracted relationships from a knowledge graph, write a short paragraph (3-5 sentences) explaining what the data reveals.

Question:
{question}

Relationships:
{df_sample}

Interpretation:
""".strip()

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are an expert at interpreting graph data from Dark Souls."},
                          {"role": "user", "content": user_prompt}],
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()

        st.markdown("### Interpretation of Results")
        with st.spinner("Generating interpretation..."):
            interpretation = generate_interpretation(result_df, final_question)
            st.write(interpretation)
