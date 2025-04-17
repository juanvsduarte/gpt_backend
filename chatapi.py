import time
from flask import Flask, request, jsonify
from openai import OpenAI
from credentials import api_key, assistant_id  # Importa a chave da API e o assistant_id
from createThreads import thread_id  # ID da thread onde o chat ocorrerá
from flask_cors import CORS

# Configuração do cliente OpenAI com a chave de API
client = OpenAI(api_key=api_key)

app = Flask(__name__)
CORS(app)


# Rota para o endpoint de chat
@app.route('/chat', methods=['POST'])
def chat():
    # Obtém a pergunta do corpo da requisição JSON
    dados = request.get_json()
    pergunta = dados.get("pergunta", "")

    if not pergunta:
        return jsonify({"erro": "Pergunta não fornecida"}), 400

    # Adiciona a mensagem do usuário à Thread
    mensagem_thread = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=pergunta
    )

    # Inicia um Run para o Assistente processar a mensagem na Thread
    meu_run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Verifica periodicamente o status do Run até ser concluído
    while meu_run.status in ["queued", "in_progress"]:
        resultado_run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=meu_run.id
        )

        if resultado_run.status == "completed":
            # Recupera todas as mensagens da Thread, incluindo a resposta do Assistente
            todas_mensagens = client.beta.threads.messages.list(
                thread_id=thread_id
            )

            # Encontra a última mensagem do assistente na lista de mensagens
            resposta = next(
                (msg.content[0].text.value for msg in todas_mensagens.data if msg.role == "assistant"),
                "Nenhuma resposta disponível."
            )
            return jsonify({"resposta": resposta})

        elif resultado_run.status == "queued" or resultado_run.status == "in_progress":
            time.sleep(2)  # Aguarda 2 segundos antes de verificar novamente

    return jsonify({"erro": "Não foi possível obter a resposta"}), 500


# Inicia o servidor Flask na porta 5001
if __name__ == '__main__':
    app.run(debug=True, port=5001)

