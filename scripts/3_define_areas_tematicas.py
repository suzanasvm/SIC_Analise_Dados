# Análise Bibliométrica do Seminário de Iniciação Científica (SIC) IFNMG
# Período: 2022 a 2025
# Autor: [Seu Nome]
# Data: 2026

# ============================================================================
# PARTE 1: IMPORTAÇÃO DE BIBLIOTECAS
# ============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Configurações visuais
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# ============================================================================
# PARTE 2: CARREGAMENTO DOS DADOS
# ============================================================================

print("=" * 70)
print("CARREGAMENTO E EXPLORAÇÃO DOS DADOS")
print("=" * 70)

# Carregar os arquivos CSV
df_areas = pd.read_csv('trabalhos_por_area_tematica_2022_processado.csv')
df_palavras = pd.read_csv('2022_contagem_palavras_por_secao.csv')
df_artigos_palavras = pd.read_csv('2022_contagem_palavras_por_secao_resumo_por_artigo.csv')

print("\n1. PRIMEIRAS OBSERVAÇÕES DOS DADOS")
print("\nDataset de Áreas Temáticas:")
print(f"   Dimensões: {df_areas.shape[0]} linhas, {df_areas.shape[1]} colunas")
print(f"   Colunas: {list(df_areas.columns)}")
print(f"\n   Primeiras linhas:")
print(df_areas.head())

print("\nDataset de Contagem de Palavras (por seção):")
print(f"   Dimensões: {df_palavras.shape[0]} linhas, {df_palavras.shape[1]} colunas")
print(f"   Colunas: {list(df_palavras.columns)}")
print(f"\n   Primeiras linhas:")
print(df_palavras.head())

print("\nDataset de Contagem por Artigo:")
print(f"   Dimensões: {df_artigos_palavras.shape[0]} linhas, {df_artigos_palavras.shape[1]} colunas")
print(f"   Colunas: {list(df_artigos_palavras.columns)}")
print(f"\n   Primeiras linhas:")
print(df_artigos_palavras.head())

# ============================================================================
# PARTE 3: ANÁLISE EXPLORATÓRIA INICIAL
# ============================================================================

print("\n" + "=" * 70)
print("ANÁLISE EXPLORATÓRIA DOS DADOS")
print("=" * 70)

print("\n2. INFORMAÇÕES GERAIS")

# Quantidade total de trabalhos
total_trabalhos = df_areas.shape[0]
print(f"\n   Total de trabalhos analisados: {total_trabalhos}")

# Áreas temáticas
areas_unicas = df_areas['area_tematica'].nunique()
print(f"   Quantidade de áreas temáticas: {areas_unicas}")
print(f"\n   Áreas temáticas encontradas:")
print(df_areas['area_tematica'].value_counts())

# Categorias (se existir)
if 'categoria' in df_areas.columns:
    print(f"\n   Categorias de participação:")
    print(df_areas['categoria'].value_counts())

print("\n3. ANÁLISE DE PALAVRAS-CHAVE")
print(f"\n   Total de palavras únicas no acervo: {df_palavras['Palavra'].nunique()}")
print(f"   Frequência média das palavras: {df_palavras['Frequencia'].mean():.2f}")

print("\n   Top 15 palavras mais frequentes:")
top_palavras = df_palavras.nlargest(15, 'Frequencia')[['Palavra', 'Frequencia', 'Classe_Gramatical']]
print(top_palavras.to_string(index=False))

print("\n4. DISTRIBUIÇÃO POR CLASSE GRAMATICAL")
distribuicao_gramatical = df_palavras['Classe_Gramatical'].value_counts()
print(distribuicao_gramatical)

# ============================================================================
# PARTE 4: ANÁLISE TEMÁTICA APROFUNDADA
# ============================================================================

print("\n" + "=" * 70)
print("ANÁLISE TEMÁTICA DETALHADA")
print("=" * 70)

# Criar tabela de frequência por área temática
print("\n5. DISTRIBUIÇÃO DE TRABALHOS POR ÁREA TEMÁTICA")

tabela_areas = df_areas.groupby('area_tematica').agg({
    'titulo_do_trabalho': 'count',
}).rename(columns={'titulo_do_trabalho': 'Quantidade'})

tabela_areas['Percentual'] = (tabela_areas['Quantidade'] / total_trabalhos * 100).round(2)
tabela_areas = tabela_areas.sort_values('Quantidade', ascending=False)

print("\n" + tabela_areas.to_string())

