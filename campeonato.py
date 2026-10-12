"""
Gerenciador de Campeonato de Pontos Corridos
Disciplina: Paradigmas de Programação (UNAMA) - Atividade Avaliativa AV1

Funcionalidades:
  - cadastro de equipes e lançamento, edição e remoção de placares
  - geração automática de calendário de ida e volta
  - classificação com confronto direto como critério de desempate
  - listagem e pesquisa de jogos
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
        if entrada.isdecimal():
            return int(entrada)
        print("  Entrada inválida. Informe um inteiro igual ou maior que zero.")


def gols_validos(valor):
    """Gols devem ser inteiros (não booleanos) maiores ou iguais a zero."""
    return isinstance(valor, int) and not isinstance(valor, bool) and valor >= 0


def saldo_de_gols(time):
    """Saldo de gols = gols pró - gols contra."""
    return time["gp"] - time["gc"]


def pontos_confronto_direto(time, grupo, partidas):
    """Soma os pontos de jogos entre equipes empatadas na classificação."""
    nomes_grupo = [equipe["nome"] for equipe in grupo]
    pontos = 0
    for partida in partidas:
        mandante = partida["mandante"]
        visitante = partida["visitante"]
        if time["nome"] not in (mandante, visitante):
            continue
        outro_time = visitante if mandante == time["nome"] else mandante
        if outro_time not in nomes_grupo:
            continue

        gols_time = (partida["gols_mandante"] if mandante == time["nome"]
                     else partida["gols_visitante"])
        gols_adversario = (partida["gols_visitante"] if mandante == time["nome"]
                           else partida["gols_mandante"])
        if gols_time > gols_adversario:
            pontos += PONTOS_VITORIA
        elif gols_time == gols_adversario:
            pontos += PONTOS_EMPATE
    return pontos


# ---------------------------------------------------------------------------
# Times
# ---------------------------------------------------------------------------
def localizar_equipe(times, nome):
    """Percorre a lista de times e devolve o dicionário do time, ou None."""
    alvo = normalizar(nome)
    for time in times:
        if normalizar(time["nome"]) == alvo:
            return time
    return None


def adicionar_equipe(times, nome):
    """Cadastra um novo time com todas as estatísticas zeradas."""
    nome = nome.strip()
    if nome == "":
        return False, "O nome da equipe não pode ficar em branco."
    if localizar_equipe(times, nome) is not None:
        return False, f"A equipe '{nome}' já faz parte do campeonato."

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
    return True, f"Equipe '{nome}' adicionada com sucesso."


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


def lancar_placar(times, partidas, nome_mandante, nome_visitante,
                  gols_mandante, gols_visitante):
    """Valida o confronto, guarda a partida e atualiza os dois times."""
    mandante = localizar_equipe(times, nome_mandante)
    visitante = localizar_equipe(times, nome_visitante)

    if mandante is None or visitante is None:
        return False, "Equipe não encontrada. Confira os nomes e cadastre as equipes primeiro."
    if mandante is visitante:
        return False, "Uma equipe não pode enfrentar a si mesma."
    if not gols_validos(gols_mandante) or not gols_validos(gols_visitante):
        return False, "Os gols precisam ser números inteiros iguais ou maiores que zero."
    if partida_ja_registrada(partidas, mandante["nome"], visitante["nome"]):
        return False, "Este jogo com esse mando de campo já está registrado."

    partida = {
        "id": max((jogo["id"] for jogo in partidas), default=0) + 1,
        "mandante": mandante["nome"],
        "visitante": visitante["nome"],
        "gols_mandante": gols_mandante,
        "gols_visitante": gols_visitante,
    }
    partidas.append(partida)

    atualizar_estatisticas(mandante, gols_mandante, gols_visitante)
    atualizar_estatisticas(visitante, gols_visitante, gols_mandante)
    return True, "Placar lançado; classificação atualizada."


def recalcular_estatisticas(times, partidas):
    """Reconstrói os totais das equipes a partir dos resultados registrados."""
    for time in times:
        for chave in ("pj", "v", "e", "d", "gp", "gc", "pts"):
            time[chave] = 0

    for partida in partidas:
        mandante = localizar_equipe(times, partida["mandante"])
        visitante = localizar_equipe(times, partida["visitante"])
        if mandante is None or visitante is None:
            continue
        atualizar_estatisticas(
            mandante, partida["gols_mandante"], partida["gols_visitante"]
        )
        atualizar_estatisticas(
            visitante, partida["gols_visitante"], partida["gols_mandante"]
        )


def editar_resultado(times, partidas, id_partida, gols_mandante,
                     gols_visitante):
    """Altera o placar de uma partida e atualiza a classificação."""
    partida = next((jogo for jogo in partidas if jogo["id"] == id_partida), None)
    if partida is None:
        return False, "Jogo não encontrado. Confira o número informado."
    if not gols_validos(gols_mandante) or not gols_validos(gols_visitante):
        return False, "Os gols precisam ser números inteiros iguais ou maiores que zero."

    partida["gols_mandante"] = gols_mandante
    partida["gols_visitante"] = gols_visitante
    recalcular_estatisticas(times, partidas)
    return True, "Placar alterado; classificação recalculada."


def remover_resultado(times, partidas, id_partida):
    """Remove uma partida e atualiza a classificação."""
    for indice, partida in enumerate(partidas):
        if partida["id"] == id_partida:
            partidas.pop(indice)
            recalcular_estatisticas(times, partidas)
            return True, "Jogo removido; classificação recalculada."
    return False, "Jogo não encontrado. Confira o número informado."


def pesquisar_jogos(partidas, termo):
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
def vem_antes(a, b, times, partidas):
    """
    Critérios: pontos, pontos no confronto direto entre equipes empatadas,
    vitórias, saldo de gols, gols pró e ordem alfabética.
    """
    if a["pts"] != b["pts"]:
        return a["pts"] > b["pts"]
    grupo_empatado = [time for time in times if time["pts"] == a["pts"]]
    pontos_a = pontos_confronto_direto(a, grupo_empatado, partidas)
    pontos_b = pontos_confronto_direto(b, grupo_empatado, partidas)
    if pontos_a != pontos_b:
        return pontos_a > pontos_b
    if a["v"] != b["v"]:
        return a["v"] > b["v"]
    if saldo_de_gols(a) != saldo_de_gols(b):
        return saldo_de_gols(a) > saldo_de_gols(b)
    if a["gp"] != b["gp"]:
        return a["gp"] > b["gp"]
    return normalizar(a["nome"]) < normalizar(b["nome"])


def ordenar_classificacao(times, partidas):
    """Ordenação por bolhas (bubble sort) sobre uma cópia da lista."""
    tabela = times[:]
    quantidade = len(tabela)
    for i in range(quantidade - 1):
        for j in range(quantidade - 1 - i):
            if not vem_antes(tabela[j], tabela[j + 1], times, partidas):
                temporario = tabela[j]
                tabela[j] = tabela[j + 1]
                tabela[j + 1] = temporario
    return tabela


def mostrar_classificacao(times, partidas):
    if len(times) == 0:
        print("Ainda não há equipes cadastradas.")
        return

    tabela = ordenar_classificacao(times, partidas)
    print()
    print(f"{'#':>2}  {'Equipe':<18}{'Pts':>4}{'PJ':>4}{'V':>4}{'E':>4}"
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
def salvar_dados(times, partidas, calendario=None):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump({"times": times, "partidas": partidas,
                   "calendario": calendario or []}, arquivo,
                  ensure_ascii=False, indent=2)


def carregar_dados(times, partidas, calendario=None):
    """Se existir arquivo salvo, preenche as listas com os dados dele."""
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return
    times.extend(dados["times"])
    partidas.extend(dados["partidas"])
    if calendario is not None:
        calendario.extend(dados.get("calendario", []))


def gerar_calendario(times):
    """Gera jogos de ida e volta pelo método de rotação das equipes."""
    if len(times) < 2:
        return []

    rotacao = [time["nome"] for time in times]
    if len(rotacao) % 2 == 1:
        rotacao.append(None)
    quantidade_por_rodada = len(rotacao) - 1
    primeira_perna = []
    folgas = []

    for numero_rodada in range(quantidade_por_rodada):
        rodada = []
        folga = None
        for indice in range(len(rotacao) // 2):
            primeiro = rotacao[indice]
            segundo = rotacao[-(indice + 1)]
            if primeiro is None or segundo is None:
                folga = primeiro if segundo is None else segundo
                continue

            if (numero_rodada + indice) % 2 == 0:
                mandante, visitante = primeiro, segundo
            else:
                mandante, visitante = segundo, primeiro
            rodada.append({"mandante": mandante, "visitante": visitante})
        primeira_perna.append(rodada)
        folgas.append(folga)
        rotacao = [rotacao[0], rotacao[-1], *rotacao[1:-1]]

    calendario = []
    for numero, rodada in enumerate(primeira_perna, start=1):
        calendario.append({
            "rodada": numero,
            "jogos": rodada,
            "folga": folgas[numero - 1],
        })
    for numero, rodada in enumerate(primeira_perna, start=quantidade_por_rodada + 1):
        volta = [
            {"mandante": jogo["visitante"], "visitante": jogo["mandante"]}
            for jogo in rodada
        ]
        calendario.append({
            "rodada": numero,
            "jogos": volta,
            "folga": folgas[numero - quantidade_por_rodada - 1],
        })
    return calendario


def imprimir_calendario(calendario, partidas):
    """Exibe as rodadas e sinaliza os jogos que já têm placar."""
    if not calendario:
        print("Ainda não há calendário. Cadastre ao menos duas equipes.")
        return

    for rodada in calendario:
        print(f"\nRodada {rodada['rodada']}")
        if rodada["folga"] is not None:
            print(f"  Folga: {rodada['folga']}")
        for jogo in rodada["jogos"]:
            registrado = next(
                (partida for partida in partidas
                 if partida["mandante"] == jogo["mandante"]
                 and partida["visitante"] == jogo["visitante"]),
                None,
            )
            if registrado is None:
                texto = f"{jogo['mandante']} x {jogo['visitante']} (pendente)"
            else:
                texto = texto_partida(registrado) + " (realizado)"
            print(f"  {texto}")


def carregar_exemplo(times, partidas):
    """Preenche o campeonato com dados de exemplo (útil para demonstração)."""
    if len(times) > 0 or len(partidas) > 0:
        print("A demonstração só pode ser carregada em um campeonato vazio.")
        return
    for nome in ["Remo", "Paysandu", "Tuna Luso", "Águia de Marabá"]:
        adicionar_equipe(times, nome)
    jogos = [
        ("Remo", "Paysandu", 2, 1),
        ("Paysandu", "Remo", 1, 1),
        ("Tuna Luso", "Águia de Marabá", 0, 0),
        ("Águia de Marabá", "Tuna Luso", 2, 3),
        ("Remo", "Tuna Luso", 3, 0),
        ("Paysandu", "Águia de Marabá", 1, 0),
    ]
    for mandante, visitante, gm, gv in jogos:
        lancar_placar(times, partidas, mandante, visitante, gm, gv)
    print("Campeonato de demonstração carregado.")


# ---------------------------------------------------------------------------
# Interface em texto (menu)
# ---------------------------------------------------------------------------
def mostrar_menu():
    print("\n=== COPA PARAENSE | PONTOS CORRIDOS ===")
    print("1 - Adicionar equipe")
    print("2 - Lançar placar de um jogo")
    print("3 - Consultar classificação")
    print("4 - Ver todos os jogos")
    print("5 - Pesquisar jogos por equipe")
    print("6 - Carregar campeonato de demonstração")
    print("7 - Editar placar de um jogo")
    print("8 - Remover um jogo")
    print("9 - Gerar e consultar calendário de ida e volta")
    print("0 - Encerrar e salvar")


def main():
    times = []
    partidas = []
    calendario = []
    carregar_dados(times, partidas, calendario)

    while True:
        mostrar_menu()
        opcao = input("Digite a opção desejada: ").strip()

        if opcao == "1":
            nome = input("Nome da equipe: ")
            _, mensagem = adicionar_equipe(times, nome)
            print(mensagem)

        elif opcao == "2":
            mandante = input("Equipe mandante: ")
            visitante = input("Equipe visitante: ")
            gols_mandante = ler_inteiro(f"Gols de {mandante.strip()}: ")
            gols_visitante = ler_inteiro(f"Gols de {visitante.strip()}: ")
            _, mensagem = lancar_placar(
                times, partidas, mandante, visitante,
                gols_mandante, gols_visitante,
            )
            print(mensagem)

        elif opcao == "3":
            mostrar_classificacao(times, partidas)

        elif opcao == "4":
            if len(partidas) == 0:
                print("Ainda não há jogos registrados.")
            for partida in partidas:
                print(texto_partida(partida))

        elif opcao == "5":
            termo = input("Nome (ou trecho do nome) da equipe: ")
            encontradas = pesquisar_jogos(partidas, termo)
            if len(encontradas) == 0:
                print("Nenhum jogo corresponde à pesquisa.")
            for partida in encontradas:
                print(texto_partida(partida))

        elif opcao == "6":
            carregar_exemplo(times, partidas)

        elif opcao == "7":
            if len(partidas) == 0:
                print("Ainda não há jogos disponíveis para editar.")
            else:
                for partida in partidas:
                    print(texto_partida(partida))
                id_partida = ler_inteiro("Número do jogo que deseja editar: ")
                gols_mandante = ler_inteiro("Novo número de gols do mandante: ")
                gols_visitante = ler_inteiro("Novo número de gols do visitante: ")
                _, mensagem = editar_resultado(
                    times, partidas, id_partida, gols_mandante, gols_visitante
                )
                print(mensagem)

        elif opcao == "8":
            if len(partidas) == 0:
                print("Ainda não há jogos disponíveis para remover.")
            else:
                for partida in partidas:
                    print(texto_partida(partida))
                id_partida = ler_inteiro("Número do jogo que deseja remover: ")
                _, mensagem = remover_resultado(times, partidas, id_partida)
                print(mensagem)

        elif opcao == "9":
            calendario = gerar_calendario(times)
            if calendario:
                imprimir_calendario(calendario, partidas)
            else:
                print("Cadastre ao menos duas equipes para criar o calendário.")

        elif opcao == "0":
            salvar_dados(times, partidas, calendario)
            print("Campeonato salvo. Até a próxima!")
            break

        else:
            print("Opção não reconhecida. Escolha um número do menu.")

        salvar_dados(times, partidas, calendario)


if __name__ == "__main__":
    main()