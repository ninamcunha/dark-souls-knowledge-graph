# Dark Souls Knowledge Graph

This project builds an interactive knowledge graph based on the lore of the Dark Souls video game series.

The goal is to extract entities and relationships from item descriptions and lore texts, structure them into a graph database, and enable interactive exploration and question-answering over this graph.

---

## 📄 Project Structure

- `notebooks/` — Jupyter Notebook with data processing, graph construction, and documentation of the process.
- `data/` — Dataset files:
  - `sampled_lore_entries.json` — Sampled raw data entries.
  - `extracted_triples.json` — Subject–predicate–object triples extracted from the text.
  - `nodes.csv` and `edges.csv` — CSV files representing the graph structure.
- `app/` — Streamlit app for interactive exploration of the graph.
- `AI_usage.md` — Documentation of how AI tools were integrated into the workflow.
- `README.md` — Project documentation and instructions.

---

## 📊 Dataset

### Source

The dataset used in this project was adapted from publicly available community resources, primarily:

- Dark Souls Knowledge Extraction by leminerva: https://github.com/leminerva/dark-souls-knowledge-extraction

It contains item names, in-game descriptions, and additional lore knowledge sourced from the game itself and fan-curated wikis.

### Files

- `ds3_clean_texts.json`: A cleaned and pre-processed version of the full dataset, used for downstream analysis and triple extraction.
- `sampled_lore_entries.json`: A smaller sample of entries used to test and iterate over the extraction process.
- `ds3.json`: The original raw dataset (not included in this repository due to size constraints; see source link above to download).

### Data Example

<pre><code>{
  "name": "Blood Red and White Shield",
  "description": "Standard round wooden shield. It features a striking red and white design. Wooden shields are light, manageable, and offer relatively high magic absorption.",
  "knowledge": "Skill: Parry — Repel an attack at the right time to follow up with a critical hit. Works while equipped in either hand."
}
</code></pre>

### Token Estimation and Sampling

- The full dataset contained approximately 268,105 tokens.
- For processing efficiency, a representative sample of 100 items was selected.
- This sample maintains diversity in item types (e.g., shields, swords, rings) and complexity of descriptions.

---

## 🔗 Deployment

The graph is deployed in **Memgraph Cloud**, an online graph database platform.

Memgraph was used for:

- Designing and testing the graph schema.
- Populating the graph with nodes and relationships derived from the lore data.

The graph structure is then exposed via an interactive **Streamlit** app, offering a user-friendly interface for exploration, visualization, and question-answering — without requiring knowledge of Cypher queries or database access.

---

## 🚀 Explore the Graph — Streamlit App

An interactive Streamlit app is included in this repository to make exploration accessible.

🔗 [Launch the app](https://dark-souls.streamlit.app/)

The app allows users to:

- Search for entities (e.g., items, places, characters).
- Visualize relationships between entities.
- Explore the structure of the lore without writing queries.
- Run pre-defined queries and question-answering tasks.

You can also run the app locally using:

<pre><code>streamlit run app.py</code></pre>

Further instructions are provided in the `/app/` folder.

---

## 🏗️ Graph Schema Design

### Nodes

- Label: `Entity`
- Property: `id` (entity name, e.g., `"Blood Red and White Shield"`)

### Relationships

- Various types based on extracted predicates.
- Examples: `IS`, `HAS_SKILL`, `OFFER`, `ENGRAVED_WITH`, `SYMBOLIZES`, etc.

The schema was automatically generated from subject–predicate–object triples extracted from item descriptions.

---

## 🤖 AI-Assisted Workflow

Language models were used to assist in:

- Extracting subject–predicate–object triples from free-text item descriptions.
- Accelerating parts of the data preparation and cleaning process.
- Drafting and proofreading code templates and documentation.

This project combined automation with manual validation to ensure accuracy and semantic relevance.

A more detailed description of AI integration is provided in [`AI_usage.md`](AI_usage.md).

---

## 📦 What’s Included

This repository includes:

- ✅ A functional knowledge graph of Dark Souls lore (deployed via Neo4j and Streamlit).
- ✅ CSV files (`nodes.csv` and `edges.csv`) representing the graph structure.
- ✅ A public Streamlit app for interactive exploration.
- ✅ Full documentation, including the annotated notebook and this README.

---

## 👩‍💻 Author

**Nina Cunha** — Data Scientist | Graph Enthusiast | PhD Economist

- 🔗 [LinkedIn](https://www.linkedin.com/in/nina-menezes-cunha/)
- 💻 [GitHub](https://github.com/ninamcunha)
