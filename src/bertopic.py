import pandas as pd
from bertopic import BERTopic
import emoji
import re
from nltk.corpus import stopwords


# DataFrame aus der CSV-Datei erstellen
df = pd.read_csv('scholz.csv')  # Hier immer Datei-Name Anpassen

"""""""""""""""""""""""""""
Data Cleaning
"""""""""""""""""""""""""""
df['Text'] = df['Text'].apply(lambda x: str(x).lower() if not pd.isnull(x) else '')


# Großbuchstaben in Kleinbuchstaben umwandeln
df['Text'] = df['Text'].apply(lambda x: x.lower())


# Funktion zum Entfernen von Emojis
def remove_emojis(text):
    if isinstance(text, str):
        return emoji.demojize(text)
    else:
        return ''


df['Text'] = df['Text'].apply(remove_emojis)


# Muster für Sonderzeichen definieren und aus den Daten löschen
special_chars_pattern = r'[!\?\/\,\:\-\_\(\)\[\]\;\"\'\&\–\„\“\|\.\+\#\%\@\^\*\<\>\`\~\,\...\$\】\【\■\—\…\’\”\№]'

df['Text'] = df['Text'].apply(lambda x: re.sub(special_chars_pattern, '', x))


# Liste mit den zu löschenden Wörtern definieren und aus den Daten löschen
words_to_delete = set(stopwords.words('english'))
words_to_delete.update(set(stopwords.words('german')))
words_to_delete = list(words_to_delete)

df['Text'] = df['Text'].apply(lambda x: ' '.join([word for word in x.split() if word not in words_to_delete]))

# Aktualisierte CSV-Datei speichern
df.to_csv('clear.csv', index=False)



"""""""""""""""""""""""""""
Bert Topic Modeling
"""""""""""""""""""""""""""
# DataFrame aus der CSV-Datei erstellen
df = pd.read_csv('clear.csv')

df['Text'] = df['Text'].astype(str)

# BERTopic-Modell initialisieren
model = BERTopic(verbose=True)

# convert to list
docs = df['Text'].to_list()

# BERTopic-Modell trainieren
topics, probabilities = model.fit_transform(docs)

# Topic-Details zu den Themen abrufen
topic_details = model.get_topic_info()

# DataFrame aus den Themen-Details erstellen
df_topic_details = pd.DataFrame(topic_details)

# DataFrame in eine CSV-Datei speichern
df_topic_details.to_csv('topic.csv', index=False)

# print(model.get_topic(0))



"""""""""""""""""""""""""""
Visualisierung
"""""""""""""""""""""""""""

# Intertopic Distance Map
#v = model.visualize_topics()

# Topic Word Scores
#v = model.visualize_barchart()

# Term score decline
#v = model.visualize_term_rank()

# Hierarchical Clustering mit Topics
hierarchical_topics = model.hierarchical_topics(docs)
v = model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
#v = model.visualize_hierarchy()

# Similarity Matrix
v_1 = model.visualize_heatmap()

v.show()
v_1.show()