# ============================================================================
# PARTE 5: ANÁLISE ESTRUTURAL DOS TRABALHOS
# ============================================================================

print("\n" + "=" * 70)
print("ANÁLISE ESTRUTURAL DOS TRABALHOS")
print("=" * 70)

print("\n6. ESTATÍSTICAS DE EXTENSÃO DOS TRABALHOS (por seção)")

# Colunas de classes gramaticais
colunas_gramaticais = ['Substantivo', 'Nome_Próprio', 'Verbo', 'Adjetivo', 
                       'Advérbio', 'Conectivo', 'Preposição', 'Outros']

# Verificar quais colunas existem
colunas_existentes = [col for col in colunas_gramaticais if col in df_artigos_palavras.columns]

print(f"\n   Seções analisadas por artigo:")
print(df_artigos_palavras['Secao'].value_counts())

print(f"\n   Estatísticas gerais de palavras por artigo:")
for col in colunas_existentes:
    media = df_artigos_palavras[col].mean()
    mediana = df_artigos_palavras[col].median()
    max_val = df_artigos_palavras[col].max()
    print(f"\n   {col}:")
    print(f"      Média: {media:.2f}")
    print(f"      Mediana: {mediana:.2f}")
    print(f"      Máximo: {int(max_val)}")

# ============================================================================
# PARTE 6: VISUALIZAÇÕES
# ============================================================================

print("\n" + "=" * 70)
print("GERANDO VISUALIZAÇÕES")
print("=" * 70)

# Figura 1: Distribuição de trabalhos por área temática
fig, ax = plt.subplots(figsize=(14, 6))
tabela_areas_plot = tabela_areas.sort_values('Quantidade', ascending=True)
ax.barh(range(len(tabela_areas_plot)), tabela_areas_plot['Quantidade'], color='steelblue')
ax.set_yticks(range(len(tabela_areas_plot)))
ax.set_yticklabels(tabela_areas_plot.index)
ax.set_xlabel('Quantidade de Trabalhos')
ax.set_title('Distribuição de Trabalhos por Área Temática (2022-2025)')
ax.grid(axis='x', alpha=0.3)

for i, v in enumerate(tabela_areas_plot['Quantidade']):
    ax.text(v + 0.5, i, str(int(v)), va='center')

plt.tight_layout()
plt.savefig('01_distribuicao_areas_tematicas.png', dpi=300, bbox_inches='tight')
print("\n✓ Gráfico salvo: 01_distribuicao_areas_tematicas.png")
plt.close()

# Figura 2: Top 20 palavras mais frequentes
fig, ax = plt.subplots(figsize=(12, 8))
top_20 = df_palavras.nlargest(20, 'Frequencia')
cores = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(top_20)))
ax.barh(range(len(top_20)), top_20['Frequencia'].values, color=cores)
ax.set_yticks(range(len(top_20)))
ax.set_yticklabels(top_20['Palavra'].values)
ax.set_xlabel('Frequência')
ax.set_title('Top 20 Palavras-chave Mais Frequentes (2022-2025)')
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

for i, v in enumerate(top_20['Frequencia'].values):
    ax.text(v + 2, i, str(int(v)), va='center')

plt.tight_layout()
plt.savefig('02_top_palavras_chave.png', dpi=300, bbox_inches='tight')
print("✓ Gráfico salvo: 02_top_palavras_chave.png")
plt.close()

# Figura 3: Distribuição por classe gramatical
fig, ax = plt.subplots(figsize=(10, 6))
dist_gramatical = df_palavras['Classe_Gramatical'].value_counts()
colors = plt.cm.Set3(np.linspace(0, 1, len(dist_gramatical)))
wedges, texts, autotexts = ax.pie(dist_gramatical.values, labels=dist_gramatical.index, 
                                    autopct='%1.1f%%', colors=colors, startangle=90)
ax.set_title('Distribuição de Palavras por Classe Gramatical (2022-2025)')

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

plt.tight_layout()
plt.savefig('03_distribuicao_classes_gramaticais.png', dpi=300, bbox_inches='tight')
print("✓ Gráfico salvo: 03_distribuicao_classes_gramaticais.png")
plt.close()

