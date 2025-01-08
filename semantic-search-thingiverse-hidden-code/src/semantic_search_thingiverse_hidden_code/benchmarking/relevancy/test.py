import os
import re
import string
import sys
import pandas as pd
import numpy as np
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util
from py2neo import Graph
from sklearn.metrics import ndcg_score
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
STOP_WORDS = set(stopwords.words('english'))
nlp = spacy.load('en_core_web_sm')

UNWANTED_WORDS = {
    "3d", "model", "models", "appears", "representation", "detailed", "complete", "assembled",
    "intricate", "design", "depicts", "depiction", "represents", "features", "includes",
    "showcases", "demonstrates", "illustrates", "portrays", "embodies", "integrates", "comprises",
    "constitutes", "consists", "containing", "contains", "constructed", "crafted", "fabricated",
    "rendered", "configured", "functional", "stylized", "displayed", "presented", "unveils",
    "introduces", "housing", "hosts", "mirroring", "resemble", "resembling", "embodied",
    "articulated", "mimicking", "integrated", "highlighting", "offering", "showing",
    "presenting", "presents", "indicating", "indicate", "promising", "solid", "structure",
    "similarity", "practical", "unique", "smooth", "realistic", "ergonomic", "polished",
    "dynamic", "static", "compact", "robust", "sleek", "precision", "accuracy", "flexibility",
    "summary", "instructions", "printing instructions", "print settings", "custom section",
    "assembly manual", "post-printing", "how i designed this", "my things", "notes", "caution",
    "print", "printed", "printit", "printing", "printing instructions for", "printer brand:",
    "printer:", "rafts:", "supports:", "resolution:", "infill:", "filament brand:",
    "filament material:", "filament color:", "print time:", "parts:", "files:", "dimensions:",
    "post images", "caution:", "if connected via wi-fi:", "if connected via usb:", "step files",
    "affiliate links", "do not use", "click", "click the", "click on", "download", "download the",
    "download the file", "download the thing", "makerbot desktop will open", "action button",
    "start print", "exit the print dialog", "action button will blink", "action button to confirm",
    "action button will glow", "indicating it is heating", "when the smart extruder is fully heated",
    "wait for the smart extruder to cool", "remove the build plate", "remove the raft",
    "uploaded a new version", "added a version", "updated parts", "updated stl", "split into",
    "join", "make", "hitting that", "hit the like", "check out", "follow my", "clicking i made one",
    "assemble", "assembly", "assemble with", "glue it", "peel off", "print with", "print it",
    "print your", "print your model", "supports only", "no supports required", "raft", "rafts",
    "raft acts", "raft will", "raft as", "raft is", "print profile", "include", "included",
    "support structures", "support is", "supportless", "link", "links", "youtube", "video",
    "website", "twitter", "facebook", "instagram", "vimeo", "element.io", "makerware", "thing",
    "thingiverse", "make by", "tip designer", "quick without any support", "snap fit retention",
    "no screws needed", "print in vase mode", "help to", "some words", "instructions:",
    "download the", "assemble the", "click on the", "click to", "slicer", "layer height", "infill",
    "print without", "print without support", "printing without", "use supports", "printed with",
    "printing the", "printed the", "printing with", "printed without", "print with", "printing",
    "print times", "print quality", "print speed", "www", "print instructions", "print options",
    "print details", "license", "cc by", "cc by-nc", "cc by-sa", "cc by-nc-sa", "cc by-nc-nd",
    "creative commons", "attribution", "non-commercial", "share alike", "no derivatives", "by",
    "is licensed under", "licensed under", "licensed under the creative commons",
    "http://", "https://", "youtube.com", "bit.ly", "youtu.be", "thingiverse.com",
    "facebook.com", "instagram.com", "twitter.com", "vimeo.com", "make by", "hit the like",
    "follow my", "clicking i made one", "go enjoy", "take your", "visit here", "download it",
    "print it as", "print as", "print your model", "print it with", "print it without",
    "print your", "print the", "print settings", "settings", "setting", "print button",
    "print dialog", "print files", "print files once", "print files to", "click start print",
    "click cancel print", "start print", "cancel print", "gear", "gears", "support structures",
    "extruder", "build plate", "snap them", "slicing tools", "layer height", "print bed",
    "extruder", "slicer settings", "use tool", "using tool", "gear sets", "pressure angle",
    "bolt", "nuts", "screws", "screwdriver bits", "electrical connections",
    "electronic components", "attachment", "attachments", "hardware", "assembled",
    "assembling", "parts", "part", "component", "components", "clipping", "clips", "holding",
    "held", "mounted", "mounting", "mounts", "glue", "sanding", "sanded", "cutting", "cut",
    "slices", "sliced", "snapping", "snap", "fixing", "tolerance", "tolerances",
    "adjusting", "adjusted", "adjust", "scale", "scaled", "scaling", "dimensions", "size",
    "sizes", "configure", "configuration"
}


def connect_to_neo4j(uri: str, user: str, password: str) -> Graph:
    """Establish a connection to the Neo4j database."""
    try:
        graph = Graph(uri, auth=(user, password))
        graph.run("RETURN 1").evaluate()
        print("Connected to Neo4j.")
        return graph
    except Exception as e:
        print(f"Neo4j connection error: {e}")
        sys.exit(1)


