import os
import time
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = "https://eventos.ifnmg.edu.br/sic2025/anais/"
PASTA = "pdfs"

os.makedirs(PASTA, exist_ok=True)

options = webdriver.ChromeOptions()

# Evita abrir PDF embutido
prefs = {
    "plugins.always_open_pdf_externally": False
}

options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

driver.get(URL)

time.sleep(5)

# Botões de download PDF
seletor = (
    "button."
    "MuiButton-containedSecondary."
    "css-1vlrefx"
)

botoes = driver.find_elements(By.CSS_SELECTOR, seletor)

print(f"Encontrados {len(botoes)} PDFs")

aba_principal = driver.current_window_handle


def salvar_blob(nome):
    script = """
    const url = window.location.href;

    return fetch(url)
      .then(r => r.blob())
      .then(blob => new Promise(resolve=>{
          const reader = new FileReader();

          reader.onloadend = () => {
              resolve(reader.result.split(',')[1]);
          };

          reader.readAsDataURL(blob);
      }));
    """

    conteudo = driver.execute_async_script("""
        const callback = arguments[arguments.length - 1];

        const url = window.location.href;

        fetch(url)
        .then(r=>r.blob())
        .then(blob=>{
            const reader = new FileReader();

            reader.onloadend=()=>{
                callback(reader.result.split(',')[1]);
            }

            reader.readAsDataURL(blob);
        });
    """)

    caminho = os.path.join(PASTA, nome)

    with open(caminho, "wb") as f:
        f.write(base64.b64decode(conteudo))

    print(f"Salvo: {nome}")


for i in range(len(botoes)):

    driver.switch_to.window(aba_principal)

    botoes = driver.find_elements(By.CSS_SELECTOR, seletor)

    try:

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            botoes[i]
        )

        time.sleep(1)

        driver.execute_script(
            "arguments[0].click();",
            botoes[i]
        )

        time.sleep(4)

        janelas = driver.window_handles

        if len(janelas) > 1:

            driver.switch_to.window(janelas[-1])

            wait.until(
                lambda d: d.current_url.startswith("blob:")
            )

            salvar_blob(f"artigo_{i+1:03}.pdf")

            driver.close()

    except Exception as e:
        print(f"Erro no PDF {i+1}: {e}")

driver.switch_to.window(aba_principal)
driver.quit()

print("Concluído.")