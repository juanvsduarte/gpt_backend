import os
import json
import time
import requests
import concurrent.futures
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Credenciais OpenAI
API_KEY = os.getenv("OPENAI_API_KEY")

# Credenciais Zoho
ZOHO_AUTH_URL = 'https://accounts.zoho.com/oauth/v2/token'
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_GRANT_TYPE = 'refresh_token'
ZOHO_SCOPE = 'Desk.search.READ,Desk.tickets.READ,Desk.settings.READ,Desk.basic.READ,Desk.contacts.READ'
ZOHO_AUTH_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '_zcsr_tmp=14277a91-f195-4bb0-bb83-a762191c2e35; iamcsr=14277a91-f195-4bb0-bb83-a762191c2e35; zalb_b266a5bf57=9f371135a524e2d1f51eb9f41fa26c60'
}

# Lista de file IDs pré-carregados (usados no assistente)
PRE_UPLOADED_FILE_IDS = [
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
    "file-Xs8OH74vc4d3T6qTI2bsRiXz"
]

# Variáveis globais para controle de atualização
is_updating = False
last_update_time = None
update_thread = None

# --------------------------
# Funções para Coleta de Tickets (Zoho Desk)
# --------------------------
def get_access_token():
    payload = {
        'refresh_token': ZOHO_REFRESH_TOKEN,
        'client_id': ZOHO_CLIENT_ID,
        'client_secret': ZOHO_CLIENT_SECRET,
        'grant_type': ZOHO_GRANT_TYPE,
        'scope': ZOHO_SCOPE
    }
    response = requests.post(ZOHO_AUTH_URL, headers=ZOHO_AUTH_HEADERS, data=payload, timeout=3000)
    response.raise_for_status()
    token_data = response.json()
    return token_data['access_token']

def get_all_ticket_ids(access_token):
    ticket_ids = []
    base_url = 'https://desk.zoho.com/api/v1/tickets'
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json',
        'Cookie': 'JSESSIONID=121F3ACCC2A05FEC24AF8B8F58218A31; _zcsr_tmp=ae21a45a-077f-427e-873a-9d53b54a66a2; crmcsr=ae21a45a-077f-427e-873a-9d53b54a66a2; zalb_9a26c99460=84b5a076da4ea1ba0b64a38c8fd681c6'
    }
    start = 0
    limit = 100
    while True:
        params = {'from': start, 'limit': limit}
        r = requests.get(base_url, headers=headers, params=params, timeout=3000)
        print(f"GET {r.url} status: {r.status_code}")
        if r.status_code != 200 or not r.text.strip():
            break
        data = r.json()
        tickets = data.get('data', [])
        if not tickets:
            break
        for ticket in tickets:
            ticket_ids.append(ticket.get('id'))
        start += limit
    return ticket_ids

def get_ticket_detail(ticket_id, access_token):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}'
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json',
        'Cookie': 'JSESSIONID=121F3ACCC2A05FEC24AF8B8F58218A31; _zcsr_tmp=ae21a45a-077f-427e-873a-9d53b54a66a2; crmcsr=ae21a45a-077f-427e-873a-9d53b54a66a2; zalb_9a26c99460=84b5a076da4ea1ba0b64a38c8fd681c6'
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def extract_tickets():
    print("Obtendo access token do Zoho...")
    access_token = get_access_token()
    print("Token obtido.")
    print("Coletando IDs dos tickets...")
    ticket_ids = get_all_ticket_ids(access_token)
    print(f"Encontrados {len(ticket_ids)} tickets.")
    tickets_with_resolution = []

    def process_ticket(ticket_id):
        print(f"Consultando ticket {ticket_id}...")
        try:
            detail = get_ticket_detail(ticket_id, access_token)
            if detail.get('resolution'):
                return {
                    'ticketNumber': detail.get('ticketNumber'),
                    'subject': detail.get('subject'),
                    'resolution': detail.get('resolution'),
                    'description': detail.get('description'),
                    'webUrl': detail.get('webUrl')
                }
        except Exception as e:
            print(f"Erro no ticket {ticket_id}: {e}")
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(process_ticket, tid) for tid in ticket_ids]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                tickets_with_resolution.append(result)
    output_dir = "GPT/archives"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "tickets.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tickets_with_resolution, f, ensure_ascii=False, indent=4)
    print(f"Tickets salvos em {output_file}")

