# Gerenciador de Campeonato de Pontos Corridos

Atividade Avaliativa AV1 — Paradigmas de Programação
Universidade da Amazônia (UNAMA) — Ciência da Computação
Professor: Rodrigo Medeiros Costa

## Integrantes

| Nome | GitHub |
|------|--------|
| pedro vinicius cardoso vidal | @pdoVDL|
| Bernardo Neto da Silva Santos - 04154707 | @bnd-sants |
| Bruno Rafael Nery Ferreira| @Brunildo-AK |


## 1. Descrição do problema

Organizar um campeonato de pontos corridos exige acompanhar vários times e
muitos jogos, e recalcular a classificação a cada resultado. Fazer isso à mão
é trabalhoso e sujeito a erros. Este programa de terminal resolve o problema.

**Entradas**
- nome dos times;
- resultado de cada partida: time mandante, time visitante e gols de cada lado;
- termo de busca (nome ou parte do nome de um time).

**Regras principais**
- vitória = 3 pontos, empate = 1 ponto, derrota = 0;
- cada confronto (mandante x visitante) só pode ser registrado uma vez, o que
  permite jogos de ida e volta;
- um time não joga contra ele mesmo, e os dois times precisam estar cadastrados;
- gols devem ser inteiros maiores ou iguais a zero;
- critérios de classificação, nesta ordem: pontos, pontos nos confrontos
  diretos entre equipes empatadas, vitórias, saldo de gols, gols pró e ordem
  alfabética.

**Resultados esperados**
- tabela de classificação com posição, pontos, jogos, vitórias, empates,
  derrotas, gols pró, gols contra e saldo de gols;
- lista de todas as partidas e busca de partidas por time;
- edição e remoção de resultados, com recálculo automático da classificação;
- calendário automático de ida e volta, com indicação de jogos pendentes,
  realizados e folgas;
- dados salvos em arquivo, para continuar o campeonato depois.

## 2. Instruções de execução

**Requisitos:** Python 3.8 ou superior. Não há bibliotecas externas.

```bash
git clone URL_DO_REPOSITORIO
cd NOME_DO_REPOSITORIO
python campeonato.py
```

No menu, a opção **6** carrega dados de exemplo (útil para testar rápido), as
opções **7** e **8** editam ou removem um resultado, e a opção **9** gera e
exibe o calendário de ida e volta. Os dados ficam no arquivo
`dados_campeonato.json`, criado automaticamente. Para começar um campeonato
do zero, apague esse arquivo.

## 3. Explicação da solução

O programa guarda o estado em três listas: `times` (dicionários com nome, jogos,
vitórias, empates, derrotas, gols e pontos), `partidas` (dicionários com
mandante, visitante e placar) e `calendario` (rodadas com seus jogos). Cada
ação do menu executa uma sequência de instruções que **altera esse estado**.

Exemplo do fluxo ao registrar o resultado `Remo 2 x 1 Paysandu`:

1. `lancar_placar` localiza as duas equipes e valida o confronto.
2. A partida é adicionada à lista `partidas` (`partidas.append(...)`).
3. `atualizar_estatisticas` é chamada para cada time e modifica suas variáveis:
   `pj` e `gp`/`gc` aumentam, e uma decisão define se somam vitória (+3 pontos),
   empate (+1) ou derrota.
4. Na próxima exibição, a tabela já reflete os novos valores.

Ao editar ou remover um jogo, `recalcular_estatisticas` zera os totais das
equipes e os reconstrói a partir dos resultados restantes. Isso evita manter
pontos ou gols antigos depois de uma alteração. O calendário é gerado pelo
método de rotação: cada equipe enfrenta todas as outras uma vez em cada mando
de campo; com número ímpar de equipes, uma equipe folga por rodada.

### Elementos do paradigma imperativo no código

| Elemento | Onde aparece em `campeonato.py` |
|----------|--------------------------------|
| **Sequência de instruções** | `lancar_placar`: validar, criar a partida, guardar e atualizar as equipes, sempre nessa ordem |
| **Variáveis e atribuições** | `time["pts"] += PONTOS_VITORIA`, `temporario = tabela[j]`, `tabela[j] = tabela[j + 1]`, `posicao += 1` |
| **Alteração de estado** | `atualizar_estatisticas` modifica as estatísticas; `adicionar_equipe` e `lancar_placar` modificam as listas |
| **Decisões** | `if/elif/else` em `atualizar_estatisticas` (vitória, empate ou derrota), em `vem_antes` (desempates) e no menu da `main` |
| **Repetições** | `while True` no menu e em `ler_inteiro`; `for` em `localizar_equipe`, `pesquisar_jogos` e `mostrar_classificacao`; laços na geração do calendário e laços aninhados na ordenação |
| **Funções/procedimentos** | `adicionar_equipe`, `lancar_placar`, `pesquisar_jogos`, `ordenar_classificacao`, `mostrar_classificacao`, `salvar_dados` etc. |
| **Constantes** | `PONTOS_VITORIA`, `PONTOS_EMPATE`, `ARQUIVO_DADOS` |

A ordenação da tabela usa **ordenação por bolhas** escrita à mão
(`ordenar_classificacao`), com dois laços `for` e troca de posições por variável
temporária. Assim fica explícito como o estado da lista muda passo a passo. A
função `vem_antes` compara os pontos no mini-campeonato entre equipes empatadas
antes de aplicar os outros critérios de desempate.

## 4. Reflexão sobre o desenvolvimento

**Decisões**
- Usar listas de dicionários, simples e fáceis de acompanhar.
- Atualizar as estatísticas ao registrar uma partida e recalculá-las ao editar
  ou remover um resultado, mantendo o estado consistente.
- Escrever a ordenação manualmente, para evidenciar laços e atribuições.
- Separar a lógica (funções que devolvem sucesso e mensagem) da interface
  (`main`), deixando o código mais legível.

**Dificuldades**
- Definir a ordem dos critérios de desempate.
- Impedir registros duplicados e entradas inválidas (gols negativos ou texto).
- Atualizar os acumuladores da tabela após editar ou remover um jogo.
- Dividir o trabalho e manter o histórico de commits coerente entre os integrantes.

**Possíveis melhorias**
- Interface gráfica ou web.
- Testes automatizados.

## 5. Contribuição dos integrantes

| Integrante                   | Participação |      matricula      |
|------------------------------|--------------|-----------------------
| Pedro Vinicius cardoso vidal | desenvolvedor do codigo |04164494
| Bruno Rafael Nery Ferreira   |Revisor de codigo e escritor do Readme|04161964
| Bernardo Neto da Silva Santos | Tester |
