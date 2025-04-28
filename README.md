## ChatBot treinado com a legislação brasileira

A sequência atual de desenvolvimento foi:
- preprocess.py: processa os arquivos PDF utilizando Docling e os converte para arquivos .md;
- convert_jsonl.py: converte os arquivos .md em arquivos .jsonl, tanto no modelo user / assistant (caso seja decidido fazer o fine-tuning) quanto no modelo ideal para implementação de RAG.
- prepare_embeddings.py: prepara os embeddings e os salva em um arquivo FAISS (Facebook AI Similarity Search), para que seja possível a busca futura, sem custo de armazenamento e, também, de forma rápida, para as respostas necessárias.


### Modelo de RN Utilizada
- https://huggingface.co/Inza124/Llama3.2_3b