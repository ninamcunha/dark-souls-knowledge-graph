# AI Usage in the Dark Souls Knowledge Graph Project

This project uses AI to transform unstructured narrative content from *Dark Souls III* into a structured, queryable knowledge graph. The primary AI component was the application of large language models (LLMs) to extract relationships between entities in the game world.

## 🧠 Use of LLMs for Knowledge Extraction

The core of the project involved using **GPT-4o** via the OpenAI API to extract subject–predicate–object triples from item descriptions, spell texts, and NPC dialogue.

Each input entry included the item's name, description, and optional in-game knowledge text. A structured prompt was passed to GPT-4o instructing it to identify 1 to 3 meaningful triples that express a relationship between entities. The output was then parsed and lightly cleaned to ensure consistency and suitability for graph modeling.

This step:

- Automates what would otherwise be manual annotation of relationships.
- Enables accurate identification of implicit connections (e.g., linking characters to locations or abilities).
- Scales to large sets of unstructured game data while maintaining high semantic quality.

## ⚙️ Additional AI-Assisted Work

While GPT-4o was only used programmatically for triple extraction, general-purpose AI tools were used throughout the development process to improve quality and efficiency:

- **Code refinement**: AI assistants were used to refactor Python code (e.g., adapting to Streamlit's latest caching API).
- **Text proofing**: All explanatory and descriptive texts—such as those in the notebook and README—were initially written manually to reflect the project's goals and narrative tone. Language models were then used to **proofread and refine** these texts, ensuring clarity, correctness, and consistency.
- **Debugging**: AI tools were occasionally consulted to resolve dependency issues and Streamlit deployment problems.

While these uses were important for productivity, they were complementary to the core logic and reasoning, which were driven by human design.

## 🎯 Summary

- The only model used in the graph construction pipeline was **GPT-4o**, via API, to extract relational triples.
- All other uses of AI (writing, formatting, debugging) supported—but did not replace—project decision-making.
- This approach allowed me to scale up semantic extraction while retaining control over graph quality and structure.
