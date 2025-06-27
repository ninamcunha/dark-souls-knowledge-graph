import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from openai import OpenAI
from relationship_types import RELATIONSHIP_TYPES
import re

# Setup
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
driver = GraphDatabase.driver(uri, auth=(user, password))

@st.cache_data
def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        return pd.DataFrame([record.data() for record in result])

def build_query(limit):
    return (
        "MATCH (n:Entity)-[r]->(m:Entity) "
        "RETURN n.id AS source, type(r) AS relation, m.id AS target "
        f"LIMIT {limit}"
    )

# Graph data sample
st.subheader("Graph Data Sample")
df = run_query(build_query(100))
st.dataframe(df)

# Full graph slider
st.markdown("## Mapping the Dark Souls Universe")
limit = st.slider("Number of relationships to visualize", 10, 500, 100, key="limit_slider")
df = run_query(build_query(limit))

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

# Question section
st.subheader("Ask a question about the Dark Souls graph")

suggested_questions = [
    "Which weapons are wielded by Black Knights?",
    "What weapons are effective against specific enemy types?",
    "What skills are associated with specific weapons?",
    "What properties or affiliations do shields reveal?",
    "Who are the Black Knights related to?",
]
placeholder_option = "— Select a predefined question —"

if "question_input" not in st.session_state:
    st.session_state["question_input"] = ""
if "selected_question" not in st.session_state:
    st.session_state["selected_question"] = ""

question_input = st.text_input("Type your question:", value=st.session_state["question_input"])
if question_input.strip():
    st.session_state["selected_question"] = ""
st.session_state["question_input"] = question_input

selected_index = (
    suggested_questions.index(st.session_state["selected_question"]) + 1
    if st.session_state["selected_question"] in suggested_questions
    else 0
)
selected_question = st.selectbox(
    "Or pick a predefined question:",
    [placeholder_option] + suggested_questions,
    index=selected_index,
)
if selected_question != placeholder_option:
    st.session_state["question_input"] = ""
    st.session_state["selected_question"] = selected_question

# Final question
final_question = st.session_state["question_input"].strip() or st.session_state["selected_question"].strip()

run_clicked = st.button("Run")
clear_clicked = st.button("Clear")

if clear_clicked:
    for key in ["question_input", "selected_question", "cypher_query", "query_result", "interpretation"]:
        st.session_state[key] = ""
    st.rerun()

# Manual queries and interpretations for the 5 key questions
MANUAL_QUERIES = {
    "Which weapons are wielded by Black Knights?": """
        MATCH (e1:Entity {id: 'Black Knights'})-[:wield]->(e2:Entity)
        RETURN e2.id AS source, 'wield' AS relation, e1.id AS target
        ORDER BY source
    """,
    "What weapons are effective against specific enemy types?": """
        MATCH (w:Entity)-[:is_effective_against]->(e:Entity)
        RETURN w.id AS source, 'is_effective_against' AS relation, e.id AS target
    """,
    "What skills are associated with specific weapons?": """
        MATCH (s:Entity)-[:has_skill]->(k:Entity)
        RETURN s.id AS source, 'has_skill' AS relation, k.id AS target
        ORDER BY source
    """,
    "What properties or affiliations do shields reveal?": """
        MATCH (s:Entity)-[r]->(e:Entity)
        WHERE toLower(s.id) CONTAINS "shield"
        RETURN s.id AS source, type(r) AS relation, e.id AS target
        ORDER BY relation
    """,
    "Who are the Black Knights related to?": """
        MATCH (e1:Entity {id: 'Black Knights'})-[r]->(e2:Entity)
        RETURN e1.id AS source, type(r) AS relation, e2.id AS target
    """,
}

INTERPRETATIONS = {
    "Which weapons are wielded by Black Knights?": (
        "The Black Knights wield two notable weapons: the **Black Knight Sword** and the **Heavy Black Knight Sword**. "
        "These weapons emphasize their brutal and imposing combat style, aligning with their fearsome reputation in the Dark Souls lore."
    ),
    "What weapons are effective against specific enemy types?": (
        "The **Blood Club** is effective against most foes, indicating its versatility in battle. "
        "The **Lightning Broadsword** is particularly effective against crowds, suggesting it excels in encounters with multiple enemies."
    ),
    "What skills are associated with specific weapons?": (
        "Two weapons have explicit skills: the **Dark Bastard Sword** is associated with *Stomp*, "
        "while the **Gargoyle Flame Hammer** has the *Kindled Flurry* skill. "
        "These pairings highlight unique combat mechanics tied to specific gear."
    ),
    "What properties or affiliations do shields reveal?": (
        "Shields in Dark Souls reflect diverse attributes. "
        "Greatshields offer high stability and absorption, while small shields excel at parrying. "
        "Some shields are tied to factions or figures, like the **Sunset Shield** and **Poison Black Iron Greatshield**. "
        "Others are engraved, decorated, or made from rare materials — even carrying symbolic commentary like ridicule or shame."
    ),
    "Who are the Black Knights related to?": (
        "The Black Knights are linked to **chaos demons** and weapons like the **Black Knight Sword**. "
        "They are described as charred and constantly facing larger foes — painting a picture of relentless battle and tragedy. "
        "These relationships reinforce their role as elite warriors shaped by fire and war."
    ),
}

# Run logic
if run_clicked and final_question:
    cypher_query = MANUAL_QUERIES.get(final_question)
    interpretation = INTERPRETATIONS.get(final_question)
    if cypher_query:
        st.session_state["cypher_query"] = cypher_query.strip()
        st.session_state["interpretation"] = interpretation
        result_df = run_query(cypher_query)
        st.session_state["query_result"] = result_df.to_dict(orient="records")
    else:
        st.warning("This question is not recognized. Please use a supported format or predefined question.")
elif run_clicked:
    st.warning("Please enter or select a question.")

# Display results
if st.session_state.get("cypher_query"):
    st.code(st.session_state["cypher_query"], language="cypher")

    result_df = pd.DataFrame(st.session_state.get("query_result", []))
    if result_df.empty:
        st.info("No results returned for this query.")
    else:
        st.markdown("### Query Results")
        st.dataframe(result_df)

        st.markdown("### Subgraph Visualization from Query")
        df_graph = result_df.rename(columns=lambda x: x.lower())
        if {"source", "relation", "target"}.issubset(df_graph.columns):
            G = nx.from_pandas_edgelist(df_graph, source="source", target="target", edge_attr="relation", create_using=nx.DiGraph())
            net = Network(height="600px", width="100%", bgcolor="#1e1e1e", font_color="white", directed=True)
            for node in G.nodes():
                net.add_node(node, label=str(node), title=str(node))
            for source, target, data in G.edges(data=True):
                net.add_edge(source, target, title=data["relation"], label=data["relation"])
            net.repulsion()
            net.save_graph("subgraph.html")
            with open("subgraph.html", "r", encoding="utf-8") as HtmlFile:
                components.html(HtmlFile.read(), height=600)

        if st.session_state.get("interpretation"):
            st.markdown("### Interpretation of Results")
            st.write(st.session_state["interpretation"])
