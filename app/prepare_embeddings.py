import json
import os
import faiss
import pandas as pd

from sentence_transformers import SentenceTransformer
from datasets import load_dataset

# Caminhos para diretórios de entrada e saída
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(project_root, 'data', 'legislacao_pronta', 'rag_*.jsonl')
output_path = os.path.join(project_root, 'data', 'legislacao_embeddings')

if not os.path.exists(output_path):
    os.makedirs(output_path)

# Carregar o dataset a ser utilizado para a geração dos embeddings
# utilizando HuggingFace Datasets
embeddings_dataset = load_dataset('json', data_files=input_path, split='train')
print(f"Total de {len(embeddings_dataset)} artigos encontrados")

# Carregar o modelo de embeddings
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Extrair os textos dos artigos gerados
textos = [artigo['conteudo'] for artigo in embeddings_dataset]
print(f"Total de {len(textos)} textos, dos artigos encontrados")

# Gerar os embeddings
embeddings = model.encode(textos, batch_size=32, show_progress_bar=True)
print(f"Total de {len(embeddings)} embeddings gerados")

# Criar um índice FAISS com os embeddings gerados
vector_dim = embeddings.shape[1]
index = faiss.IndexFlatIP(vector_dim)
index.add(embeddings)

# Salvar o índice FAISS em um arquivo
faiss.write_index(index, os.path.join(output_path, 'faiss_embeddings.bin'))

# Salvando todos os artigos do modelo rag, para consulta posterior
json_embeddings = embeddings_dataset.to_json(
    os.path.join(output_path, 'artigos_absolutos.jsonl'),
    orient='records',
    lines=True,
    force_ascii=False
)
print(f"Arquivo {os.path.join(output_path, 'artigos_absolutos.jsonl')} salvo com sucesso")