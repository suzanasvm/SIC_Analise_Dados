import pandas as pd
import sys
import argparse
from pathlib import Path
from collections import Counter
import re
import unicodedata

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, mac_morpho

# Download automático dos recursos do NLTK
recursos = ['punkt', 'stopwords', 'mac_morpho', 'punkt_tab', 'rslp']
for resource in recursos:
    try:
        nltk.download(resource, quiet=True)
    except Exception:
        pass

# Configuração do NLTK Tagger
try:
    stop_words = set(stopwords.words('portuguese'))
    tagged_sents = mac_morpho.tagged_sents()
    tagger = nltk.UnigramTagger(tagged_sents)
except Exception as e:
    print(f"Erro ao inicializar recursos do NLTK: {e}")
    sys.exit(1)

def mapear_classe_macmorpho(tag):
    """Mapeia as tags do MacMorpho do NLTK para as categorias gramaticais."""
    if not tag:
        return 'Outros'
    
    tag = tag.upper()
    
    if tag.startswith('V'):
        return 'Verbo'
    elif tag.startswith('NPROP'):
        return 'Nome Próprio'
    elif tag.startswith('N'):
        return 'Substantivo'
    elif tag.startswith('ADJ'):
        return 'Adjetivo'
    elif tag.startswith('ADV'):
        return 'Advérbio'
    elif tag.startswith('KC') or tag.startswith('KS'):
        return 'Conectivo'
    elif tag.startswith('PREP') or tag.startswith('P3P'):
        return 'Preposição'
    else:
        return 'Outros'

def contar_citacoes(texto):
    """Identifica e conta citações bibliográficas no texto."""
    if pd.isna(texto):
        return 0
    
    texto_str = str(texto)
    
    padrao_autor_ano = r'\([A-ZÀ-Ú][a-zà-úA-ZÀ-Ú\s&,.-]+(?:\set\sal\.)?,\s*(?:19|20)\d{2}[a-z]?\)'
    padrao_autor_fora = r'[A-ZÀ-Ú][a-zà-úA-ZÀ-Ú\s&.-]+(?:\set\sal\.)?\s*\((?:19|20)\d{2}[a-z]?\)'
    padrao_numerico = r'\[\d+(?:\s*[\,-]\s*\d+)*\]'
    
    citacoes = (len(re.findall(padrao_autor_ano, texto_str)) + 
                len(re.findall(padrao_autor_fora, texto_str)) + 
                len(re.findall(padrao_numerico, texto_str)))
    return citacoes

def limpar_e_tokenizar(texto):
    """
    Limpa o texto removendo URLs e acentuação de forma segura 
    para evitar cortar palavras acentuadas (ex: importância -> importancia).
    """
    if pd.isna(texto):
        return []
    
    texto = str(texto).lower()
    
    # Remover URLs
    texto = re.sub(r'http\S+|www\S+', '', texto)
    
    # Normalizar Unicode para remover acentos mantendo todas as letras intactas
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    
    # Manter apenas letras e espaços
    texto = re.sub(r'[^a-z\s]', ' ', texto)
    
    tokens = word_tokenize(texto, language='portuguese')
    return tokens

def analisar_texto(texto, min_tamanho=2):
    """Processa um único texto e retorna as contagens por classe e citações."""
    contagem_classes = Counter({
        'Substantivo': 0,
        'Nome Próprio': 0,
        'Verbo': 0,
        'Adjetivo': 0,
        'Advérbio': 0,
        'Conectivo': 0,
        'Preposição': 0,
        'Outros': 0
    })
    
    citacoes = contar_citacoes(texto)
    tokens = limpar_e_tokenizar(texto)
    tokens_filtrados = [t for t in tokens if len(t) >= min_tamanho and t not in stop_words]
    
    if not tokens_filtrados:
        return Counter(), contagem_classes, citacoes
    
    palavras_etiquetadas = tagger.tag(tokens_filtrados)
    contagem_palavras = Counter()
    
    for palavra, tag in palavras_etiquetadas:
        classe = mapear_classe_macmorpho(tag)
        contagem_palavras[(palavra, classe)] += 1
        contagem_classes[classe] += 1
        
    return contagem_palavras, contagem_classes, citacoes

