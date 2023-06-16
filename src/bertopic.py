import pandas as pd
from bertopic import BERTopic
import emoji
import re


# DataFrame aus der CSV-Datei erstellen
df = pd.read_csv('It_Takes_Two.csv')                # Hier immer Datei-Name Anpassen


"""""""""""""""""""""""""""
Data Cleaning
"""""""""""""""""""""""""""

# Funktion zum Entfernen von Emojis
def remove_emojis(text):
    return emoji.demojize(text)

df['Text'] = df['Text'].apply(remove_emojis)


# Muster für Sonderzeichen definieren und aus den Daten löschen
special_chars_pattern = r'[!\?\/\,\:\-\_\(\)\[\]\;\"\'\&\–\„\“\|\.\+\#\%\@\^\*\<\>\`\~\,]'

df['Text'] = df['Text'].apply(lambda x: re.sub(special_chars_pattern, '', x))


# Liste mit den zu löschenden Wörtern definieren und aus den Daten löschen
words_to_delete = ['der', 'Der', 'die', 'Die', 'das', 'Das', 'den', 'Den', 'dem', 'Dem',
                   'ein', 'Ein', 'einen', 'Einen', 'einer', 'Einer', 'eines','eine', 'kein', 'keinen', 'keiner',
                   'in', 'im', 'zu', 'Zu', 'ZU', 'zum', 'zur', 'und', 'auf', 'mit', 'über', 'von', 'dass',
                   'für', 'aus', 'mit', 'von', 'vom', 'denn', 'bei', 'nach', 'statt',
                   'ist', 'Ist', 'mal', 'k', 'o'  'hier', 'fr', 'co', 'Co', 'klartext', 'HD', 'I', 'jetzt', 'Jetzt', 'aust'
                   'Sie', 'er', 'Er', 'sie', 'es', 'Es', 'wir', 'Wir', 'ihr', 'ihn', 'ihr', 'ich', 'unsere', 'unseren', 'unserem', 'unserer',
                   'sein', 'seinen', 'seinem', 'seiner', 'ihrer', 'ihren', 'ihrem', 'ihres', 'eure', 'euren', 'eurem', 'eurer',
                   '1990', '1991', '1992', '1993', '1994', '1995',
                   '1996', '1997', '1998', '1999' '2000', '2001', '2002', '2003', '2004',
                   '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013',
                   '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022',
                   '2023', '1983', '1989', '53', 'Januar', 'Februar', 'Mart', 'April', 'Mai',
                   'Juni', 'Juli', 'August', 'September', 'Oktober', 'Novemder', 'Dezember',
                   'it', 'you', 'this', 'did', 'what', 'about', 'all', 'vs']

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