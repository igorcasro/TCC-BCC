import os
import glob
from docling.document_converter import DocumentConverter

# 1. Buscar o arquivo e definir paths
# Paths are being passed like this to avoid some path finding errors
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(project_root, 'data', 'legislacao_bruta')
output_path = os.path.join(project_root, 'data', 'legislacao_processada')

files = glob.glob(os.path.join(input_path, '*.pdf'))

# 2. Processar com Docling
converter = DocumentConverter()

if not os.path.exists(output_path):
    os.makedirs(output_path)

for file in files:
    print(f'Converting file: {file}')

    result = converter.convert(file)
    
    base_name = os.path.basename(file).replace('.pdf', '.md')

    # 3. Salvar com nome padronizado em legislacao_processada
    output_file = os.path.join(output_path, base_name)

    makdown_converted = result.document.export_to_markdown()
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(makdown_converted)
        f.flush()
        os.fsync(f.fileno())

    print(f'Arquivo {base_name} salvo com sucesso em: {output_file}')