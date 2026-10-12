"""
Gerenciador de Campeonato de Pontos Corridos
Disciplina: Paradigmas de Programação (UNAMA) - Atividade Avaliativa AV1

Programa em Python escrito no paradigma imperativo: uma sequência de
instruções que altera o estado de listas e dicionários por meio de
atribuições, decisões (if/elif/else), repetições (for/while) e funções.

Funcionalidades:
  - cadastro de times
  - registro de resultados (jogos de ida e volta)
  - tabela de classificação ordenada por critérios de desempate
  - listagem e busca de partidas
"""

import json

# ---------------------------------------------------------------------------
# Constantes (regras do campeonato)
# ---------------------------------------------------------------------------
ARQUIVO_DADOS = "dados_campeonato.json"
PONTOS_VITORIA = 3
PONTOS_EMPATE = 1


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def normalizar(texto):
    """Remove espaços extras e coloca em minúsculas, para comparar nomes."""
    return texto.strip().lower()


def ler_inteiro(mensagem):
    """Repete a leitura até o usuário digitar um inteiro maior ou igual a zero."""
    while True:
        entrada = input(mensagem).strip()
        if entrada.isdigit():
            return int(entrada)
        print("  Valor inválido. Digite um número inteiro maior ou igual a zero.")


def saldo_de_gols(time):
    """Saldo de gols = gols pró - gols contra."""
    return time["gp"] - time["gc"]


# ---------------------------------------------------------------------------
# Times
# ---------------------------------------------------------------------------
def buscar_time(times, nome):
    """Percorre a lista de times e devolve o dicionário do time, ou None."""
    alvo = normalizar(nome)
    for time in times:
        if normalizar(time["nome"]) == alvo:
            return time
    return None


def cadastrar_time(times, nome):
    """Cadastra um novo time com todas as estatísticas zeradas."""
    nome = nome.strip()
    if nome == "":
        return False, "O nome do time não pode ser vazio."
    if buscar_time(times, nome) is not None:
        return False, f"O time '{nome}' já está cadastrado."

    novo_time = {
        "nome": nome,
        "pj": 0,   # partidas jogadas
        "v": 0,    # vitórias
        "e": 0,    # empates
        "d": 0,    # derrotas
        "gp": 0,   # gols pró
        "gc": 0,   # gols contra
        "pts": 0,  # pontos
    }
    times.append(novo_time)
    return True, f"Time '{nome}' cadastrado com sucesso."


# ---------------------------------------------------------------------------
# Partidas
# ---------------------------------------------------------------------------
def atualizar_estatisticas(time, gols_pro, gols_contra):
    """Altera o estado do time (variáveis acumuladoras) após uma partida."""
    time["pj"] += 1
    time["gp"] += gols_pro
    time["gc"] += gols_contra

    if gols_pro > gols_contra:
        time["v"] += 1
        time["pts"] += PONTOS_VITORIA
    elif gols_pro == gols_contra:
        time["e"] += 1
        time["pts"] += PONTOS_EMPATE
    else:
        time["d"] += 1


def partida_ja_registrada(partidas, mandante, visitante):
    """Cada confronto (mandante x visitante) só pode ocorrer uma vez."""
    for partida in partidas:
        if partida["mandante"] == mandante and partida["visitante"] == visitante:
            return True
    return False


def registrar_resultado(times, partidas, nome_mandante, nome_visitante,
                        gols_mandante, gols_visitante):
    """Valida o confronto, guarda a partida e atualiza os dois times."""
    mandante = buscar_time(times, nome_mandante)
    visitante = buscar_time(times, nome_visitante)

    if mandante is None or visitante is None:
        return False, "Time não encontrado. Cadastre os dois times antes."
    if mandante is visitante:
        return False, "Um time não pode jogar contra ele mesmo."
    if partida_ja_registrada(partidas, mandante["nome"], visitante["nome"]):
        return False, "Esse confronto (com esse mando de campo) já foi registrado."

    partida = {
        "id": len(partidas) + 1,
        "mandante": mandante["nome"],
        "visitante": visitante["nome"],
        "gols_mandante": gols_mandante,
        "gols_visitante": gols_visitante,
    }
    partidas.append(partida)

    atualizar_estatisticas(mandante, gols_mandante, gols_visitante)
    atualizar_estatisticas(visitante, gols_visitante, gols_mandante)
    return True, "Resultado registrado e tabela atualizada."


def buscar_partidas(partidas, termo):
    """Devolve as partidas em que o termo aparece no nome de algum time."""
    termo = normalizar(termo)
    encontradas = []
    for partida in partidas:
        if termo in normalizar(partida["mandante"]) or \
           termo in normalizar(partida["visitante"]):
            encontradas.append(partida)
    return encontradas


def texto_partida(partida):
    return (f"#{partida['id']:>2}  {partida['mandante']} "
            f"{partida['gols_mandante']} x {partida['gols_visitante']} "
            f"{partida['visitante']}")


