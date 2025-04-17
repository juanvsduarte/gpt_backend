import os
import requests
import json
from datetime import datetime
from credentials import api_key

# ===== CONFIGURAÇÕES INICIAIS =====
headers_beta = {
    "Authorization": f"Bearer {api_key}",
    "OpenAI-Beta": "assistants=v2"
}

# ===== PASSO 1: USAR ARQUIVOS JÁ UPLOADADOS =====
# Lista de file IDs já enviados com purpose "assistants"
uploaded_file_ids = [
    "file-VbSUWHbs8gmxQ5jPdHJh8KXW",
    "file-FT6385Pe7gIJSTqXIwLxZjeZ",
    "file-QVw0ziA0pR37Jh9pPGog4fC1",
    "file-wjTebfUlGGTVgAB7yaKSwaKT",
    "file-oveVGUuNwAoGT1gN69JYq9a7",
    "file-LqjmVnud8xfT7kg3rv16oZhV",
    "file-ZzFbohQoqh4W6LdmUgyNgF2U",
    "file-KEFLiSOSZbNs0gN4xgIXICAA",
    "file-Dr3yuY1aVe8aCwIFQV8f666G",
    "file-VAi81fin1iOL3FwvvKkoA2jz",
    "file-Q2MVQs8UYYmaUlvl3KmDiGXB",
    "file-Ccy3Y2oIwnc3ANm49teGOSai",
    "file-AyftOz1QRday566s5cJoz630",
    "file-JB3KbXJbBKfpXxm5UL0uT2FU",
    "file-TSaejDI1pSheD0plWNKS9CHi",
    "file-IRdcZKunXOmPCWtjrBWFWAmC",
    "file-sY40VZezGu73qdbkOwk4V2vJ",
    "file-bvZWOFoVzdpWoUU31aLerKCR",
    "file-fkLsEttSu0EEUuHAkFWloKee",
    "file-4yZmKB9tzMJz2rDubE6xO2Uo",
    "file-XBzSgdlCrGFz7C338mMpClRO",
    "file-tHAvp9PEG7gOoEos2yfuRsEC",
    "file-C26CCkG879eNGeX4RYrBySlh",
    "file-JmFgiWc4zy34MkFRhKKGUrHS",
    "file-M7QN6kmDL2MShrqibjhMrI98",
    "file-VHVJNUiiqWGfzGbYj4vpyNwk",
    "file-lOaXxQ3ej7rnYJkcV9UitzYF",
    "file-SQoTxXjasVdzMCNyZ0iYOdm3",
    "file-XnVLin15K0UjnFTElm3psRw2",
    "file-SaQ9tyciXVLNYTvWSIv73mwn",
    "file-Iy0UazeTXWn0XcVASFMYweoh",
    "file-mHVCuz4o7tnZl47kU1daX2hM",
    "file-wAxwUMLCZ5SsoAWwZkEVbKVV",
    "file-i1eK7bHU6DmO94r1RFfijuK3",
    "file-ryJWcZGiPGZaawmLeD2eKD0h",
    "file-Jiqw3izaq03QN9FJGqvuetiN",
    "file-db30lRHTG051rDtOtXoKsoAu",
    "file-PaTqdbA2ocCuAUL7QMk7trsm",
    "file-xt2RZ9ZzbILhQ23nygkYY6TQ",
    "file-WTlo9QVIDLc96yf6B7c608p8",
    "file-DpwkYg04pavZpI8JyMglO7Dn",
    "file-eoWblypAeA3ogd3rw8GRA7lp",
    "file-kt2ruqRbKVKiDvZQWhYOfida",
    "file-TMQEZTr8I8OkpFOiAhdeWy6p",
    "file-pwhl4jQdeWDBNmGLpg8NqdxS",
    "file-bbWNXF5daBvYjEanzWYwO9A1",
    "file-sgc9Qa0hsje7gEE8Y5r2Yz6T",
    "file-Gdbh9jDUN2JLoAZ2F7szIQpy",
    "file-vo1sR3RphROIzYkahNNyOZfu",
    "file-X1C0wBEWIf4i3Xi6kVaiOnni",
    "file-UOT0rWq1D1MOCRxeWSJRAMVj",
    "file-nyG1lRdpu0Czn3NQhvj1mgKu",
    "file-lxoK1U3HFqnS54UdBmVm0Usx",
    "file-SvoaJyq3fS9PqVjkxG0faN8b",
    "file-c2tkmcqx5MvUZFwADJbdM7dq",
    "file-73lDBvD1kWASUHWrYSyGhjZX",
    "file-eaWBTrWlSI8hZr1Ax7kJI1He",
    "file-MKfhlbJIDB2ul1ugC4ODO7As",
    "file-VEkziDGnJ8Ngukq7EeYetOEM",
    "file-N34hrPEbdLsC1nBVJtXmDrzg",
    "file-F2GWnRaNMmyKEyS5vRixRh6Z",
    "file-fxDmo98K4MIl4t1UcFGjRUu9",
    "file-ToFhDsajs8CjsNGJcPMADfPf",
    "file-u0FPshzKft2IZKBmpjqVdATc",
    "file-1nH5Z2mOBCLfABQnk4iyQBs0",
    "file-KLlh8ZWogWaJLNkuwBqotINR",
    "file-WofSGNU0XNS8wh68TI7mYnoi",
    "file-ImoZv3oG7tGIALIHUWJAOpMR",
    "file-ToPXRtduAdoFp2pQwDhRcZU0",
    "file-RrYuBLZWqea1vd9Fa3IWQFhK",
    "file-QZwaaYjSXBr7wL71Ec0g64F7",
    "file-fnxbowrcSaSFsDE5eZedh3Y8",
    "file-ZkyyYaC8Ous5szqZ1eoJFtHR",
    "file-z6SQAOt0RR5MVTxPmAEsrOG8",
    "file-19fpSANk8VQxp6oEJfJbp0FR",
    "file-chq256OCWDX4pZDx4B8iGiCr",
    "file-pGTwqfsz17ozNyiy0g3z6vWR",
    "file-IuVeDdE5v6Hv75Pxh3QpfrSh",
    "file-muSMjeVsiHS2i1CU5jFVpPEL",
    "file-dnpspC5qUM43Oiii2QVg1OWm",
    "file-DDO1PLVQqgmbOpsp2VAOlY27",
    "file-nKQpp1BL7Vkx6ahzObfjOgUT",
    "file-utmwbJransLlYIZ1CS3uLkHj",
    "file-Jzbl9rLw2Bih6nfRzX7PhxEz",
    "file-5Xu8WCOJTeDmJAk1jqahK9tG",
    "file-veAbQ9r5hooHbyBKgX8l8tK0",
    "file-uWrJYmoWV9ixPRyQNFmzGbdx",
    "file-Xs8OH74vc4d3T6qTI2bsRiXz",
    "file-9NALLZUGnSrHp1vpYvwS6OI3",
    "file-k3WkbRZP83S3f2Y1q7VrzYOX",
    "file-YybK1dntGChBgemKlrXRlHYg",
    "file-lwRRnZ9O8LkKRb1AcadB2wHv",
    "file-I06ayWlxrWjgdNOSF3PGv5Oj",
    "file-tudDdM7RHUkjsJgIeUMzRO4L",
    "file-tUzoKmXYWz308h5Yvkdb87Pu"
]

