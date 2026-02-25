import json
import zmq

# cria contexto e socket REP (responder)
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("[SERVER] Servidor de tarefas iniciado em tcp://*:5555", flush=True)

# dicionário: client_id -> lista de tarefas
tasks_by_client = {}

while True:
    # 1) recebe mensagem como string (JSON)
    raw_message = socket.recv_string()
    print(f"[SERVER] Mensagem recebida: {raw_message!r}", flush=True)

    # 2) tenta converter JSON para dicionário
    try:
        request = json.loads(raw_message)
    except json.JSONDecodeError:
        response = {
            "status": "error",
            "message": "JSON inválido recebido pelo servidor."
        }
        socket.send_string(json.dumps(response))
        continue

    client_id = request.get("client_id", "default")
    action = request.get("action")

    # garante que exista uma lista de tarefas para esse cliente
    tasks = tasks_by_client.setdefault(client_id, [])

    # 3) trata as ações
    if action == "add":
        task_text = (request.get("task") or "").strip()
        if not task_text:
            response = {
                "status": "error",
                "message": "Tarefa vazia não pode ser adicionada."
            }
        else:
            tasks.append(task_text)
            response = {
                "status": "ok",
                "message": "Tarefa adicionada com sucesso.",
                "tasks": tasks,
            }

    elif action == "list":
        response = {
            "status": "ok",
            "message": f"{len(tasks)} tarefa(s) encontrada(s).",
            "tasks": tasks,
        }

    elif action == "remove":
        index = request.get("index")
        try:
            idx = int(index) - 1  # usuário manda 1-based
            if idx < 0 or idx >= len(tasks):
                response = {
                    "status": "error",
                    "message": "Índice de tarefa inválido."
                }
            else:
                removed = tasks.pop(idx)
                response = {
                    "status": "ok",
                    "message": f"Tarefa removida: {removed}",
                    "tasks": tasks,
                }
        except (TypeError, ValueError):
            response = {
                "status": "error",
                "message": "Índice de tarefa inválido (não é número)."
            }

    else:
        response = {
            "status": "error",
            "message": f"Ação desconhecida: {action!r}."
        }

    # 4) envia a resposta como JSON
    socket.send_string(json.dumps(response))
