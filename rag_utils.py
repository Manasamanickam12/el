from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def load_documents(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        docs = f.readlines()
    return [doc.strip() for doc in docs if doc.strip()]

def create_faiss_index(docs):
    embeddings = model.encode(docs)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index, embeddings

def search(query, docs, index, k=3):
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), k)
    results = [docs[i] for i in indices[0]]
    return "\n".join(results)