# Figura 4: Distribuição de palavras por seção
fig, ax = plt.subplots(figsize=(12, 6))
palavras_secao = df_palavras.groupby('Secao')['Frequencia'].sum().sort_values(ascending=False)
ax.bar(range(len(palavras_secao)), palavras_secao.values, color='coral')
ax.set_xticks(range(len(palavras_secao)))
ax.set_xticklabels(palavras_secao.index, rotation=45, ha='right')
ax.set_ylabel('Frequência Total')
ax.set_title('Frequência Total de Palavras por Seção dos Trabalhos (2022-2025)')
ax.grid(axis='y', alpha=0.3)

for i, v in enumerate(palavras_secao.values):
    ax.text(i, v + 50, str(int(v)), ha='center', va='bottom')

plt.tight_layout()
plt.savefig('04_frequencia_por_secao.png', dpi=300, bbox_inches='tight')
print("✓ Gráfico salvo: 04_frequencia_por_secao.png")
plt.close()

# ============================================================================
# PARTE 7: ANÁLISE TEMPORAL (se dados forem de múltiplos anos)
# ============================================================================

print("\n" + "=" * 70)
print("ANÁLISE TEMPORAL")
print("=" * 70)

# Tentar extrair ano do título ou criar agrupamento por arquivo
print("\n7. INFORMAÇÃO: Adicione coluna 'ano' aos seus dados para análise temporal")
print("   Exemplo: 2022, 2023, 2024, 2025")

# ============================================================================
# PARTE 8: ANÁLISE DE TENDÊNCIAS E INSIGHTS
# ============================================================================

print("\n" + "=" * 70)
print("INSIGHTS E TENDÊNCIAS PRINCIPAIS")
print("=" * 70)

print("\n8. PRINCIPAIS ACHADOS:")

# Área com mais trabalhos
area_destaque = tabela_areas.index[0]
qtd_destaque = tabela_areas.iloc[0]['Quantidade']
pct_destaque = tabela_areas.iloc[0]['Percentual']

print(f"\n   a) Área temática com maior participação:")
print(f"      {area_destaque}")
print(f"      Quantidade: {int(qtd_destaque)} trabalhos ({pct_destaque}%)")

# Palavra mais frequente
palavra_top = df_palavras.iloc[0]
print(f"\n   b) Termo mais frequente no acervo:")
print(f"      '{palavra_top['Palavra']}' ({int(palavra_top['Frequencia'])} ocorrências)")
print(f"      Classe gramatical: {palavra_top['Classe_Gramatical']}")

# Padrão estrutural
print(f"\n   c) Estrutura média dos trabalhos:")
if colunas_existentes:
    for col in colunas_existentes[:3]:
        media = df_artigos_palavras[col].mean()
        print(f"      {col}: {media:.1f} palavras em média")

# ============================================================================
# PARTE 9: EXPORTAÇÃO DE TABELAS RESUMIDAS
# ============================================================================

print("\n" + "=" * 70)
print("EXPORTANDO TABELAS RESUMIDAS")
print("=" * 70)

# Tabela de áreas
tabela_areas.to_csv('resumo_areas_tematicas.csv', encoding='utf-8')
print("\n✓ Tabela salva: resumo_areas_tematicas.csv")

# Tabela de palavras-chave
top_100_palavras = df_palavras.nlargest(100, 'Frequencia')
top_100_palavras.to_csv('top_100_palavras_chave.csv', index=False, encoding='utf-8')
print("✓ Tabela salva: top_100_palavras_chave.csv")

# Resumo estatístico
resumo_stats = pd.DataFrame({
    'Métrica': [
        'Total de Trabalhos',
        'Áreas Temáticas',
        'Palavras Únicas',
        'Frequência Média de Palavras',
        'Classe Gramatical Predominante'
    ],
    'Valor': [
        total_trabalhos,
        areas_unicas,
        df_palavras['Palavra'].nunique(),
        f"{df_palavras['Frequencia'].mean():.2f}",
        df_palavras['Classe_Gramatical'].value_counts().index[0]
    ]
})

resumo_stats.to_csv('resumo_estatistico_geral.csv', index=False, encoding='utf-8')
print("✓ Tabela salva: resumo_estatistico_geral.csv")

print("\n" + "=" * 70)
print("ANÁLISE CONCLUÍDA COM SUCESSO!")
print("=" * 70)
print("\nArquivos gerados:")
print("   Gráficos: 01_*.png até 04_*.png")
print("   Tabelas: resumo_*.csv")
print("\nPróximos passos:")
print("   1. Revisar os gráficos e tabelas gerados")
print("   2. Interpretar os resultados obtidos")
print("   3. Integrar as análises no artigo científico")
print("=" * 70)
