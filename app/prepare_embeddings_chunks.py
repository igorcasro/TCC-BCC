import os
import faiss
import json
import textwrap
import numpy as np
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize

from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from tqdm import tqdm

# Caminhos para diretórios de entrada e saída
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(project_root, 'data', 'legislacao_pronta', 'rag_*.jsonl')
output_path = os.path.join(project_root, 'data', 'legislacao_embeddings')

if not os.path.exists(output_path):
    os.makedirs(output_path)

# Parâmetro de chunking
tamanho_max_chunk = 500  # número máximo de caracteres por bloco

# Carregar o dataset de arquivos RAG
embeddings_dataset = load_dataset('json', data_files=input_path, split='train')
print(f"Total de {len(embeddings_dataset)} artigos encontrados")

# Carregar modelo de embeddings
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
vector_dim = model.get_sentence_embedding_dimension()
index = faiss.IndexFlatIP(vector_dim)

# Preparar armazenamento dos vetores e metadados
vetores = []
chunks_info = []

# Processar cada artigo
print("Gerando embeddings por blocos...")
for artigo in tqdm(embeddings_dataset):
    conteudo = artigo['conteudo']
    sentencas = sent_tokenize(conteudo)
    blocos = []
    bloco_atual = ""

    for sent in sentencas:
        if len(bloco_atual) + len(sent) + 1 <= tamanho_max_chunk:
            bloco_atual += " " + sent
        else:
            blocos.append(bloco_atual.strip())
            bloco_atual = sent

    if bloco_atual:
        blocos.append(bloco_atual.strip())

    for i, bloco in enumerate(blocos, start=1):
        vetor = model.encode(bloco.strip())
        vetores.append(vetor)

        chunk = {
            "id": f"{artigo['id']}_chunk_{i}",
            "fonte": artigo.get("fonte", ""),
            "tipo": artigo.get("tipo", ""),
            "artigo": f"{artigo['artigo']} (parte {i})",
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