def get_all_archived_ticket_ids(access_token):
    archived_ticket_ids = []
    base_url = 'https://desk.zoho.com/api/v1/tickets/archivedTickets'
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json',
        'Cookie': 'JSESSIONID=121F3ACCC2A05FEC24AF8B8F58218A31; _zcsr_tmp=ae21a45a-077f-427e-873a-9d53b54a66a2; crmcsr=ae21a45a-077f-427e-873a-9d53b54a66a2; zalb_9a26c99460=84b5a076da4ea1ba0b64a38c8fd681c6'
    }
    start = 0
    limit = 100
    while True:
        params = {'from': start, 'limit': limit, 'departmentId': '358470000000006907'}
        r = requests.get(base_url, headers=headers, params=params, timeout=3000)
        print(f"GET {r.url} status: {r.status_code}")
        if r.status_code != 200 or not r.text.strip():
            break
        data = r.json()
        tickets = data.get('data', [])
        if not tickets:
            break
        for ticket in tickets:
            archived_ticket_ids.append(ticket.get('id'))
        start += limit
    return archived_ticket_ids

def get_archived_ticket_detail(ticket_id, access_token):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}'

    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json',
        'Cookie': 'JSESSIONID=121F3ACCC2A05FEC24AF8B8F58218A31; _zcsr_tmp=ae21a45a-077f-427e-873a-9d53b54a66a2; crmcsr=ae21a45a-077f-427e-873a-9d53b54a66a2; zalb_9a26c99460=84b5a076da4ea1ba0b64a38c8fd681c6'
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def extract_archived_tickets():
    print("Obtendo access token do Zoho para archivedtickets...")
    access_token = get_access_token()
    print("Token obtido.")
    print("Coletando IDs dos archived tickets...")
    archived_ticket_ids = get_all_archived_ticket_ids(access_token)
    print(f"Encontrados {len(archived_ticket_ids)} archived tickets.")
    archived_tickets_with_resolution = []

    def process_archived_ticket(ticket_id):
        print(f"Consultando archived ticket {ticket_id}...")
        try:
            detail = get_archived_ticket_detail(ticket_id, access_token)
            if detail.get('resolution'):
                return {
                    'ticketNumber': detail.get('ticketNumber'),
                    'subject': detail.get('subject'),
                    'resolution': detail.get('resolution'),
                    'description': detail.get('description'),
                    'webUrl': detail.get('webUrl')
                }
        except Exception as e:
            print(f"Erro no archived ticket {ticket_id}: {e}")
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(process_archived_ticket, tid) for tid in archived_ticket_ids]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                archived_tickets_with_resolution.append(result)
    
    output_dir = "GPT/archives"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "archivedtickets.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(archived_tickets_with_resolution, f, ensure_ascii=False, indent=4)
    print(f"Archived tickets salvos em {output_file}")

# --------------------------
# Função para Deletar Recursos Existentes
# --------------------------
def delete_assistant(assistant_id):
    delete_url = f"https://api.openai.com/v1/assistants/{assistant_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.delete(delete_url, headers=headers)
    if response.ok:
        print("Assistente deletado com sucesso!")
    else:
        print("Erro ao deletar assistente:", response.text)

def delete_vector_store(vector_store_id):
    delete_url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.delete(delete_url, headers=headers)
    if response.ok:
        print("Vector store deletado com sucesso!")
    else:
        print("Erro ao deletar vector store:", response.text)

def delete_existing_resources():
    # Verifica e deleta o assistente existente, se o arquivo existir
    assistant_file = "assistant_id.txt"
    if os.path.exists(assistant_file):
        with open(assistant_file, "r") as f:
            old_assistant = f.read().strip()
        if old_assistant:
            delete_assistant(old_assistant)
        os.remove(assistant_file)
    
    # Verifica e deleta o vector store existente, se o arquivo existir
    vector_store_file = "vector_store_id.txt"
    if os.path.exists(vector_store_file):
        with open(vector_store_file, "r") as f:
            old_vector = f.read().strip()
        if old_vector:
            delete_vector_store(old_vector)
        os.remove(vector_store_file)

