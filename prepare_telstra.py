import pandas as pd
import os

# Liste des fichiers nécessaires pour la base de connaissances
required_files = ['train.csv', 'event_type.csv', 'severity_type.csv', 'log_feature.csv', 'resource_type.csv']

print("🔍 Vérification des fichiers dans le dossier...")
missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    print(f"❌ ERREUR : Il manque ces fichiers : {missing_files}")
    print("Assurez-vous d'avoir dézippé tous les fichiers au même endroit que ce script.")
    exit()

print("✅ Tous les fichiers critiques sont présents. Chargement...")

# 1. Chargement des données brutes
train = pd.read_csv('train.csv')        # Les incidents avec le résultat (Panne ou pas)
event = pd.read_csv('event_type.csv')   # Ce qu'il s'est passé
severity = pd.read_csv('severity_type.csv') # L'alerte
log = pd.read_csv('log_feature.csv')    # Les logs techniques
resource = pd.read_csv('resource_type.csv') # Le matériel

print(f"📊 Nombre d'incidents historiques trouvés : {len(train)}")

# 2. Nettoyage et Regroupement (Car un incident peut avoir plusieurs logs)
print("🔗 Fusion des données techniques...")

# On compresse les lignes multiples en une seule ligne par ID
event_grouped = event.groupby('id')['event_type'].apply(lambda x: ', '.join(x)).reset_index()
log_grouped = log.groupby('id')['log_feature'].apply(lambda x: ', '.join(x)).reset_index()
resource_grouped = resource.groupby('id')['resource_type'].apply(lambda x: ', '.join(x)).reset_index()

# 3. Création du MASTER DATASET (La fusion)
# On part de 'train' et on colle les infos des autres fichiers
df = train.merge(severity, on='id', how='left')
df = df.merge(event_grouped, on='id', how='left')
df = df.merge(log_grouped, on='id', how='left')
df = df.merge(resource_grouped, on='id', how='left')

# 4. Traduction pour l'IA (Text Enrichment)
# On crée une phrase en langage naturel que l'IA pourra lire facilement
print("📝 Génération du texte pour l'IA...")

def create_narrative(row):
    # Traduction du code de sévérité en mots humains
    status = "Inconnu"
    if row['fault_severity'] == 0:
        status = "AUCUNE PANNE (Fonctionnement normal)"
    elif row['fault_severity'] == 1:
        status = "ALERTE MINEURE (Quelques erreurs)"
    elif row['fault_severity'] == 2:
        status = "PANNE CRITIQUE (Coupure de service)"

    return (f"Incident {row['id']} à {row['location']}. "
            f"Statut Final: {status}. "
            f"Détails Techniques: Logs [{row['log_feature']}], "
            f"Événements [{row['event_type']}], "
            f"Ressource [{row['resource_type']}].")

df['text_for_ai'] = df.apply(create_narrative, axis=1)

# 5. Sauvegarde
output_file = 'network.csv'
df.to_csv(output_file, index=False)

print("-" * 30)
print(f"✅ SUCCÈS TOTAL ! Fichier '{output_file}' généré.")
print(f"👉 Contient {len(df)} cas historiques prêts à être ingérés.")
print("👉 Vous pouvez maintenant lancer : python ingest.py")

