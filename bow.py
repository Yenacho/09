# -*- coding: utf-8 -*-
"""BoW

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ua8L8C686mKZ7k4Pq8Gm9-wtkQMJc_qB

# Introduction to Bag of Words

Bag-of-Words is a family of text representations, where text vectors are built by observing and counting the words that appear in a text.

We study 2 types of BoW vectors:
* **Raw Count**: actually count the number of occurences of each word in a text
* **TF-IDF**: adjust the raw count to favor words that appear a lot in a few documents, as opposed to those who appear a lot in all documents

## Definitions

**Document** and **Corpus**: 
* **Document** is the smallest unit of text of your use case
* **Corpus** is your collection of documents
* **Use case**: think of the typical question you are looking the answer to
* **Query**: the text you will use to search in your corpus

A few examples of use cases:
* Use case 1: "*which academic papers are about black holes?*"
   * Corpus: academic papers uploaded to ArXiv
   * Document: 1 paper
   * Query: "black hole"
* Use case 2: "*Where does Victor Hugo mention Notre-Dame?*"
   * Corpus: entire works from Victor Hugo
   * Document: 1 paragraph
   * Query: "notre dame"
* Use case 3: "*What can I cook with pasta and garlic?*"
   * Corpus: all recipes in multiple cook books
   * Document: 1 recipe
   * Query: "pasta garlic"

**Tokenizer**

A tokenizer is a program that takes in a text and splits it into smaller units. A book can be split into chapters, into paragraphs, into sentences, into words. Those are all examples of tokenization process.

Once a text is tokenized into sentences, you can tokenize sentences into words.


**Sentence**

In natural language, a text is made of multiple sentences, separated by punctuation marks such as `.`. It is nonetheless a challenge to split a text into sentences as some `.` indicate abbreviations, for example.

**Word**:

Any text is made of words. Sometimes they are nicely separated by spaces or punctuation marks. As with sentences, some words include punctuation marks, like `U.S.A.`, or `to court-martial`.


**Vocabulary**:

The list of unique words used in the corpus.
"""

import numpy as np
import math
import pandas as pd

"""## Download Corpus

We will use some short extracts from a Sherlock Holmes story "Scandal in Bohemia", by Sir Arthur Conan Doyle.

We will start with the first paragraph of the book.

* **Corpus**: All sentences in "Scandal in Bohemia"
* **Document**: 1 sentence of the book
"""

import requests

r = requests.get('https://sherlock-holm.es/stories/plain-text/scan.txt')

assert r.status_code == 200

with open('scandal_in_bohemia.txt', 'w') as out:
    out.write(r.content.decode('utf-8'))
lines = [txt for txt in open('scandal_in_bohemia.txt') if len(txt.strip()) > 0]

print(lines[:20])

# First Paragraph
par = ' '.join([x.strip() for x in lines[7:25]])

import textwrap
print(textwrap.fill(par, width=80))

"""## NLTK

NLTK is a Python library for text analytics.

See [Link](https://www.nltk.org).
"""

import nltk
nltk.download('punkt')

"""The **sentence tokenizer** takes care to split a text into sentences."""

from nltk.tokenize import sent_tokenize
nltk_sentences = sent_tokenize(par)
nltk_sentences

"""The **word tokenizer** takes care to split a text into words."""

from nltk.tokenize import word_tokenize
nltk_tokens = word_tokenize(nltk_sentences[0])
nltk_tokens

"""## SpaCy

SpaCy is another Python libary for text analytics.

See [Link](https://spacy.io)
"""

import spacy
nlp = spacy.load('en_core_web_sm')

doc = nlp(par)

"""It has also a **sentence tokenizer**."""

spacy_sentences = list(doc.sents)
spacy_sentences

"""And a **word tokenizer**"""

spacy_tokens = [x for x in spacy_sentences[0]]
spacy_tokens

"""**Warning**: NLTK / SpaCy might produce different results: break sentences at different places, break words at different places, etc..."""

s = nltk_sentences[0]

"""## SKLEARN Generalities

Classes likes `CountVectorizer` or `TfidfVectorizer` works in the following way:
* Instantiate an object with specific parameters (`v = CountVectorizer(...)`)
* Fit this object to your corpus = learn the vocabulary (method `v.fit(...)`)
* Transform any piece of text you have into a vector (method `v.transform()`)
"""

def show_vocabulary(vectorizer):
    words = vectorizer.get_feature_names()

    print(f'Vocabulary size: {len(words)} words')

    # we can print ~10 words per line
    for l in np.array_split(words, math.ceil(len(words) / 10)):
        print(''.join([f'{x:<15}' for x in l]))

