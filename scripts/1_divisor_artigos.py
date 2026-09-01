import re
import unicodedata
from pathlib import Path
from pypdf import PdfReader, PdfWriter


# -------------------------------------------------------
# UTILIDADES
# -------------------------------------------------------

def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ASCII", "ignore").decode("ASCII")
    return texto.lower()


def extrair_texto(reader, pagina):
    try:
        texto = reader.pages[pagina].extract_text()
        return texto or ""
    except:
        return ""


def remover_cabecalho(texto):
    linhas = texto.split("\n")

    novas = []

    for linha in linhas:

        if "SEMINÁRIO DE INICIAÇÃO CIENTÍFICA" in linha.upper():
            continue

        if "ISBN" in linha.upper():
            continue

        novas.append(linha)

    return "\n".join(novas)


# -------------------------------------------------------
# DETECÇÃO DE TÍTULO
# -------------------------------------------------------

def primeira_linha(texto):

    for linha in texto.split("\n"):

        linha = linha.strip()

        if len(linha) > 10:
            return linha

    return ""


def titulo_maiusculo(linha):

    letras = [c for c in linha if c.isalpha()]

    if len(letras) < 15:
        return False

    maiusculas = sum(c.isupper() for c in letras)

    return maiusculas / len(letras) > 0.80


# -------------------------------------------------------
# SCORE DE INÍCIO
# -------------------------------------------------------

def score_inicio(texto):

    texto = remover_cabecalho(texto)

    texto_norm = normalizar(texto)

    score = 0

    linha = primeira_linha(texto)

    if titulo_maiusculo(linha):
        score += 40

    if "introducao" in texto_norm:
        score += 25

    if "palavras chave" in texto_norm:
        score += 20

    if "palavras-chave" in texto_norm:
        score += 20

    if "keywords" in texto_norm:
        score += 20

    if "abstract" in texto_norm:
        score += 10

    if re.search(r"\bdiscente", texto_norm):
        score += 10

    if re.search(r"\bdocente", texto_norm):
        score += 10

    if re.search(r"\buniversidade", texto_norm):
        score += 5

    if re.search(r"\bcampus\b", texto_norm):
        score += 5

    return score


# -------------------------------------------------------
# LOCALIZA INÍCIOS
# -------------------------------------------------------

def localizar_inicios(pdf):

    reader = PdfReader(pdf)

    inicios = []

    for pagina in range(len(reader.pages)):

        texto = extrair_texto(reader, pagina)

        score = score_inicio(texto)

        print(f"Página {pagina+1} -> score {score}")

        if score >= 60:
            inicios.append(pagina)

    return inicios


# -------------------------------------------------------
# AGRUPA ARTIGOS
# -------------------------------------------------------

def agrupar_artigos(pdf):

    reader = PdfReader(pdf)

    total = len(reader.pages)

    inicios = localizar_inicios(pdf)

    artigos = []

    for i, inicio in enumerate(inicios):

        if i == len(inicios) - 1:
            fim = total - 1
        else:
            fim = inicios[i + 1] - 1

        artigos.append(list(range(inicio, fim + 1)))

    return artigos


# -------------------------------------------------------
# EXTRAI TÍTULO
# -------------------------------------------------------

def titulo_artigo(reader, pagina):

    texto = extrair_texto(reader, pagina)

    texto = remover_cabecalho(texto)

    titulo = primeira_linha(texto)

    titulo = re.sub(r'[\\/*?:"<>|]', "", titulo)

    return titulo[:120]


# -------------------------------------------------------
# SALVAR
# -------------------------------------------------------

def salvar(pdf, artigos):

    reader = PdfReader(pdf)

    pasta = Path("artigos")

    pasta.mkdir(exist_ok=True)

    for numero, paginas in enumerate(artigos, 1):

        writer = PdfWriter()

        for p in paginas:
            writer.add_page(reader.pages[p])

        titulo = titulo_artigo(reader, paginas[0])

        nome = f"{numero:03d} - {titulo}.pdf"

        with open(pasta / nome, "wb") as f:
            writer.write(f)

        print(
            f"Artigo {numero}: páginas {paginas[0]+1}-{paginas[-1]+1}"
        )


# -------------------------------------------------------
# EXECUÇÃO
# -------------------------------------------------------

if __name__ == "__main__":

    pdf = "/home/suzanamota/Documentos/sic/resumos_sic/2021/Anais do SIC 2021-9-1227.pdf"

    artigos = agrupar_artigos(pdf)

    print()

    print("Artigos encontrados:", len(artigos))

    salvar(pdf, artigos)