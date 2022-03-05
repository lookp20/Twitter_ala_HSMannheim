# Twitter_ala_HSMannheim

Gruppenteilnehmer:

Francisca Hartmann    2060545
Georgi Kostiuchik     2061349
Look Phanthavong      2060544


Die Grundidee für diese Übungsaufgabe ist der Aufbau eines sozialen Netzwerks. 

Damit es einigermaßen realistisch wird, verwenden wir dazu die untenstehenden, aus Twitter extrahierten, Follower-Beziehungen sowie eine Reihe von Promi-Tweets. Der erste Link enthält eine Text-Datei in der in jeder Zeile angegeben ist, welche ID welcher anderen ID folgt ("a follows b"). Im zweiten Link sind Tweets von diversen Promis gesammelt, die wir bspw. zufällig oder reihum auf die User-IDs verteilen wollen, um ein wenig Last für das System zu produzieren. 
aden Sie also bitte alle Daten über Kafka (um Datenverluste durch Rückstaus zu vermeiden) in eine geeignete Datenbank (oder ggf. auch mehrere) und erstellen Sie eine kleine UI (gerne grafisch, Text reicht aber auch), die mindestens folgende Möglichkeiten bietet:

Für eine ID: Anzeige aller Follower sowie Anzeige aller verfolgten IDs (edit: vielleicht nicht unbedingt immer alle, die ersten 20 oder die populärsten 20 sollten reichen)
Auflistung aller Tweets für eine ID
Anzeige der Startseite für eine ID (diese soll die Tweets aller verfolgten IDs beinhalten; ggf. auch nur die neusten 100 o.ä.)
Versenden eines neuen Tweets unter Angabe der Absender-ID
Ideen für optionale Erweiterungen:
Durchsuchen aller Tweets nach einzugegebenen Suchbegriffen
Bauen Sie einen Filter ein, der Tweets mit unerwünschten Worten in einen speziellen Account (z.B. ID 0000) routet und stattdessen nur "censored" in den Tweet der entsprechenden ID einstellt. (ganz wichtig in 2021... 🤔)
Statistik-Abfragen wie wer hat die meisten Follower oder die meisten Tweets
Vorschläge für IDs, die interessant sein könnten (weil die Follower diesen folgen oder die selbst verfolgten User diesen folgen)
Evtl. Einbindung von Flink[tweets.csv]

Daten:
Twitter_Follower: http://snap.stanford.edu/data/twitter_combined.txt.gz
Promi-Tweets: https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/JBXKFD/F4FULO
