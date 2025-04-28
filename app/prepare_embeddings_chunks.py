import os
import faiss
import json
import numpy as np

from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from tqdm import tqdm
from utils import chunk_por_sentencas

# Caminhos para diretórios de entrada e saída
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(project_root, 'data', 'legislacao_pronta', 'rag_*.jsonl')
output_path = os.path.join(project_root, 'data', 'legislacao_embeddings')

if not os.path.exists(output_path):
    os.makedirs(output_path)

# Parâmetro de chunking
tamanho_max_chunk = 600  # número máximo de caracteres por bloco

# Carregar o dataset de arquivos RAG
embeddings_dataset = load_dataset('json', data_files=input_path, split='train')
print(f"Total de {len(embeddings_dataset)} artigos encontrados")

# Carregar modelo de embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
vector_dim = model.get_sentence_embedding_dimension()
index = faiss.IndexFlatIP(vector_dim)

# Preparar armazenamento dos vetores e metadados
vetores = []
chunks_info = []

# Processar cada artigo
print("Gerando embeddings por blocos...")
for artigo in tqdm(embeddings_dataset):
    conteudo = artigo['conteudo']
    
    # Chunking baseado em sentenças
    blocos = chunk_por_sentencas(conteudo, tamanho_max_chars=1200)

    # Gera os embeddings e salva em blocos
    for i, bloco in enumerate(blocos, start=1):
        vetor = model.encode(bloco.strip())
        vetores.append(vetor)

        chunk = {
            "id": f"{artigo['id']}_chunk_{i}",
            "fonte": artigo.get("fonte", ""),
            "tipo": artigo.get("tipo", ""),
            "artigo": artigo.get("artigo", "").strip(),
            "parte": i,
            "conteudo": bloco.strip()
        }

        chunks_info.append(chunk)

# Converter para matriz FAISS
matriz = np.vstack(vetores)
index.add(matriz)

# Salvar índice FAISS
faiss_path = os.path.join(output_path, 'faiss_embeddings.bin')
faiss.write_index(index, faiss_path)
print(f"Índice FAISS salvo em: {faiss_path}")

# Salvar metadados dos chunks
json_path = os.path.join(output_path, 'artigos_chunks.jsonl')
with open(json_path, 'w', encoding='utf-8') as f:
    for chunk in chunks_info:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"Arquivo com chunks salvos em: {json_path}")
print(f"Total de {len(chunks_info)} blocos indexados.")
