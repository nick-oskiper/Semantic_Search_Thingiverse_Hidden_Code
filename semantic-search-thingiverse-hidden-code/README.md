# Semantic_Search_Thingiverse_Hidden_Code

[![PyPI - Version](https://img.shields.io/pypi/v/semantic-search-thingiverse-hidden-code.svg)](https://pypi.org/project/semantic-search-thingiverse-hidden-code)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/semantic-search-thingiverse-hidden-code.svg)](https://pypi.org/project/semantic-search-thingiverse-hidden-code)

This is a summarized version of the Semantic_Search_Thingiverse project, meant to show its functionalities through only some snippets of code rather than the full project, due to Northeastern's research policy.
The full project can be made public for a short period of time upon request.

-----

## Table of Contents

All files will be replicated in the same format of the original project; only the code will be modified such that most of it is hidden.

# Main Folders
bechmarking: contains benchmarking tests on both the AI system and the multi-edge system, depending on which test is conducted. Less relevant tests like testing whether dataset size or target density impacts the system are conducted only on the multi-edge system, whereas the other tests involving relevancy, optimal number of keywords in query, and optimal similarity threshold are implemented in both systems.

main_AI_nonAI_multi_edge: Only relevant file is Jupyter notebook and contains in order - generate_description_main, build_graph_multi_edge, and model_search_by_sim_type.

main_gen_AI: Only relevant file is Jupyter notebook and contains in order - generate_description_main (can be substituted with generate_description_more_expensive), build_graph_with_AI, and model_search.

main_non_AI: Only relevant file is  Jupyter notebook and contains in order - build_graph_existing_noAI and model_search.

### Specific Files
- build_graph_with_AI: builds a knowledge graph based on the AI generated captions from generate_description_main
- build_graph_existing_noAI: builds a knowledge graph for free by using creator summaries on thingiverse (similar to build_graph_with_AI)
- build_graph_multi_edge: Uses the AI generated summaries above, as well as the nonAI summaries from the thingiverse Scraper. It constructs a knowledge graph with the following edges between each node: 
  1. AI and nonAI summaries similarity using tf-idf vectors and cosine similarity calculation (labeled SIMILAR_SUMMARY_AI and SIMILAR_SUMMARY_NONAI)
  2. AI and nonAI summaries similarity using BERT Embedding (labeled SIMILAR_EMBEDDING_AI and SIMILAR_EMBEDDING_NONAI)
  3. Name similarity using tf-idf vectors and cosine similarity calculation (labeled SIMILAR_NAMES_ALL)
  4. AI and nonAI tag similarity using Jaccard similarity (labeled SIMILAR_TAGS_AI and SIMILAR_TAGS_NONAI)
- generate_desciption_main: uses genAI to generate descriptions based on .stl and .png files scraped from Thingiverse. Outputs these to a csv, tht build_graph_with_AI uses to build the knowledge graph.
- generate_description_more_expensive: similar to generate_description_main but uses the creator summaries on thingiverse as well as genAI to describe images. Costs more than generate_description_main but may not be worth this additional cost.
- model_search.py: after building a knowledge graph in Neo4j through running generate_description_main as well as build_graph_with_AI (or one can also run build_graph_without_AI), this allows the user to search through models and find the one they are looking for. Also includes filtering and advanced searching functions.
- model_search_by_sim_type.py: after building a knowledge graph in Neo4j through running generate_description_main as well as build_graph_multi_edge, this allows the user to search through models and pick which similarity edge they would like to traverse from the seven in the knowlege graph. Also includes filtering and advanced searching functions.
- thing_details_only_id_summary (2) (1): Approximately 1000 Thingiverse models ID and summary information from the Thingiverse Scraper.
- benchmarking: contains benchmarking files that perform the task in their name. Relevancy and keywords_in_query are very important in testing this system.


- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install semantic-search-thingiverse-hidden-code
```

## License

`semantic-search-thingiverse-hidden-code` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
