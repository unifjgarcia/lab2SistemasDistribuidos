import json
import zmq

def send_request(socket, data: dict) -> dict:
    """Envia um dicionário como JSON e retorna a resposta (também dicionário)."""
    socket.send_string(json.dumps(data))
    raw = socket.recv_string()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"status": "error", "message": f"Resposta inválida do servidor: {raw!r}"}


def print_tasks(tasks):
    if not tasks:
        print("\n[CLIENT] Nenhuma tarefa cadastrada.\n")
        return

    print("\n[CLIENT] Suas tarefas:")
    for i, task in enumerate(tasks, start=1):
        print(f"  {i}. {task}")
    print()


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    # nome "servidor" é o service name do docker-compose
    socket.connect("tcp://servidor:5555")

    # poderia ser seu RA, por exemplo; aqui deixei fixo
    client_id = "cliente-1"
    print(f"[CLIENT] Conectado ao servidor como {client_id}\n")

    while True:
        print("===== GERENCIADOR DE TAREFAS =====")
        print("1 - Adicionar tarefa")
        print("2 - Listar tarefas")
        print("3 - Remover tarefa")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            descricao = input("Digite a descrição da tarefa: ").strip()
            req = {
                "client_id": client_id,
                "action": "add",
                "task": descricao,
            }
            resp = send_request(socket, req)
            print(f"\n[SERVER] {resp.get('message')}")
            if resp.get("status") == "ok":
                print_tasks(resp.get("tasks", []))

        elif opcao == "2":
            req = {
                "client_id": client_id,
                "action": "list",
            }
            resp = send_request(socket, req)
            print(f"\n[SERVER] {resp.get('message')}")
            if resp.get("status") == "ok":
                print_tasks(resp.get("tasks", []))

        elif opcao == "3":
            # primeiro pega a lista atual pra mostrar pro usuário
            req_list = {
                "client_id": client_id,
                "action": "list",
            }
            resp_list = send_request(socket, req_list)
            if resp_list.get("status") != "ok":
                print(f"\n[SERVER] {resp_list.get('message')}\n")
                continue

            tasks = resp_list.get("tasks", [])
            print_tasks(tasks)

            index = input("Digite o número da tarefa a remover: ").strip()
            req = {
                "client_id": client_id,
                "action": "remove",
                "index": index,
            }
            resp = send_request(socket, req)
            print(f"\n[SERVER] {resp.get('message')}")
            if resp.get("status") == "ok":
                print_tasks(resp.get("tasks", []))

        elif opcao == "0":
            print("Encerrando cliente...")
            break

        else:
            print("Opção inválida, tente novamente.\n")


if __name__ == "__main__":
    main()