# --------------------------
# Upload dos Arquivos (archives)
# --------------------------
def upload_archives():
    uploaded_file_ids = PRE_UPLOADED_FILE_IDS.copy()
    archives_folder = "GPT/archives"
    if os.path.isdir(archives_folder):
        for filename in os.listdir(archives_folder):
            if filename.endswith(".json"):
                file_path = os.path.join(archives_folder, filename)
                with open(file_path, "rb") as f:
                    files = {"file": f}
                    data = {"purpose": "assistants"}
                    response = requests.post("https://api.openai.com/v1/files",
                                             headers={"Authorization": f"Bearer {API_KEY}"},
                                             data=data,
                                             files=files)
                if response.ok:
                    result = response.json()
                    file_id = result["id"]
                    uploaded_file_ids.append(file_id)
                    print(f"Arquivo '{file_path}' enviado. File ID: {file_id}")
                else:
                    print(f"Erro ao enviar '{file_path}':", response.text)
    else:
        print(f"Pasta '{archives_folder}' não encontrada.")
    if len(uploaded_file_ids) > 100:
        print("Mais de 100 arquivos, usando os primeiros 100 IDs.")
        uploaded_file_ids = uploaded_file_ids[:100]
    return uploaded_file_ids

# --------------------------
# Criação do Vector Store e Assistente LSBrain
# --------------------------
def create_vector_store(file_ids):
    vector_store_url = "https://api.openai.com/v1/vector_stores"
    vector_store_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    vector_payload = {
        "file_ids": file_ids,
        "name": vector_store_name
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    response = requests.post(vector_store_url, headers=headers, json=vector_payload)
    if response.ok:
        result = response.json()
        vector_store_id = result["id"]
        print(f"Vector store criado. ID: {vector_store_id}")
        # Salva o ID do vector store para futuras deleções
        with open("vector_store_id.txt", "w") as f:
            f.write(vector_store_id)
        return vector_store_id
    else:
        print("Erro ao criar vector store:", response.text)
        exit(1)

def create_assistant(vector_store_id):
    assistant_url = "https://api.openai.com/v1/assistants"
    instructions_text = (
        "A Lean Scheduling Brasil (LSB) é uma empresa brasileira especializada em soluções de planejamento e programação da produção para indústrias. "
        "Ela se destaca por aplicar princípios de Lean Manufacturing e ferramentas avançadas de otimização para ajudar empresas a melhorar o fluxo de produção, reduzir desperdícios e aumentar a eficiência. "
        "A LSB trabalha principalmente com ferramentas de Advanced Planning and Scheduling (APS) que facilitam o planejamento detalhado e a gestão de atividades nas linhas de produção, "
        "alinhando demanda e capacidade de forma otimizada. Eles oferecem serviços como consultoria, implementação de sistemas, treinamentos e softwares especializados em Lean Manufacturing, "
        "especialmente em setores que têm alta variabilidade e demanda por personalização na produção. "
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
        "Sempre que possivel busque uma solução no arquivo tickets.json. "
        "Exemplo de Interação: "
        "O Ticket #0001 foi aberto pelo cliente X e precisamos solucioná-lo. "
        "Consultor pergunta ao assistente: 'Como podemos resolver o chamado #0001, com o assunto \"Incluir campo de atributo no relatório de carregamento por recurso\"?' "
        "Assistente responde: 'Para resolver o chamado, é necessário trazer o atributo para a tabela de ordens, incluí-la na procedure no SQL e incluir o campo no report builder.'"
    )
    assistant_payload = {
        "model": "gpt-4o",
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
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    response = requests.post(assistant_url, headers=headers, json=assistant_payload)
    if response.ok:
        assistant_result = response.json()
        print("Assistente LSBrain criado com sucesso!")
        print(json.dumps(assistant_result, indent=2))
        new_assistant_id = assistant_result['id']
        # Salva o ID do assistente para futuras deleções
        with open("assistant_id.txt", "w") as f:
            f.write(new_assistant_id)
        return new_assistant_id
    else:
        print("Erro ao criar assistente:", response.text)
        exit(1)

# --------------------------
# Criação da Thread (para interação via Chat)
# --------------------------
def create_thread():
    thread_url = "https://api.openai.com/v1/threads"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    try:
        response = requests.post(thread_url, headers=headers)
        response.raise_for_status()
        thread_data = response.json()
        thread_id = thread_data['id']
        print("Thread criada. ID:", thread_id)
        return thread_id
    except Exception as e:
        print("Erro ao criar thread:", e)
        return None

# --------------------------
# Servidor Flask para API de Chat
# --------------------------

# Configuração da API Key do OpenAI

app = Flask(__name__)
CORS(app, resources={
    r"/chat": {
        "origins": [
            "https://desk.zoho.com",
            "https://*.zohocdn.com",
            "https://*.zohostatic.com",
            "https://lsbrain-api-esbzd8hychbsetc4.brazilsouth-01.azurewebsites.net"
        ],
        "methods": ["POST"],
        "allow_headers": ["Content-Type", "Accept", "X-Requested-With"],
        "supports_credentials": True
    }
})

# Variáveis globais para armazenar thread e assistant IDs
global_thread_id = None
global_assistant_id = None  # Será definido após a criação do assistente

def background_update():
    global is_updating, last_update_time, global_assistant_id, global_thread_id
    while True:
        now = datetime.now()
        # Verifica se é meia-noite e ainda não atualizou hoje
        if now.hour == 0 and (last_update_time is None or (now - last_update_time).days >= 1):
            is_updating = True
            try:
                print("Iniciando atualização diária...")
                # Deleta os recursos existentes
                delete_existing_resources()
                # Processa os tickets ativos
                extract_tickets()
                # Processa os archived tickets
                extract_archived_tickets()
                # Envia os arquivos
                file_ids = upload_archives()
                # Cria novo vector store
                vector_store_id = create_vector_store(file_ids)
                # Cria novo assistente
                global_assistant_id = create_assistant(vector_store_id)
                # Cria nova thread
                global_thread_id = create_thread()
                last_update_time = now
                print("Atualização diária concluída com sucesso!")
            except Exception as e:
                print(f"Erro durante a atualização: {str(e)}")
            finally:
                is_updating = False
        time.sleep(60)  # Verifica a cada minuto

@app.route('/chat', methods=['POST'])
def chat():
    global is_updating
    data = request.get_json()
    pergunta = data.get("pergunta", "")
    
    if not pergunta:
        return jsonify({"erro": "Pergunta não fornecida"}), 400
    
    if is_updating:
        return jsonify({
            "resposta": "O sistema está sendo atualizado com os dados mais recentes. Por favor, aguarde alguns minutos e tente novamente.",
            "status": "updating"
        })
    
    try:
        # Adiciona a mensagem do usuário na thread
        client.beta.threads.messages.create(
            thread_id=global_thread_id,
            role="user",
            content=pergunta
        )
        # Inicia um run para que o assistente processe a mensagem
        meu_run = client.beta.threads.runs.create(
            thread_id=global_thread_id,
            assistant_id=global_assistant_id
        )
        
        while meu_run.status in ["queued", "in_progress"]:
            resultado_run = client.beta.threads.runs.retrieve(
                thread_id=global_thread_id,
                run_id=meu_run.id
            )
            if resultado_run.status == "completed":
                todas_mensagens = client.beta.threads.messages.list(thread_id=global_thread_id)
                resposta = next(
                    (msg.content[0].text.value for msg in todas_mensagens.data if msg.role == "assistant"),
                    "Nenhuma resposta disponível."
                )
                return jsonify({"resposta": resposta, "status": "success"})
            elif resultado_run.status in ["queued", "in_progress"]:
                time.sleep(2)
        
        return jsonify({"erro": "Não foi possível obter a resposta"}), 500
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "success", "message": "API is running"})

# --------------------------
# Inicialização Única e Permanência Online
# --------------------------
def initialize_system():
    # Deleta os recursos existentes (assistente e vector store) se existirem
    delete_existing_resources()
    extract_tickets()            # Processa os tickets ativos
    extract_archived_tickets()   # Processa os archived tickets (integração igual ao endpoint tickets)
    file_ids = upload_archives() # Envia os arquivos da pasta GPT/archives (que conterá tickets.json e archivedtickets.json)
    vector_store_id = create_vector_store(file_ids)
    assistant_id = create_assistant(vector_store_id)
    thread_id = create_thread()
    return assistant_id, thread_id

if __name__ == '__main__':
    print("Inicializando sistema...")
    global_assistant_id, global_thread_id = initialize_system()
    print("Sistema inicializado com sucesso.")
    
    # Inicia a thread de atualização em background
    update_thread = threading.Thread(target=background_update)
    update_thread.daemon = True
    update_thread.start()
    
    # Inicia o servidor Flask
    app.run(debug=False, use_reloader=False)
 