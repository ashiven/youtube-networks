from transformers import BertTokenizer, BertModel
import torch
import numpy as np
from sklearn.cluster import KMeans

# BERT-Modell und Tokenizer laden
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

# Dokument einlesen und in Sätze aufteilen
with open('dein_dokument.txt', 'r', encoding='utf-8') as file:
    document = file.read()

sentences = document.split('.')  # Annahme: Sätze werden durch Punkte getrennt

# Titel extrahieren
titles = []
for sentence in sentences:
    sentence = sentence.strip()
    if sentence:
        encoded_input = tokenizer.encode(sentence, return_tensors='pt')
        with torch.no_grad():
            embeddings = model(encoded_input)[0]
        sentence_embedding = torch.mean(embeddings, dim=1).squeeze().numpy()
        titles.append((sentence, sentence_embedding))

# BERT-Embeddings für alle Titel erstellen
title_embeddings = np.array([title[1] for title in titles])

# K-Means-Clustering durchführen
num_clusters = 5  # Anzahl der gewünschten Themen
kmeans = KMeans(n_clusters=num_clusters, random_state=0)
kmeans.fit(title_embeddings)

# Themen-Zuordnung für jeden Titel ermitteln
topic_labels = kmeans.labels_

# Themen extrahieren
topics = {}
for i, title in enumerate(titles):
    topic = topic_labels[i]
    if topic in topics:
        topics[topic].append(title[0])
    else:
        topics[topic] = [title[0]]

# Ausgabe der Themen
for topic, titles in topics.items():
    print(f"Thema {topic+1}:")
    for title in titles:
        print(f"- {title}")
    print()