# ===== PASSO ADICIONAL: UPLOAD DOS ARQUIVOS .json DA PASTA /archives =====
archives_folder = "GPT/archives"
if os.path.isdir(archives_folder):
    for filename in os.listdir(archives_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(archives_folder, filename)
            with open(file_path, "rb") as f:
                files = {"file": f}
                data = {"purpose": "assistants"}
                response = requests.post("https://api.openai.com/v1/files",
                                         headers={"Authorization": f"Bearer {api_key}"},
                                         data=data,
                                         files=files)
            if response.ok:
                result = response.json()
                file_id = result["id"]
                uploaded_file_ids.append(file_id)
                print(f"Arquivo '{file_path}' enviado com sucesso. File ID: {file_id}")
            else:
                print(f"Erro ao enviar o arquivo '{file_path}':", response.text)
else:
    print(f"Pasta '{archives_folder}' não encontrada.")

# Limita o número de file_ids para no máximo 100, conforme exigido pela API
if len(uploaded_file_ids) > 100:
    print(f"A lista de file_ids contém {len(uploaded_file_ids)} itens, que excede o máximo permitido. Usando apenas os primeiros 100 IDs.")
    uploaded_file_ids = uploaded_file_ids[:100]

# ===== PASSO 2: CRIAÇÃO DO VECTOR STORE =====
vector_store_url = "https://api.openai.com/v1/vector_stores"
# Define o nome do vector store como o timestamp atual
vector_store_name = datetime.now().strftime("%Y%m%d_%H%M%S")
vector_payload = {
    "file_ids": uploaded_file_ids,
    "name": vector_store_name
    # Outras propriedades, como chunking_strategy ou metadata, podem ser adicionadas se necessário
}

vector_response = requests.post(
    vector_store_url,
    headers={**headers_beta, "Content-Type": "application/json"},
    json=vector_payload
)

if vector_response.ok:
    vector_result = vector_response.json()
    vector_store_id = vector_result["id"]
    print(f"Vector store criado com sucesso. ID: {vector_store_id}")
else:
    print("Erro ao criar o vector store:", vector_response.text)
    exit(1)

# ===== PASSO 3: CRIAÇÃO DO ASSISTENTE LSBrain =====
assistant_url = "https://api.openai.com/v1/assistants"

instructions_text = (
    "A Lean Scheduling Brasil (LSB) é uma empresa brasileira especializada em soluções de planejamento e programação da produção para indústrias. "
    "Ela se destaca por aplicar princípios de Lean Manufacturing e ferramentas avançadas de otimização para ajudar empresas a melhorar o fluxo de produção, reduzir desperdícios e aumentar a eficiência. "
    "A LSB trabalha principalmente com ferramentas de Advanced Planning and Scheduling (APS) que facilitam o planejamento detalhado e a gestão de atividades nas linhas de produção, "
    "alinhando demanda e capacidade de forma otimizada. Eles oferecem serviços como consultoria, implementação de sistemas, treinamentos e softwares especializados em Lean Manufacturing, "
    "especialmente em setores que têm alta variabilidade e demanda por personalização na produção, como o automotivo, metalúrgico, alimentício e outros. "
    "Com essas soluções, a Lean Scheduling Brasil ajuda empresas a melhorar a eficiência operacional e, ao mesmo tempo, a adotar uma filosofia de melhoria contínua. "
    "Dentro da LSB, temos uma área de Customer Success, onde os clientes recorrem para solucionar problemas e implementar melhorias em suas soluções, através da abertura de tickets no Zoho Desk. "
    "Nesta área atuam consultores, em sua maioria, mais juniors, que não possuem tanta experiência. Para auxiliá-los a ter um melhor direcionamento acerca do caminho para o desenvolvimento de um Ticket, "
    "estamos criando um assistente que, com base no histórico de tickets e documentações técnicas das soluções, sugere um caminho inicial para o atendimento da demanda. "
    "O assistente será implementado dentro das extensões do Zoho Desk e será acionado pelos consultores para direcionamento do desenvolvimento do Ticket. "
    "Como resposta, esperamos que o assistente informe de forma resumida o assunto do ticket exibido na tela e qual a forma ideal de resolução do mesmo, apontando em quais partes da solução devemos atuar, "
    "com base nas documentações técnicas fornecidas. "
    "Como limitações, o assistente deve evitar a consulta em tickets que não tenham resolução. "
    "O assistente deve ter uma linguagem amigável, com um tom mais técnico quando necessário. "
    "O nome do assistente será LSBrain. "
    "Deve sempre buscar referência primeiro nos arquivos fornecidos. "
    "Sempre que possivel busque uma solução no arquivo tickets.json"
    "Exemplo de Interação: "
    "O Ticket #0001 foi aberto pelo cliente X e precisamos solucioná-lo. "
    "Consultor pergunta ao assistente: 'Como podemos resolver o chamado #0001, com o assunto \"Incluir campo de atributo no relatório de carregamento por recurso\"?' "
    "Assistente responde: 'Para resolver o chamado, é necessário trazer o atributo para a tabela de ordens, incluí-la na procedure no SQL e incluir o campo no report builder.'"
   
)

assistant_payload = {
    "model": "gpt-4o",  # Substitua pelo modelo desejado
    "name": "LSBrain",
    "instructions": instructions_text,
    "tools": [
        {"type": "file_search"}
    ],
    "tool_resources": {
        "file_search": {
            "vector_store_ids": [vector_store_id]
        }
    },
    "temperature": 1,
    "top_p": 1
}

assistant_response = requests.post(
    assistant_url,
    headers={**headers_beta, "Content-Type": "application/json"},
    json=assistant_payload
)

if assistant_response.ok:
    assistant_result = assistant_response.json()
    print("Assistente LSBrain criado com sucesso!")
    print(json.dumps(assistant_result, indent=2))
else:
    print("Erro ao criar o assistente:", assistant_response.text)
