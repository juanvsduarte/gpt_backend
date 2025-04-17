import os
import json
import requests
import concurrent.futures

# Configurações de autenticação (substitua pelos seus dados se necessário)
AUTH_URL = 'https://accounts.zoho.com/oauth/v2/token'
REFRESH_TOKEN = '1000.b507c93e165827432b3946f4b10c3e92.b7a23e26c1c1e1c8bdfa5830335b4116'
CLIENT_ID = '1000.U11OPPS6O3K37Z22ZT29O4TSVTEYYN'
CLIENT_SECRET = 'd62975aa3ec9bbdc5e039c16a29cc21cf8db70170c'
GRANT_TYPE = 'refresh_token'
SCOPE = 'Desk.search.READ,Desk.tickets.READ,Desk.settings.READ,Desk.basic.READ,Desk.contacts.READ'

# Headers e cookies podem ser necessários conforme o exemplo curl (ajuste se precisar)
AUTH_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '_zcsr_tmp=14277a91-f195-4bb0-bb83-a762191c2e35; iamcsr=14277a91-f195-4bb0-bb83-a762191c2e35; zalb_b266a5bf57=9f371135a524e2d1f51eb9f41fa26c60'
}

# Função para obter o access token
def get_access_token():
    payload = {
        'refresh_token': REFRESH_TOKEN,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
        'scope': SCOPE
    }
    response = requests.post(AUTH_URL, headers=AUTH_HEADERS, data=payload)
    response.raise_for_status()
    token_data = response.json()
    return token_data['access_token']

# Função para coletar os IDs dos tickets via paginação
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
        r = requests.get(base_url, headers=headers, params=params)
        print(f"Requisição GET para {r.url} retornou status code {r.status_code}")
        
        if r.status_code != 200:
            print("Erro na requisição:", r.text)
            break

        if not r.text.strip():
            print("Resposta vazia recebida.")
            break

        try:
            data = r.json()
        except Exception as e:
            print("Erro ao decodificar JSON:", e)
            print("Conteúdo da resposta:", r.text)
            break

        tickets = data.get('data', [])
        if not tickets:
            break

        for ticket in tickets:
            ticket_ids.append(ticket.get('id'))
        start += limit

    return ticket_ids

# Função para obter detalhes de um ticket específico
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

# Função para salvar tickets com resolução em um arquivo JSON
def save_tickets_with_resolution(tickets_list, output_file):
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tickets_list, f, ensure_ascii=False, indent=4)

def main():
    try:
        print("Obtendo access token...")
        access_token = get_access_token()
        print("Token obtido com sucesso.")

        print("Coletando IDs de tickets...")
        ticket_ids = get_all_ticket_ids(access_token)
        print(f"Foram encontrados {len(ticket_ids)} tickets.")

        tickets_with_resolution = []

        # Função auxiliar para processar cada ticket
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
                print(f"Erro ao consultar ticket {ticket_id}: {e}")
            return None

        # Executa até 25 requisições em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(process_ticket, tid) for tid in ticket_ids]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    tickets_with_resolution.append(result)

        output_file = os.path.join('GPT/archives', 'tickets.json')
        save_tickets_with_resolution(tickets_with_resolution, output_file)
        print(f"Tickets com resolução salvos em {output_file}")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == '__main__':
    main()
