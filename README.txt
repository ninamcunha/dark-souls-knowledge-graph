# Dark Souls Knowledge Graph

This project builds an interactive knowledge graph based on the lore of the Dark Souls video game series.

The goal is to extract entities and relationships from item descriptions and lore texts, structure them into a graph database, and enable interactive exploration and question-answering over this graph.

---

## 📄 Project Structure

- notebooks/ — Jupyter Notebook with data processing, graph construction, and documentation of the process.
- data/ — Dataset files:
  - sampled_lore_entries.json — Sampled raw data entries.
  - extracted_triples.json — Subject–predicate–object triples extracted from the text.
  - nodes.csv and edges.csv — CSV files representing the graph structure.
- cypher_batches/ — Cypher script batches to recreate the graph in Memgraph Cloud if needed.
- app/ — Streamlit app for interactive exploration of the graph.
- AI_usage.md — Documentation of how AI tools were integrated into the workflow.
- README.md — Project documentation and instructions.

---

## 📊 Dataset

### Source

The dataset is derived from the Dark Souls Item Descriptions and lore sources, compiled from community resources like:

- https://github.com/leminerva/dark-souls-knowledge-extraction

It contains item names, descriptions, and additional knowledge extracted from the game and fan-maintained wikis.

### Data Example

    {
      "name": "Blood Red and White Shield",
      "description": "Standard round wooden shield. It features a striking red and white design. Wooden shields are light, manageable, and offer relatively high magic absorption.",
      "knowledge": "Skill: Parry — Repel an attack at the right time to follow up with a critical hit. Works while equipped in either hand."
    }

### Token Estimation and Sampling

- The full dataset contained approximately 268,105 tokens.
- For processing efficiency, a representative sample of 100 items was selected.
- This sample maintains diversity in item types (e.g., shields, swords, rings) and complexity of descriptions.

---

## 🔗 Deployment

The graph is deployed in Memgraph Cloud, an online graph database platform.

Memgraph was used for:

- Designing and testing the graph schema.
- Populating the graph with nodes and relationships derived from the lore data.

The graph structure is then exposed via an interactive Streamlit app, offering a user-friendly interface for exploration, visualization, and question-answering — without requiring knowledge of Cypher queries or database access.

---

## 🚀 Explore the Graph — Streamlit App

An interactive Streamlit app is included in this repository to make exploration accessible.

The app allows users to:

- Search for entities (e.g., items, places, characters).
- Visualize relationships between entities.
- Explore the structure of the lore without writing queries.
- Run pre-defined queries and question-answering tasks.

To run the app locally:

    cd app
    streamlit run app.py

Further instructions on setup and usage are provided in the /app/ folder.

---

## 🏗️ Graph Schema Design

### Nodes

- Label: Entity
- Property: id (entity name, for example, "Blood Red and White Shield")

### Relationships

- Various types based on extracted predicates.
- Examples: IS, HAS_SKILL, OFFER, ENGRAVED_WITH, SYMBOLIZES, etc.

The schema was automatically generated from subject–predicate–object triples extracted from item descriptions.

---

## 🤖 AI-Assisted Workflow

Language models were used to assist in:

- Extracting subject–predicate–object triples from free-text item descriptions.
- Accelerating parts of the data preparation and cleaning process.
- Drafting code templates for graph construction, Cypher generation, and documentation.

This project combined automation with manual validation to ensure accuracy and semantic relevance.

A more detailed description of AI integration is provided in AI_usage.md.

---

## 🎯 Deliverables

- A fully functional knowledge graph of Dark Souls lore.
- CSV files (nodes.csv and edges.csv) representing the graph structure.
- Cypher scripts (in /cypher_batches/) for graph reproduction if needed.
- An interactive Streamlit app for exploring the graph.
- Full documentation, including this README and the process notebook.

---

## 👩‍💻 Author

Nina Cunha — Data Scientist | Graph Enthusiast | PhD Economist

- LinkedIn: https://www.linkedin.com/in/nina-menezes-cunha/
- GitHub: https://github.com/ninamcunha

---
