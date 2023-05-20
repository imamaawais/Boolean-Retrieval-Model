# Boolean Retrieval Model

## Introduction
The Boolean Retrieval Model is a simple information retrieval model that allows users to search for documents using Boolean expressions. This model is particularly useful when dealing with large collections of text documents and enables precise searches based on the presence or absence of specific terms.

## Dependencies
- Python 3.7 or higher.
- nltk (Natural Language Toolkit) library.

## Usage
Supported query expressions:
   - Single word query: Enter a single word. The script will return the list of documents where the term occurred.
   - Biword query: Enter two words separated by a space. The script will return the list of documents where the words occur as a biword (with proximity k=1).
   - Proximity query: Enter two words separated by a space, followed by "/ k" (where k is the desired proximity). The script will return the list of documents where the words occur within the specified proximity.
   - Simple boolean query: Enter boolean expressions using the operators AND, OR, NOT, and parentheses for grouping terms. For example: "not term1", "term1 and term2", "term1 or term2".
   - Complex boolean query: Enter complex boolean expressions combining multiple terms and operators. For example: "not (term1 and term2)", "(term1 and term2) or term3".
