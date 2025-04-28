import os
import glob
import re
import json

from utils import mapeamento_romanos_ordinais
from utils import substituir_numeros_romanos
from utils import substituir_caracteres_com_re
from utils import limpar_sumario_e_imagens

# Mapeando os tipos de legislação processados
LEGISLACAO_TIPOS = {
    "codigo_penal": "Direito Penal",
    "constituicao_federal" : "Direito Constitucional",
    "declaracao_universal_dos_direitos_humanos": "Direitos Humanos"
    
}

# Buscando arquivos e definindo paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(project_root, 'data', 'legislacao_processada')
output_path = os.path.join(project_root, 'data', 'legislacao_pronta')

if not os.path.exists(output_path):
    os.makedirs(output_path)

log_path = os.path.join(project_root, 'data', 'log_integridade.txt')

# Abrir log
total_processados = 0
rag_total_processados = 0
erros = []

with open(log_path, 'w', encoding='utf-8') as log:
    log.write('==== LOG DE PROCESSAMENTO DE LEGISLAÇÃO ====\n')

    files = glob.glob(os.path.join(input_path, '*.md'))

    for file in files:
        try:
            base_name = os.path.basename(file).replace('.md', '.jsonl')
            output_file = os.path.join(output_path, base_name)
            
            rag_base_name = f"rag_{base_name}"
            rag_output_file = os.path.join(output_path, rag_base_name)
            
            with open(file, 'r', encoding='utf-8') as f:
                texto = f.read()

            # Removendo espaços extras e quebras de linha indesejadas
            texto_limpo = re.sub(r'\s+', ' ', texto).strip()
            print(f'Espaços extras e quebras removidas de {base_name}')

            # Removendo imagens e sumários, irrelevantes no contexto da legislação
            texto_limpo = limpar_sumario_e_imagens(texto_limpo)
            print(f'Sumário e imagens removidos de {base_name}')

            # retirando termos comuns do arquivo, para facilitar no treinamento da base
            texto_limpo = substituir_caracteres_com_re(texto_limpo)
            print(f'Termos comuns removidos de {base_name}')

            # removendo --- ou ... desnecessários
            texto_limpo = re.sub(r'[-_.]{3,}', '', texto_limpo)
            print(f"Hífens e pontos excessivos removidos de {base_name}")

            # removendo - * desnecessários
            texto_limpo = re.sub(r'[-*]', '', texto_limpo)
            print(f"Hífens seguidos de asteriscos removidos de {base_name}")

            # removendo # desnecessários
            texto_limpo = re.sub(r'[#]', '', texto_limpo)
            print(f"Hasthtags removidos de {base_name}")  

            # remoção de 'o' e 'a' isolados no texto (resquícios de símbolos como º e ª)
            texto_limpo = re.sub(r'(\s)[oa](?=\s)', '', texto_limpo) 
            print(f'Letras isoladas removidas de {base_name}')  

            # Troca de art. por Artigo, para facilitar posterior processamento
            artigos_regex = r'(?i)\b(art(?:igo)?\.?)\b'
            texto_limpo = re.sub(artigos_regex, 'Artigo', texto_limpo) 
            print(f'Letras isoladas removidas de {base_name}')     

            # trocando os algorismos romanos do texto por ordinais
            texto_limpo = substituir_numeros_romanos(texto_limpo)
            for romano, escrito in mapeamento_romanos_ordinais.items():
                texto_limpo = re.sub(r'Art\. {romano}\b', r'Art\. {escrito}', texto_limpo)
            print(f'Algarismos romanos alterados em: {base_name}')

            artigos_segmentados = r'(?i)\b(art(?:igo|\.?)\.?)\s*(\d+[\dºª\-\.A-Za-z]*)'

            # Segmentação
            blocos_texto = re.split(artigos_segmentados, texto_limpo)
            artigos = []
            rag_artigos = []

            for i in range(1, len(blocos_texto), 2):
                titulo = f"{blocos_texto[i].rstrip('.')}"
                conteudo = blocos_texto[i + 1].strip() if i + 1 < len(blocos_texto) else ""
                # Verifica se está puxando titulo e conteúdo
                # print(f'Titulo: {titulo}\nConteudo: {conteudo[:50]}')

                base_name_no_extension = os.path.splitext(base_name)[0]
                rag_artigo_id = f"{base_name_no_extension}_{titulo.replace(" ", "_")}"
                rag_artigo_fonte = base_name_no_extension.replace("_", " ").title()
                rag_artigo_tipo = LEGISLACAO_TIPOS.get(base_name_no_extension)

                if len(conteudo) > 10:  # Ignorar ruído
                    artigos.append({
                        "messages": [
                            {"role": "user", "content": f"Artigo {titulo}"},
                            {"role": "assistant", "content": conteudo}
                        ]
                    })

                    rag_artigos.append({
                        "id": rag_artigo_id,
                        "fonte": rag_artigo_fonte,
                        "tipo": rag_artigo_tipo,
                        "artigo": f"Artigo {titulo}",
                        "conteudo": conteudo,
                    })

            # Salvamento
            with open(output_file, 'w', encoding='utf-8') as f:
                for artigo in artigos:
                    f.write(json.dumps(artigo, ensure_ascii=False) + '\n')
            total_processados += 1

            with open(rag_output_file, 'w', encoding='utf-8') as f:
                for rag_artigo in rag_artigos:
                    f.write(json.dumps(rag_artigo, ensure_ascii=False) + '\n')
            rag_total_processados += 1
            
            log.write(f'[OK] {base_name}: {len(artigos)} artigos segmentados.\n')
            log.write(f'[OK] {rag_base_name}: {len(rag_artigos)} artigos segmentados.\n')

        except Exception as e:
            erros.append(file)
            log.write(f'[ERRO] {file}: {str(e)}\n')

    log.write(f'\nTOTAL PROCESSADOS: {total_processados + rag_total_processados}\n')
    if erros:
        log.write(f'FALHAS EM: {len(erros)} arquivos:\n')
        for f in erros:
            log.write(f' - {f}\n')

print(f'Processamento finalizado! {total_processados + rag_total_processados} arquivos convertidos.')