from termcolor import colored

def show_bow(vectorizer, bow):
    words = vectorizer.get_feature_names()

    # we can print ~8 words + coefs per line
    for l in np.array_split(list(zip(words, bow)), math.ceil(len(words) / 8)):
        print(' | '.join([colored(f'{w:<15}:{n:>2}', 'grey') if int(n) == 0 else colored(f'{w:<15}:{n:>2}', on_color='on_yellow', attrs=['bold']) for w, n in l ]))

def show_bow_float(vectorizer, bow):
    words = vectorizer.get_feature_names()

    # we can print ~6 words + coefs per line
    for l in np.array_split(list(zip(words, bow)), math.ceil(len(words) / 6)):
        print(' | '.join([colored(f'{w:<15}:{float(n):>0.2f}', 'grey') if float(n) == 0 else colored(f'{w:<15}:{float(n):>0.2f}', on_color='on_yellow', attrs=['bold']) for w, n in l ]))

"""# Raw Count

* We take a text, any text, and represent it as a vector
* Each text is represented by a vector with **N** dimensions
* Each dimension is representative of **1 word** of the vocabulary
* The coefficient in dimension **k** is the number of times the word at index **k** in the vocabulary is seen in the represented text
"""

from sklearn.feature_extraction.text import CountVectorizer

"""## First Example - Reduced Vocabulary

We illustrate with a small corpus so we have a reduced vocabulary.

* **Corpus**: The first paragraph of the book
* **Document**: 1 sentence
"""

count_small = CountVectorizer(lowercase=False)
count_small.fit(nltk_sentences)
show_vocabulary(count_small)

"""The option `lowercase` sets up one behavior of the raw count: do we consider `And` to be different than `and`?

* `lowercase=False` gives 134 unique words in the vocabulary
* `lowercase=True` gives 127 unique words
"""

count_small = CountVectorizer(lowercase=True)
count_small.fit(nltk_sentences)
show_vocabulary(count_small)

s = nltk_sentences[0]

print(f'Text: "{s}"')
bow = count_small.transform([s])
print(f'BoW Shape: {bow.shape}')
bow = bow.toarray()   # From sparse matrix to dense matrix (Careful with MEMORY)
print(f'BoW Vector: {bow}')

show_bow(count_small, bow[0])

"""## Second Example - Larger Corpus

* **Corpus**: entire book
* **Document**: 1 sentence
"""

book = ' '.join([x.strip() for x in lines])
sentences = sent_tokenize(book)

count = CountVectorizer(lowercase=True)
count.fit(sentences)
show_vocabulary(count)

s = sentences[10]

print(f'Text: "{s}"')
bow = count.transform([s])
print(f'BoW Shape: {bow.shape}')
bow = bow.toarray()   # From sparse matrix to dense matrix (Careful with MEMORY)
print(f'BoW Vector: {bow}')

show_bow(count, bow[0])

"""## Real-Life Corpus

Books are very clean texts. Real-Life corpuses including user-generated material will be on the opposite of the spectrum, and will include typos, strange usernames, artefacts of all kinds...

The "20 newsgroups" dataset is a classical NLP dataset. Newsgroups are the ancestors of reddit, people could post messages and reply in a thread.

* **Corpus**: newsgroup messages
* **Document**: full text of 1 message
"""

from sklearn.datasets import fetch_20newsgroups

newsgroups = fetch_20newsgroups()

print(f'Number of documents: {len(newsgroups.data)}')
print(f'Sample document:\n{newsgroups.data[0]}')

"""* Vocabulary is much larger (130107 unique words)
* Lots of "garbage" in vocabulary ("mbocjlo3", "mc2i", "mc68882rc25")
"""

count = CountVectorizer()
count.fit(newsgroups.data)
show_vocabulary(count)

print(f'Size of vocabulary: {len(count.get_feature_names())}')

