# Função para substituir caracteres especiais com expressões regulares
import re
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

from nltk.tokenize import sent_tokenize

# Dicionário para mapear números romanos para ordinais
mapeamento_romanos_ordinais = {
    'I': 'primeiro', 'II': 'segundo', 'III': 'terceiro', 'IV': 'quarto',
    'V': 'quinto', 'VI': 'sexto', 'VII': 'sétimo', 'VIII': 'oitavo', 'IX': 'nono',
    'X': 'décimo', 'XI': 'décimo primeiro', 'XII': 'décimo segundo',
    'XIII': 'décimo terceiro', 'XIV': 'décimo quarto', 'XV': 'décimo quinto',
    'XVI': 'décimo sexto', 'XVII': 'décimo sétimo', 'XVIII': 'décimo oitavo',
    'XIX': 'décimo nono', 'XX': 'vigésimo', 'XXI': 'vigésimo primeiro',
    'XXII': 'vigésimo segundo', 'XXIII': 'vigésimo terceiro', 'XXIV': 'vigésimo quarto',
    'XXV': 'vigésimo quinto', 'XXVI': 'vigésimo sexto', 'XXVII': 'vigésimo sétimo',
    'XXVIII': 'vigésimo oitavo', 'XXIX': 'vigésimo nono', 'XXX': 'trigésimo',
    'XXXI': 'trigésimo primeiro', 'XXXII': 'trigésimo segundo', 'XXXIII': 'trigésimo terceiro',
    'XXXIV': 'trigésimo quarto', 'XXXV': 'trigésimo quinto', 'XXXVI': 'trigésimo sexto',
    'XXXVII': 'trigésimo sétimo', 'XXXVIII': 'trigésimo oitavo', 'XXXIX': 'trigésimo nono',
    'XL': 'quadragésimo', 'XLI': 'quadragésimo primeiro', 'XLII': 'quadragésimo segundo',
    'XLIII': 'quadragésimo terceiro', 'XLIV': 'quadragésimo quarto', 'XLV': 'quadragésimo quinto',
    'XLVI': 'quadragésimo sexto', 'XLVII': 'quadragésimo sétimo', 'XLVIII': 'quadragésimo oitavo',
    'XLIX': 'quadragésimo nono', 'L': 'quinquagésimo', 'LI': 'quinquagésimo primeiro',
    'LII': 'quinquagésimo segundo', 'LIII': 'quinquagésimo terceiro', 'LIV': 'quinquagésimo quarto',
    'LV': 'quinquagésimo quinto', 'LVI': 'quinquagésimo sexto', 'LVII': 'quinquagésimo sétimo',
    'LVIII': 'quinquagésimo oitavo', 'LIX': 'quinquagésimo nono', 'LX': 'sexagésimo',
    'LXI': 'sexagésimo primeiro', 'LXII': 'sexagésimo segundo', 'LXIII': 'sexagésimo terceiro',
    'LXIV': 'sexagésimo quarto', 'LXV': 'sexagésimo quinto', 'LXVI': 'sexagésimo sexto',
    'LXVII': 'sexagésimo sétimo', 'LXVIII': 'sexagésimo oitavo', 'LXIX': 'sexagésimo nono',
    'LXX': 'septuagésimo', 'LXXI': 'septuagésimo primeiro', 'LXXII': 'septuagésimo segundo',
    'LXXIII': 'septuagésimo terceiro', 'LXXIV': 'septuagésimo quarto', 'LXXV': 'septuagésimo quinto',
    'LXXVI': 'septuagésimo sexto', 'LXXVII': 'septuagésimo sétimo', 'LXXVIII': 'septuagésimo oitavo',
    'LXXIX': 'septuagésimo nono', 'LXXX': 'octogésimo', 'LXXXI': 'octogésimo primeiro',
    'LXXXII': 'octogésimo segundo', 'LXXXIII': 'octogésimo terceiro', 'LXXXIV': 'octogésimo quarto',
    'LXXXV': 'octogésimo quinto', 'LXXXVI': 'octogésimo sexto', 'LXXXVII': 'octogésimo sétimo',
    'LXXXVIII': 'octogésimo oitavo', 'LXXXIX': 'octogésimo nono', 'XC': 'nonagésimo',
    'XCI': 'nonagésimo primeiro', 'XCII': 'nonagésimo segundo', 'XCIII': 'nonagésimo terceiro',
    'XCIV': 'nonagésimo quarto', 'XCV': 'nonagésimo quinto', 'XCVI': 'nonagésimo sexto',
    'XCVII': 'nonagésimo sétimo', 'XCVIII': 'nonagésimo oitavo', 'XCIX': 'nonagésimo nono',
    'C': 'centésimo'
}

# Expressão regular que cobre todos os romanos de 1 - 100  
padrao_romanos = r'\b(M{0,3}|C|XC|XL|L|X{0,3}|IX|IV|V?I{0,3})\b'

# Função para substituir números romanos por ordinais usando regex
def substituir_numeros_romanos(texto):
    # Função auxiliar para substituição
    def substituir_por_ordinal(match):
        romano = match.group(0)
        return mapeamento_romanos_ordinais.get(romano, romano)
    
    # Substituição com re.sub usando a função de substituição
    texto_corrigido = re.sub(padrao_romanos, substituir_por_ordinal, texto)
    
    return texto_corrigido

def substituir_caracteres_com_re(texto):
    substituicoes = {
        r'§': 'Parágrafo ',
        r'º': '(o) ',
        r'ª': '(a) ',
        r'“|”': ' " ',  # Substitui aspas duplas
        r'‘|’': " ' ",  # Substitui aspas simples
        r'—|–': ' - ',  # Substitui diferentes tipos de hífen
        r'Art\.': ' Artigo ',
        r'Inc\.': ' Inciso ',
        r'C\.C\.': ' Código Civil ',
        r'C\.P\.': ' Código Penal ',
        r'C\.F\.': ' Constituição Federal ',
        r'R\$': ' reais ',
        r'/': ' de ',
    }
    
    for padrao, substituto in substituicoes.items():
        texto = re.sub(padrao, substituto, texto)
    
    return texto

def limpar_sumario_e_imagens(texto):
    # Remover linhas típicas de sumário
    texto = re.sub(r'^.*\.{3,}\s*\d+\s*$', '', texto, flags=re.MULTILINE)

    # Remover imagens do markdown ![](imagem.png)
    texto = re.sub(r'!\[.*?\]\(.*?\)', '', texto)

    # Remover tags tipo <!image>, <! image >, etc. (HTML/Markdown estranhos)
    texto = re.sub(r'<\s*!?\s*image\s*.*?>', '', texto, flags=re.IGNORECASE)

    # Remover cabeçalhos comuns de legislação
    padroes_indesejados = [
        r'Presidência da República',
        r'Secretaria-Geral',
        r'Subchefia para Assuntos Jurídicos',
        r'Página \d+ de \d+'
    ]

    for padrao in padroes_indesejados:
        texto = re.sub(padrao, '', texto, flags=re.IGNORECASE)

    return texto

# Chunking baseado em sentenças
def chunk_por_sentencas(texto, tamanho_max_chars=1200):
    sentencas = sent_tokenize(texto, language='portuguese')
    blocos = []
    bloco_atual = ""

    for sentenca in sentencas:
        if len(bloco_atual) + len(sentenca) + 1 <= tamanho_max_chars:
            bloco_atual += (" " if bloco_atual else "") + sentenca
        else:
            if bloco_atual:
                blocos.append(bloco_atual.strip())
            bloco_atual = sentenca

    if bloco_atual:
        blocos.append(bloco_atual.strip())

    return blocos
