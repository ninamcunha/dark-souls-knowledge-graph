# AI Usage in the Dark Souls Knowledge Graph Project

This project uses AI to transform unstructured narrative content from *Dark Souls III* into a structured, queryable knowledge graph. The primary AI component was the application of large language models (LLMs) to extract relationships between entities in the game world.

## 🧠 Use of LLMs for Knowledge Extraction

The core of the project involved using **GPT-4o** via the OpenAI API to extract subject–predicate–object triples from item descriptions, spell texts, and NPC dialogue.

Each input entry included the item's name, description, and optional in-game knowledge text. A structured prompt was passed to GPT-4o instructing it to identify 1 to 3 meaningful triples that express a relationship between entities. The output was then parsed and lightly cleaned to ensure consistency and suitability for graph modeling.

This step:

- Automates what would otherwise be manual annotation of relationships.
- Enables accurate identification of implicit connections (e.g., linking characters to locations or abilities).
- Scales to large sets of unstructured game data while maintaining high semantic quality.

## 💬 Natural-Language Question Answering with AI

To make the graph easier to explore and understand, I implemented a **natural-language QA interface** using GPT-4o within the Streamlit app. AI is used in two critical stages:

1. **Query generation:** When the user types a question in plain English, GPT-4o generates a valid Cypher query based on the structure and relationships of the Neo4j graph.
2. **Interpretation of results:** After the query is executed, the resulting relationships are summarized by GPT-4o into a short, readable explanation (3–5 sentences).

This dual use of AI allows even non-technical users to interact naturally with the graph and understand its structure, bridging the gap between lore complexity and usability.

## ⚙️ Additional AI-Assisted Work

In addition to core logic, AI tools were used throughout development to improve quality and efficiency:

- **Code refinement:** Refactoring and adapting Python code (e.g., modern Streamlit patterns).
- **Text proofing:** All text in the notebook and documentation was reviewed and improved using language models.
- **Debugging:** LLMs helped resolve deployment and dependency issues in Python and Streamlit.
- **Domain support:** Since I wasn’t previously familiar with *Dark Souls*, I used AI tools to:
  - Understand core lore concepts, characters, and terminology.
  - Validate extracted relationships and suggest improvements.
  - Generate realistic and diverse example questions for the QA interface.

These uses complemented human-led design and ensured contextual accuracy.

## 🎯 Summary

- AI is used for both **graph construction** (triple extraction) and **graph interaction** (question generation + result interpretation).
- Supporting AI use cases include text editing, debugging, and knowledge discovery.
- This human-in-the-loop approach enabled semantic extraction at scale while maintaining full control over quality and narrative integrity.
