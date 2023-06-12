import pandas as pd
import numpy as np
from bertopic import BERTopic
from bertopic.plotting import visualize_topics
import matplotlib.pyplot as plt


# DataFrame aus der CSV-Datei erstellen
df = pd.read_csv('Hart.csv')                # Hier immer Datei-Name Anpassen

# Textsätze aufteilen
df_sentences = df['Text'].str.split('.', expand=True)

"""
Zur Kontrolle, ob die Aufteilung der Sätze korrekt erfolgt ist:

df_t = pd.DataFrame(df_sentences)
df_t.to_csv('senten.csv', index=False)
"""

# BERTopic-Modell initialisieren
model = BERTopic(verbose=True)

# convert to list
docs = df_sentences[0].to_list()

# BERTopic-Modell trainieren
topics, probabilities = model.fit_transform(docs)

# Topic-Details zu den Themen abrufen
topic_details = model.get_topic_info()

# DataFrame aus den Themen-Details erstellen
df_topic_details = pd.DataFrame(topic_details)

# DataFrame in eine CSV-Datei speichern
df_topic_details.to_csv('themen_details.csv', index=False)

"""
TODO: Themen visualisieren
visualize_topics(model, top_n_topics=2)
hierarchical_topics = model.hierarchical_topics(docs)
model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
"""

