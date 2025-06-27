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

# Neo4j + OpenAI setup
uri = st.secrets["NEO4J_URI"]
user = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

@st.cache_resource
def create_driver(uri, user, password):
    return GraphDatabase.driver(uri, auth=(user, password))
driver = create_driver(uri, user, password)

@st.cache_data
def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        return pd.DataFrame([record.data() for record in result])

# Graph preview
st.subheader("Graph Data Sample")
df = run_query("MATCH (n:Entity)-[r]->(m:Entity) RETURN n.id AS source, type(r) AS relation, m.id AS target LIMIT 100")
st.dataframe(df)

# Visualization
st.markdown("## Mapping the Dark Souls Universe")
limit = st.slider("Number of relationships to visualize", 10, 500, 100)
df = run_query(f"MATCH (n:Entity)-[r]->(m:Entity) RETURN n.id AS source, type(r) AS relation, m.id AS target LIMIT {limit}")

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

# Session setup
for key in ["question_input", "selected_question", "cypher_query", "query_result", "has_run_query"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "query_result" else None

# Input fields
st.subheader("Ask a question about the Dark Souls graph")
question_input = st.text_input(
    "Type your question (e.g., 'Which weapons are wielded by Black Knights?')",
    value=st.session_state["question_input"]
)
if question_input.strip():
    st.session_state["selected_question"] = ""
st.session_state["question_input"] = question_input

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
selected_question = st.selectbox(
    "Predefined question", [placeholder_option] + suggested_questions, index=selected_index
)
if selected_question != placeholder_option:
    st.session_state["question_input"] = ""
    st.session_state["selected_question"] = selected_question

final_question = ""
if question_input.strip() and selected_question == placeholder_option:
    final_question = question_input.strip()
elif selected_question != placeholder_option and not question_input.strip():
    final_question = selected_question.strip()
final_question = re.sub(r"^\s*\d+\.\s*", "", final_question)

# Manual queries (validated)
manual_queries = {
    "Which weapons are wielded by Black Knights?": """MATCH (e1:Entity {id: 'Black Knights'})-[:wield]->(e2:Entity)
RETURN e2.id AS source, 'wield' AS relation, 'Black Knights' AS target""",
    "What weapons are effective against specific enemy types?": """MATCH (w:Entity)-[:is_effective_against]->(e:Entity)
RETURN w.id AS source, 'is_effective_against' AS relation, e.id AS target""",
    "What skills are associated with specific weapons?": """MATCH (s:Entity)-[:has_skill]->(k:Entity)
RETURN s.id AS source, 'has_skill' AS relation, k.id AS target""",
    "What properties or affiliations do shields reveal?": """MATCH (s:Entity)-[r]->(e:Entity)
WHERE toLower(s.id) CONTAINS "shield"
RETURN s.id AS source, type(r) AS relation, e.id AS target""",
    "Who are the Black Knights related to?": """MATCH (e1:Entity {id: 'Black Knights'})-[r]->(e2:Entity)
RETURN 'Black Knights' AS source, type(r) AS relation, e2.id AS target"""
}

# Manual interpretations
interpretations = {
    "Who are the Black Knights related to?": """The Black Knights in Dark Souls have a rich web of connections that highlight their tragic lore. They are shown to have faced chaos demons and foes larger than themselves, emphasizing their valor in the face of overwhelming odds. Their armor was charred black, suggesting exposure to intense fire—perhaps as a result of these battles. They also wield iconic weapons like the Heavy Black Knight Sword and the Black Knight Sword, reinforcing their identity as elite warriors. These relationships paint a picture of formidable yet doomed soldiers, forever marked by the flames and wars of the past.""",

    "Which weapons are wielded by Black Knights?": """The graph reveals that Black Knights are directly linked to two powerful weapons: the Black Knight Sword and the Heavy Black Knight Sword. These weapons are deeply associated with their combat style—brutal, deliberate, and overwhelming. Their presence in the hands of the Black Knights reinforces their image as elite adversaries within the Dark Souls universe. The query’s precision highlights only confirmed wielded items, stripping away speculation and grounding the connection in established lore.""",

    "What properties or affiliations do shields reveal?": """The graph unveils that shields in Dark Souls serve not only defensive functions but also reflect lore, symbolism, and mechanical variety. Some shields are engraved with crests, bear emblems, or are decorated with motifs like dragons or flames—highlighting affiliation and craftsmanship. Others are associated with specific factions or characters, such as the Holy Knights of the Sunless Realms or Knightslayer Tsorig. Functionally, they offer effects like fire or magic resistance, parrying capability, and skill enhancements. Interestingly, some shields were even made to shame weak-willed knights, hinting at deeper narrative undertones. Altogether, shields act as narrative artifacts as much as tools for survival.""",

    "What weapons are effective against specific enemy types?": """The dataset identifies a small but insightful set of weapon-enemy effectiveness relationships. The Blood Club is noted as effective against most foes, making it a versatile and broadly useful choice. The Lightning Broadsword stands out as being particularly effective against crowds, suggesting area-of-effect damage or multi-target capabilities. Although limited in number, these connections offer strategic guidance, helping players optimize weapon selection based on the combat scenarios they face.""",

    "What skills are associated with specific weapons?": """This query reveals how specific weapons are tied to unique combat skills in the Dark Souls universe. The Dark Bastard Sword, for example, is linked to 'Stomp,' a skill known for enhancing poise and delivering powerful counterattacks. The Gargoyle Flame Hammer is associated with 'Kindled Flurry,' likely a flame-infused combo attack. These connections emphasize that weapon choice isn't only about stats, but also about the combat style they enable. Even with just two matches, the graph demonstrates how skills are woven into weapon identity."""
}


# Query generator
def generate_query(question):
    if question in manual_queries:
        return manual_queries[question]
    relation_list = ", ".join(f"`{rel}`" for rel in RELATIONSHIP_TYPES)
    system_prompt = f"""
You are a Cypher expert translating natural language into Neo4j Cypher queries.

GRAPH STRUCTURE:
- Nodes are labeled `Entity` and have an `id` property.
- Edges use only the following relationship types: {relation_list}

RULES:
- Use only the exact relationships above. Do not invent or conjugate them.
- Always use variable r if you call type(r) in RETURN.
- Do not use generic terms like "related_to", "associated_with", etc.

MATCHING:
- Use exact match for specific entities (e.g. "Black Knights")
- Use partial match (e.g. CONTAINS) for categories like "shields"
- If unsure, use fallback:
  MATCH (a:Entity {{id: "X"}})-[r]->(b:Entity)
  RETURN a.id AS source, type(r) AS relation, b.id AS target
Only return the Cypher query.
""".strip()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()

# Button actions
col1, col2 = st.columns([1, 1])
run_clicked = col1.button("Run Question")
clear_clicked = col2.button("Clear")

if clear_clicked:
    for key in ["question_input", "selected_question", "cypher_query", "query_result", "has_run_query"]:
        st.session_state[key] = "" if key != "query_result" else None
    st.rerun()

# Execute query
if run_clicked and final_question:
    with st.spinner("Generating Cypher query..."):
        try:
            cypher_query = generate_query(final_question)
            st.session_state["cypher_query"] = cypher_query

            with driver.session() as session:
                result = session.run(cypher_query)
                records = [record.data() for record in result]

            st.session_state["query_result"] = records
            st.session_state["has_run_query"] = True

        except Exception as e:
            st.session_state["query_result"] = []
            st.session_state["has_run_query"] = True
            st.error(f"Failed to execute query: {e}")
elif run_clicked:
    st.warning("Please enter or select a question.")

# Show results
if st.session_state.get("has_run_query", False):
    query_result = st.session_state["query_result"]
    cypher_query = st.session_state["cypher_query"]
    result_df = pd.DataFrame(query_result or [])

    if cypher_query:
        st.code(cypher_query, language="cypher")

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

        st.markdown("### Interpretation of Results")
        if final_question in interpretations:
            st.write(interpretations[final_question])
        else:
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
                    messages=[
                        {"role": "system", "content": "You are an expert at interpreting graph data from Dark Souls."},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                )
                return response.choices[0].message.content.strip()

            with st.spinner("Generating interpretation..."):
                interpretation = generate_interpretation(result_df, final_question)
                st.write(interpretation)