"""# TF-IDF

The basic for TF-IDF is that cosine similarity with raw count coefficients puts too much emphasis on the number of occurences of a word within a document.

Repeating a word will artifically increase the cosine similarity with any text containing this word.

Consider which word would be important:
1. One that is repeated a lot and equally present in each document
1. One that appears a lot only in a few document

TF-IDF computes coefficients:
* Low values for common words (ie present in the document, but quite common over the corpus)
* High values for uncommon words (ie present in the document, but not common over the corpus)

We consider one specific document, and one specific word.

* **TF = Term Frequency**: the number of times the word appears in the document
* **DF = Document Frequency**: the number of document in the corpus, in which the word appears
* **IDF = Inverse Document Frequency**: the inverse of the Document Frequency.

Logarithms are introduced, to reflect that 100 times a word does not deliver 100 times the information.

Given a word **w**, a document **d** in a corpus of **D** documents:

$\textrm{TF-IDF(w, d) = TF(w, d) * IDF(w)}$

$
\begin{align}
\textrm{IDF(w) = log} \left( \frac{1 + \textrm{D}}{1 + \textrm{DF(w)}} \right) + 1
\end{align}
$

This is the default SKLEARN formula (see [Link](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfTransformer.html#sklearn.feature_extraction.text.TfidfTransformer))

Bag of Words vectors with TF-IDF coefficients (often called TF-IDF vectors):
* **N** dimensions, where **N** is the size of the vocabulary
* Coefficient at dimension **k** is the coefficient for the word at index **k** in the vocabulary
* Coefficients are TF-IDF coefficients, instead of raw count
"""

from sklearn.feature_extraction.text import TfidfVectorizer

"""### Example

We continue with the Sherlock Holmes book "Scandal in Bohemia"

* **Corpus**: full text of the book
* **Document**: 1 sentence
"""

tfidf = TfidfVectorizer()
tfidf.fit(sentences)
show_vocabulary(tfidf)

s = sentences[10]

print(f'Text: "{s}"')
bow = tfidf.transform([s])
print(f'BoW Shape: {bow.shape}')
bow = bow.toarray()   # From sparse matrix to dense matrix (Careful with MEMORY)
print(f'BoW Vector: {bow}')

show_bow_float(tfidf, bow[0])

"""Display the IDF of some words. 

* High IDF = word that appears in few documents
* Low IDF = word that appears in most of documents
"""

words = tfidf.get_feature_names()
word = input('Word: ').lower()

if word in words:
    k = words.index(word)
    print(f'IDF({words[k]}) = {tfidf.idf_[k]}')
else:
    print('Not in vocabulary')



"""#### More than one TF-IDF

There is a family of TF-IDF formulas. 

Another example is the **sublinear TF**, which is then:

$
\begin{align}
\textrm{TF(w, d) = 1 + log} \left( raw count \right)
\end{align}
$
"""

tfidf_sublinear = TfidfVectorizer(sublinear_tf=True)
tfidf_sublinear.fit(sentences)

s = sentences[10]

print(f'Text: "{s}"')
bow_sl = tfidf_sublinear.transform([s])
print(f'BoW Shape: {bow_sl.shape}')
bow_sl = bow_sl.toarray()   # From sparse matrix to dense matrix (Careful with MEMORY)
print(f'BoW Vector: {bow_sl}')

show_bow_float(tfidf_sublinear, bow_sl[0])

word = 'yet'

index = words.index(word)

bow = tfidf.transform([s]).toarray()

print(f'Word: "{word}"')
print(f'TF-IDF with Natural TF   = {bow[0][index]:0.4f}')
print(f'TF-IDF with Sublinear TF = {bow_sl[0][index]:0.4f}')

"""Repeating a word in a text will modify the TF-IDF coefficient for this word in the text representation."""

word = 'yet'
s = sentences[10]
s = s + ' '.join(100 * [word])

bow = tfidf.transform([s]).toarray()
bow_sl = tfidf_sublinear.transform([s]).toarray()

index = words.index(word)
print(f'Word: "{word}"')
print(f'TF-IDF with Natural TF   = {bow[0][index]:0.4f}')
print(f'TF-IDF with Sublinear TF = {bow_sl[0][index]:0.4f}')

"""# Search Engine

With these vectors, we can build a search engine.

* **Query**: Let the user enter a text query
* Search through the corpus the documents that are **similar** to the query
* **Similarity**: we use the **cosine similary** of the BoW vectors of two texts to evaluate their similarity.
"""

corpus_bow = count.transform(newsgroups.data)

query = input("Type your query: ")
query_bow = count.transform([query])

from sklearn.metrics.pairwise import cosine_similarity

similarity_matrix = cosine_similarity(corpus_bow, query_bow)
print(f'Similarity Matrix Shape: {similarity_matrix.shape}')

"""The similarity matrix has **D** rows (the number of documents in the corpus) and 1 column.

Coefficient at row **k** is the cosine similarity between the document at index **k** in the corpus and the query.

"""

similarities = pd.Series(similarity_matrix[:, 0])
similarities.head(10)

top_10 = similarities.sort_values(ascending=False)[:10]
top_10

print('Best document:')
print(newsgroups.data[top_10.index[0]])