def fetch_all_models(graph: Graph, label: str = "Model", embedding_prop: str = "embedding") -> pd.DataFrame:
    """Fetch all models with embeddings from Neo4j."""
    try:
        query = f"""
        MATCH (m:{label})
        WHERE m.{embedding_prop} IS NOT NULL
        RETURN m.id AS id, m.description AS description, m.{embedding_prop} AS embedding
        """
        records = graph.run(query).data()
        if not records:
            print("No models found with embeddings.")
            sys.exit(1)
        df = pd.DataFrame(records)
        df['embedding'] = df['embedding'].apply(lambda x: np.array(x) if isinstance(x, list) else np.array([]))
        print(f"Fetched {df.shape[0]} models from Neo4j.")
        return df
    except Exception as e:
        print(f"Error fetching models: {e}")
        sys.exit(1)


def preprocess_text(text: str) -> str:
    """Clean and preprocess text by removing unwanted words and stop words."""
    text = text.lower()
    pattern = r'\b(' + '|'.join(map(re.escape, UNWANTED_WORDS)) + r')\b'
    text = re.sub(pattern, '', text)
    text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'http\S+|www.\S+', '', text)
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in STOP_WORDS]
    doc = nlp(' '.join(tokens))
    lemmatized = [token.lemma_ for token in doc]
    return ' '.join(lemmatized)


def load_ground_truth(csv_path: str) -> pd.DataFrame:
    """Load ground truth data from CSV."""
    try:
        df = pd.read_csv(csv_path, dtype=str)
        required_columns = {'query_id', 'related_id'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"CSV must contain columns: {required_columns}")
        df = df.dropna(subset=['query_id', 'related_id'])
        df['query_id'] = df['query_id'].str.strip()
        df['related_id'] = df['related_id'].str.strip()
        print(f"Loaded ground truth with {df.shape[0]} relations.")
        return df
    except FileNotFoundError:
        print(f"CSV file not found at path: {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        sys.exit(1)


def compute_similarity(query: str, model: SentenceTransformer, embeddings: np.ndarray, ids: list,
                       threshold: float = 0.6) -> list:
    """Compute similarity and retrieve relevant model IDs."""
    processed_query = preprocess_text(query)
    if not processed_query:
        print("Processed query is empty. Skipping.")
        return []
    query_embedding = model.encode(processed_query, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(query_embedding, embeddings)[0]
    retrieved_indices = (cosine_scores >= threshold).nonzero(as_tuple=True)[0].tolist()
    retrieved_ids = [ids[idx] for idx in retrieved_indices]
    print(f"Retrieved {len(retrieved_ids)} models with threshold {threshold}.")
    return retrieved_ids


def evaluate_single_query(retrieved_ids: list, related_ids: list, k: int = 20) -> dict:
    """Calculate Precision, Recall, F1-Score, and NDCG@k for a single query."""
    retrieved_set = set(retrieved_ids[:k])
    related_set = set(related_ids)
    TP = len(retrieved_set & related_set)
    FP = len(retrieved_set - related_set)
    FN = len(related_set - retrieved_set)
    precision = TP / (TP + FP) if TP + FP else 0.0
    recall = TP / (TP + FN) if TP + FN else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if precision + recall else 0.0
    relevance = [1 if id_ in related_set else 0 for id_ in retrieved_ids[:k]]
    ideal_relevance = sorted(relevance, reverse=True)
    ndcg = ndcg_score([ideal_relevance], [relevance], k=k) if any(relevance) else 0.0
    return {'precision': precision, 'recall': recall, 'f1_score': f1, 'ndcg@20': ndcg}


def plot_metrics(metrics: dict, title: str):
    """Plot evaluation metrics."""
    plt.figure(figsize=(8, 6))
    sns.barplot(x=list(metrics.keys()), y=list(metrics.values()), palette='viridis')
    plt.title(title)
    plt.ylim(0, 1)
    for index, (metric, value) in enumerate(metrics.items()):
        plt.text(index, value + 0.01, f"{value:.2f}", ha='center')
    plt.tight_layout()
    plt.show()


def evaluate_search(ground_truth: pd.DataFrame, df: pd.DataFrame, model: SentenceTransformer, k: int = 20,
                    threshold: float = 0.6):
    """Evaluate search performance against ground truth."""
    embeddings = model.encode(df['description'].tolist(), convert_to_tensor=True, show_progress_bar=True)
    ids = df['id'].tolist()

    for query_id in ground_truth['query_id'].unique():
        related_ids = ground_truth.loc[ground_truth['query_id'] == query_id, 'related_id'].tolist()
        query_description = df.loc[df['id'] == query_id, 'description'].values
        if not query_description.size:
            print(f"No description found for query_id {query_id}. Skipping.")
            continue
        query = query_description[0]
        retrieved_ids = compute_similarity(query, model, embeddings, ids, threshold=threshold)
        metrics = evaluate_single_query(retrieved_ids, related_ids, k=k)
        print(f"Query ID {query_id} Metrics: {metrics}")
        plot_metrics(metrics, f"Metrics for Query ID {query_id}")


def main():
    """Main function to execute the evaluation."""

    CSV_PATH = 'test.csv'
    LABEL = "Model"
    EMBEDDING_PROP = "embedding"
    K = 60
    THRESHOLD = 0.5

    ground_truth = load_ground_truth(CSV_PATH)

    uri = os.getenv("NEO4J_CONNECTION_URL")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    graph = connect_to_neo4j(uri, user, password)

    df = fetch_all_models(graph, label=LABEL, embedding_prop=EMBEDDING_PROP)

    df['description'] = df['description'].apply(preprocess_text)

    model = SentenceTransformer('all-MiniLM-L6-v2')

    evaluate_search(ground_truth, df, model, k=K, threshold=THRESHOLD)

if __name__ == "__main__":
    main()