# ---------------------------------------------------------------------------
# Classificação
# ---------------------------------------------------------------------------
def vem_antes(a, b):
    """
    Critérios de classificação, nesta ordem:
    1) mais pontos  2) mais vitórias  3) maior saldo de gols
    4) mais gols pró  5) ordem alfabética
    """
    if a["pts"] != b["pts"]:
        return a["pts"] > b["pts"]
    if a["v"] != b["v"]:
        return a["v"] > b["v"]
    if saldo_de_gols(a) != saldo_de_gols(b):
        return saldo_de_gols(a) > saldo_de_gols(b)
    if a["gp"] != b["gp"]:
        return a["gp"] > b["gp"]
    return normalizar(a["nome"]) < normalizar(b["nome"])


def ordenar_classificacao(times):
    """Ordenação por bolhas (bubble sort) sobre uma cópia da lista."""
    tabela = times[:]
    quantidade = len(tabela)
    for i in range(quantidade - 1):
        for j in range(quantidade - 1 - i):
            if not vem_antes(tabela[j], tabela[j + 1]):
                temporario = tabela[j]
                tabela[j] = tabela[j + 1]
                tabela[j + 1] = temporario
    return tabela


def imprimir_tabela(times):
    if len(times) == 0:
        print("Nenhum time cadastrado ainda.")
        return

    tabela = ordenar_classificacao(times)
    print()
    print(f"{'#':>2}  {'Time':<18}{'Pts':>4}{'PJ':>4}{'V':>4}{'E':>4}"
          f"{'D':>4}{'GP':>4}{'GC':>4}{'SG':>5}")
    print("-" * 53)
    posicao = 1
    for time in tabela:
        print(f"{posicao:>2}  {time['nome']:<18}{time['pts']:>4}{time['pj']:>4}"
              f"{time['v']:>4}{time['e']:>4}{time['d']:>4}{time['gp']:>4}"
              f"{time['gc']:>4}{saldo_de_gols(time):>5}")
        posicao += 1


# ---------------------------------------------------------------------------
# Persistência (arquivo JSON)
# ---------------------------------------------------------------------------
def salvar_dados(times, partidas):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump({"times": times, "partidas": partidas}, arquivo,
                  ensure_ascii=False, indent=2)


def carregar_dados(times, partidas):
    """Se existir arquivo salvo, preenche as listas com os dados dele."""
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return
    times.extend(dados["times"])
    partidas.extend(dados["partidas"])


def carregar_exemplo(times, partidas):
    """Preenche o campeonato com dados de exemplo (útil para demonstração)."""
    if len(times) > 0 or len(partidas) > 0:
        print("O exemplo só pode ser carregado com o campeonato vazio.")
        return
    for nome in ["Remo", "Paysandu", "Tuna Luso", "Águia de Marabá"]:
        cadastrar_time(times, nome)
    jogos = [
        ("Remo", "Paysandu", 2, 1),
        ("Paysandu", "Remo", 1, 1),
        ("Tuna Luso", "Águia de Marabá", 0, 0),
        ("Águia de Marabá", "Tuna Luso", 2, 3),
        ("Remo", "Tuna Luso", 3, 0),
        ("Paysandu", "Águia de Marabá", 1, 0),
    ]
    for mandante, visitante, gm, gv in jogos:
        registrar_resultado(times, partidas, mandante, visitante, gm, gv)
    print("Dados de exemplo carregados.")


# ---------------------------------------------------------------------------
# Interface em texto (menu)
# ---------------------------------------------------------------------------
def mostrar_menu():
    print("\n=== CAMPEONATO DE PONTOS CORRIDOS ===")
    print("1 - Cadastrar time")
    print("2 - Registrar resultado de partida")
    print("3 - Ver tabela de classificação")
    print("4 - Listar todas as partidas")
    print("5 - Buscar partidas por time")
    print("6 - Carregar dados de exemplo")
    print("0 - Sair")


def main():
    times = []
    partidas = []
    carregar_dados(times, partidas)

    while True:
        mostrar_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            nome = input("Nome do time: ")
            _, mensagem = cadastrar_time(times, nome)
            print(mensagem)

        elif opcao == "2":
            mandante = input("Time mandante: ")
            visitante = input("Time visitante: ")
            gols_mandante = ler_inteiro(f"Gols do mandante ({mandante.strip()}): ")
            gols_visitante = ler_inteiro(f"Gols do visitante ({visitante.strip()}): ")
            _, mensagem = registrar_resultado(times, partidas, mandante, visitante,
                                              gols_mandante, gols_visitante)
            print(mensagem)

        elif opcao == "3":
            imprimir_tabela(times)

        elif opcao == "4":
            if len(partidas) == 0:
                print("Nenhuma partida registrada.")
            for partida in partidas:
                print(texto_partida(partida))

        elif opcao == "5":
            termo = input("Nome (ou parte do nome) do time: ")
            encontradas = buscar_partidas(partidas, termo)
            if len(encontradas) == 0:
                print("Nenhuma partida encontrada.")
            for partida in encontradas:
                print(texto_partida(partida))

        elif opcao == "6":
            carregar_exemplo(times, partidas)

        elif opcao == "0":
            salvar_dados(times, partidas)
            print("Dados salvos. Até logo!")
            break

        else:
            print("Opção inválida.")

        salvar_dados(times, partidas)


if __name__ == "__main__":
    main()
