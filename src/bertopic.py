import pandas as pd
from bertopic import BERTopic
import emoji
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import re


# DataFrame aus der CSV-Datei erstellen
df = pd.read_csv('It_Takes_Two.csv')                # Hier immer Datei-Name Anpassen


"""""""""""""""""""""""""""
Data Cleaning
"""""""""""""""""""""""""""

# Funktion zum Entfernen von Emojis
def remove_emojis(text):
    return emoji.demojize(text) #😎

df['Text'] = df['Text'].apply(remove_emojis)


# Muster für Sonderzeichen definieren und aus den Daten löschen
special_chars_pattern = r'[!\?\/\,\:\-\_\(\)\[\]\;\"\'\&\–\„\“\|\.\+\#\%\@\^\*\<\>\`\~\,]'

df['Text'] = df['Text'].apply(lambda x: re.sub(special_chars_pattern, '', x))


# Liste mit den zu löschenden Wörtern definieren und aus den Daten löschen
stopwords = set(stopwords.words('english'))
stopwords.update(set(stopwords.words('german')))
words_to_delete = list(stopwords)

df['Text'] = df['Text'].apply(lambda x: ' '.join([word for word in x.split() if word not in words_to_delete]))


# Aktualisierte CSV-Datei speichern
df.to_csv('clear.csv', index=False)



"""""""""""""""""""""""""""
Bert Topic Modeling
"""""""""""""""""""""""""""
# DataFrame aus der CSV-Datei erstellen
df = pd.read_csv('clear.csv')

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
v = model.visualize_topics()

# Topic Word Scores
# v = model.visualize_barchart()

# Hierarchical Clustering
# hierarchical_topics = model.hierarchical_topics(docs)
# v = model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)

v.show()