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

The graph is deployed in **Neo4j AuraDB**, a fully managed cloud graph database service.

Neo4j was used for:

- **Storing** the structured knowledge graph extracted from the Dark Souls lore.
- **Managing** labeled nodes and typed relationships using the Cypher query language.
- **Powering** real-time graph querying integrated into the Streamlit app.

The graph was populated by:

- Establishing a secure connection to the Neo4j AuraDB instance using the official Neo4j Python driver.
- Uploading data from `nodes.csv` and `edges.csv`:
  - Nodes are labeled `Entity` and contain an `id` property.
  - Relationships are created using the `source`, `target`, and `type` columns from the edge list.

This setup enables seamless interaction between the Streamlit frontend and the graph backend, allowing users to explore, visualize, and query the knowledge graph without needing direct access to the database.

---

## 🚀 Explore the Graph — Streamlit App

An interactive Streamlit app is included in this repository to make exploration accessible.

🔗 [Launch the app](https://dark-souls.streamlit.app/)

The app allows users to:

- 📄 Browse the full dataset of graph relationships in tabular form.
- 🌐 Visualize the complete knowledge graph with a size control slider.
- ❓ Ask natural-language questions about the lore (e.g., “Which weapons are wielded by Black Knights?”).
- ⚡ View results as both a table and a dynamic subgraph visualization.
- 🧠 Read automatic interpretations of query results written by a language model.

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

- 🔎 Extracting subject–predicate–object triples from free-text item descriptions.
- 🧹 Accelerating parts of the data preparation and cleaning process.
- 🧠 Interpreting Cypher query results into short human-readable summaries.
- 🧪 Translating natural-language questions into Cypher queries in real time.
- 📚 Understanding and exploring the lore and structure of the Dark Souls universe, since I had no prior familiarity with the game world.

This project combined automation with manual validation to ensure accuracy and semantic relevance.

A more detailed description of AI integration is provided in [`AI_usage.md`](AI_usage.md).

---

## ⚠️ Challenges and Future Improvements

One of the most impactful features of this project is the natural-language question-answering (QA) interface, powered by GPT-4. However, this also introduced challenges related to **model reliability and cost**.

### Relationship Type Mismatches

The underlying graph uses specific relationship types (e.g., `wield`, `belongs_to`, `engraved_with`). The LLM sometimes generated invalid or inferred types like `wielded_by` or `related_to`, leading to query failures or empty results.

To mitigate this, a full list of valid relationship types was extracted and injected into the system prompt used by GPT-4. While this significantly reduced errors, some queries still failed due to strict matching filters, typos, or variable naming issues (e.g., using `type(r)` without defining `r`).

### Fixing Core Questions with Manual Queries

To address this, five core questions—those most commonly asked during testing—were handled manually:

- The Cypher queries and interpretations for these questions were hardcoded into the app.
- When a user selects one of them (or types it verbatim), **no LLM call is made**, eliminating latency and API costs.
- Interpretations for these queries are also fixed, based on LLM style but validated manually to match the exact query results.

This hybrid approach improved reliability and reduced unnecessary LLM calls.

### Future Enhancements

To improve open-ended question handling, future iterations of this project could explore:

- 🧠 **Few-shot fine-tuning** of a smaller LLM using valid question-query examples.
- 🧪 **Semantic query repair**, using fuzzy logic to replace invalid relationships with valid alternatives.
- 🔁 **Fallback query relaxations**, such as switching from `id =` to `CONTAINS` matching.
- 🗣️ **User feedback on query failure**, to help refine input phrasing.

This process revealed the practical limits of real-time LLM integration and the benefits of mixing automation with **rule-based fallback strategies**.

## 📦 What’s Included

This repository includes:

- ✅ A functional knowledge graph of Dark Souls lore (deployed via Neo4j and Streamlit).
- ✅ CSV files (`nodes.csv` and `edges.csv`) representing the graph structure.
- ✅ A public Streamlit app for interactive exploration and QA.
- ✅ Full documentation, including the annotated notebook and this README.

---

## 👩‍💻 Author

**Nina Cunha** — Data Scientist | Graph Enthusiast | PhD Economist

- 🔗 [LinkedIn](https://www.linkedin.com/in/nina-menezes-cunha/)
- 💻 [GitHub](https://github.com/ninamcunha)
