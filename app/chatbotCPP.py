import streamlit as st
import faiss
import os, json
import numpy as np

from langchain_core.messages import AIMessage, HumanMessage
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
    

# Carregando índice FAISS, juntamente com toda a 
# legislação processada e salva em arquivo json
# além de pegar os caminhos de todos os arquivos utilizados
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
index_path = os.path.join(project_root, 'data', 'legislacao_embeddings', 'faiss_embeddings.bin')
artigos_path = os.path.join(project_root, 'data', 'legislacao_embeddings', 'artigos_chunks.jsonl')
model_path = os.path.join(project_root, 'Llama-3.2-3B', 'Llama3.2-maIN.gguf')

index = faiss.read_index(index_path)

with open(artigos_path, 'r', encoding='utf-8') as f:
    artigos = [json.loads(linha) for linha in f if linha.strip()]
    f.close()

model_embeddings = SentenceTransformer('all-MiniLM-L6-v2')

# Caminho para o modelo GGUF baixado
# MODEL_PATH = "../Llama-3.2-3B/Llama3.2-maIN.gguf"  # Altere conforme necessário

# Configurações do Streamlit
st.set_page_config(page_title="Seu assistente virtual 🤖", page_icon="🤖")
st.title("Seu assistente virtual 🤖")

# Inicializa o modelo Llama-CPP
@st.cache_resource
def load_model():
    return Llama(
        model_path=model_path,
        n_gpu_layers=-1,     # Usa GPU se disponível
        n_ctx=2048,          # Janela de contexto
        temperature=0.1,     # Mais precisão e menos criatividade
    )

llm = load_model()

# Busca o contexto da pergunta, baseado no FAISS
def recupera_contexto(pergunta, top_k=5, max_chars=1600):
    vetor_pergunta = model_embeddings.encode([pergunta])
    D, I = index.search(np.array(vetor_pergunta, dtype=np.float32), top_k)

    grupos = {}

    # Primeiro: apenas agrupar
    for idx in I[0]:
        if idx < 0 or idx >= len(artigos):
            continue

        artigo = artigos[idx]
        id_completo = artigo.get('id', '')
        id_base = id_completo.rsplit("_chunk_", 1)[0]

        if id_base not in grupos:
            grupos[id_base] = {
                "tipo": artigo.get('tipo', 'Tipo desconhecido'),
                "artigo": artigo.get('artigo', 'Artigo desconhecido'),
                "fonte": artigo.get('fonte', 'Fonte desconhecida'),
                "partes": []
            }

        grupos[id_base]["partes"].append({
            "parte": artigo.get("parte", 1),
            "conteudo": artigo.get("conteudo", "").strip()
        })

    # Segundo: montar o contexto fora do loop
    contexto = ""
    total = 0

    for id_base, dados in grupos.items():
        tipo = dados["tipo"]
        artigo = dados["artigo"]
        fonte = dados["fonte"]

        # Ordenar as partes pelo número da 'parte'
        partes_ordenadas = sorted(dados["partes"], key=lambda x: x["parte"])
        texto_completo = "\n".join(p["conteudo"] for p in partes_ordenadas)

        bloco_formatado = f"[{tipo}] {artigo} - {fonte}\n{texto_completo}\n\n"

        if total + len(bloco_formatado) > max_chars:
            break

        contexto += bloco_formatado
        total += len(bloco_formatado)

    return contexto


def model_response(user_query, chat_history):
    """Gera resposta usando o modelo Llama-CPP, com contexto jurídico passado
    , no modo chat."""

    # Recuperação do contexto a ser utilizado
    contexto = recupera_contexto(user_query)
    print("Chunks recuperados")
    print("="*40)
    print(f"Contexto: \n{contexto}")
    print("="*40)

    # Lista de mensagens no formato esperado
    messages = []

    # Mensagem de sistema (comportamento do assistente)
    system_prompt = (
        "Você é um assistente jurídico especializado em leis brasileiras. "
        "Todas as respostas devem ser baseadas apenas nas informações fornecidas no contexto a seguir. "
        "Se a informação não estiver presente, diga que não pode responder com base nos dados fornecidos.\n\n"
        # "=== CONTEXTO INÍCIO ===\n"
        f"{contexto}\n"
        # "=== CONTEXTO FIM ===\n"
        "Se a resposta não estiver no contexto acima, diga que não pode responder."
    )
    messages.append({"role": "system", "content": system_prompt})

    # Adiciona o histórico de conversa no formato correto
    for msg in chat_history:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})

    # Adiciona a nova mensagem do usuário
    messages.append({"role": "user", "content": user_query})

    try:
        # Geração de resposta com create_chat_completion
        response = llm.create_chat_completion(
            messages=messages,
            max_tokens=1024,
            stream=False
        )
        return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"❌ Erro ao gerar resposta: {str(e)}"

# Inicialização do histórico de mensagens
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Olá, sou o seu assistente virtual! Como posso ajudar você?"),
    ]

# Exibe o histórico de mensagens
for message in st.session_state.chat_history:
    role = "AI" if isinstance(message, AIMessage) else "Human"
    with st.chat_message(role):
        st.markdown(message.content)

# Entrada do usuário
user_query = st.chat_input("Digite sua mensagem aqui...")
if user_query:
    # Adiciona a mensagem do usuário no histórico
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("Human"):
        st.markdown(user_query)

    # Gera resposta da IA
    with st.chat_message("AI"):
        resp = model_response(user_query, st.session_state.chat_history)
        st.markdown(resp)

    # Adiciona resposta ao histórico
    st.session_state.chat_history.append(AIMessage(content=resp))