def main(arquivo_csv, arquivo_saida):
    caminho = Path(arquivo_csv)
    if not caminho.exists():
        print(f"Erro: arquivo '{arquivo_csv}' não encontrado.")
        sys.exit(1)
        
    print(f"Carregando arquivo CSV: {arquivo_csv}")
    try:
        df = pd.read_csv(arquivo_csv)
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        sys.exit(1)
        
    print(f"Total de artigos carregados: {len(df)}")
    
    # Mapeamento flexível das colunas de seções
    mapa_colunas = {
        'Introdução': ['caminho_introducao', 'introducao', 'introdução', 'intro', 'introduction'],
        'Materiais e Métodos': ['materiais_metodos', 'materiais_e_metodos', 'metodologia', 'materiais', 'methods'],
        'Resultados e Discussão': ['resultados_discussao', 'resultados_e_discussao', 'resultados', 'discussao', 'results'],
        'Conclusão': ['conclusao', 'conclusoes', 'conclusão', 'conclusion'],
        'Agradecimentos': ['agradecimentos', 'agradecimento', 'acknowledgments'],
        'Referências': ['referencias', 'referências', 'references']
    }
    
    secoes_validas = {}
    colunas_csv_lower = {col.lower(): col for col in df.columns}
    
    for nome_secao, possiveis_nomes in mapa_colunas.items():
        for nome in possiveis_nomes:
            if nome.lower() in colunas_csv_lower:
                coluna_real = colunas_csv_lower[nome.lower()]
                secoes_validas[coluna_real] = nome_secao
                break

    if not secoes_validas:
        print("Erro: Nenhuma coluna de seção reconhecida foi encontrada no CSV.")
        sys.exit(1)
        
    coluna_id = 'id_artigo' if 'id_artigo' in df.columns else df.columns[0]
    
    registros_palavras = []
    resumo_geral_secoes = []
    resumo_por_artigo = []
    
    # Estrutura acumuladora geral por seção
    acumulado_secoes = {
        nome: {'classes': Counter(), 'citacoes': 0, 'palavras': Counter()} 
        for nome in secoes_validas.values()
    }

    print("\nIniciando processamento por artigo e seção...")
    
    for idx, row in df.iterrows():
        artigo_id = row[coluna_id] if pd.notna(row[coluna_id]) else f"Artigo_{idx+1}"
        
        for coluna_csv, nome_secao in secoes_validas.items():
            texto = row[coluna_csv]
            
            cont_palavras, cont_classes, citacoes = analisar_texto(texto)
            
            # Acumular no resumo individual por artigo
            item_artigo = {
                'id_artigo': artigo_id,
                'Secao': nome_secao
            }
            item_artigo.update(cont_classes)
            item_artigo['Total_Citacoes'] = citacoes
            resumo_por_artigo.append(item_artigo)
            
            # Acumular para o resumo geral de seções
            acumulado_secoes[nome_secao]['classes'] += cont_classes
            acumulado_secoes[nome_secao]['citacoes'] += citacoes
            acumulado_secoes[nome_secao]['palavras'] += cont_palavras

    # Gerar registros gerais de palavras
    for nome_secao, dados in acumulado_secoes.items():
        for (palavra, classe), freq in dados['palavras'].items():
            registros_palavras.append({
                'Secao': nome_secao,
                'Palavra': palavra,
                'Classe_Gramatical': classe,
                'Frequencia': freq
            })
            
        resumo_item = {'Secao': nome_secao}
        resumo_item.update(dados['classes'])
        resumo_item['Total_Citacoes'] = dados['citacoes']
        resumo_geral_secoes.append(resumo_item)

    # DataFrames
    df_palavras = pd.DataFrame(registros_palavras)
    df_resumo_geral = pd.DataFrame(resumo_geral_secoes)
    df_resumo_artigo = pd.DataFrame(resumo_por_artigo)
    
    if not df_palavras.empty:
        df_palavras = df_palavras.sort_values(by=['Secao', 'Frequencia'], ascending=[True, False])
    
    # 1. Salvar palavras gerais
    df_palavras.to_csv(arquivo_saida, index=False, encoding='utf-8-sig')
    print(f"\n✅ Contagem de palavras salva em: {arquivo_saida}")
    
    # 2. Salvar resumo geral de seções
    caminho_resumo = Path(arquivo_saida).stem + "_resumo_gramatical.csv"
    df_resumo_geral.to_csv(caminho_resumo, index=False, encoding='utf-8-sig')
    print(f"✅ Resumo por classe e citações (Geral) salvo em: {caminho_resumo}")
    
    # 3. Salvar NOVO resumo detalhado por ARTIGO
    caminho_artigo = Path(arquivo_saida).stem + "_resumo_por_artigo.csv"
    df_resumo_artigo.to_csv(caminho_artigo, index=False, encoding='utf-8-sig')
    print(f"✅ Resumo por artigo salvo em: {caminho_artigo}\n")

    # Exibir resumo no console
    print("="*85)
    print("RESUMO DE ELEMENTOS TEXTUAIS E CITAÇÕES POR SEÇÃO (GERAL)")
    print("="*85)
    print(df_resumo_geral.to_string(index=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Análise de elementos gramaticais e citações por seção e artigo.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('arquivo_csv', help='Caminho do CSV de entrada com os artigos.')
    parser.add_argument(
        '-o', '--output', 
        default='contagem_palavras_por_secao.csv',
        help='Caminho do CSV de saída (Padrão: contagem_palavras_por_secao.csv)'
    )
    
    args = parser.parse_args()
    main(args.arquivo_csv, args.output)