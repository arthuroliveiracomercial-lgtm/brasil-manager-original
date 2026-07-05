# Brasil Manager 0.2

Jogo local de gerenciamento de futebol brasileiro, feito em Python, Streamlit e SQLite.
A base inicial vem de `data/modelos/modelo_importacao_brasil_manager.xlsx`. No primeiro início,
os registros da planilha são preservados e completados com dados fictícios determinísticos para
formar uma liga jogável de 20 clubes e 38 rodadas.

O jogo não depende de API externa nem de scraping.

## Recursos da versão 0.1

- escolha do clube;
- elenco com atributos, condição, moral, salários e valores;
- seis formações e escalação persistida;
- tática com mentalidade, estilo, pressão, linha, ritmo, foco e passes;
- calendário de pontos corridos, turno e returno;
- simulação de toda a rodada com eventos;
- classificação atualizada após cada resultado;
- bilheteria, saldo, orçamento e folha salarial;
- mercado com filtros, propostas e transferências;
- atualização da base por CSV ou Excel com validação.

## Interface e experiência 0.2

- painel principal do treinador com clube, classificação, caixa e próximo jogo;
- identidade visual própria em verde-escuro, azul-petróleo e dourado;
- campo visual para as seis formações;
- funções individuais por posição, com efeitos no motor;
- resumo visual dos efeitos da tática;
- central da rodada com todos os jogos, cronômetro e quatro velocidades;
- eventos de gols, cartões, lesões, defesas, traves, chances e substituições;
- estatísticas detalhadas do jogo do usuário;
- classificação com zonas continentais e rebaixamento;
- calendário agrupado por rodada;
- elenco com filtros, status, moral e condição;
- projeção financeira e alertas de folha salarial.

### Testar uma rodada ao vivo

1. Abra **Escalação**, escolha jogadores e funções e clique em **Salvar Escalação**.
2. Abra **Tática**, ajuste o plano e clique em **Salvar Tática**.
3. Abra **Partida**, escolha a velocidade e clique em **Iniciar Rodada**.
4. Ao final, consulte **Classificação**, **Calendário** e **Finanças**.

Na opção instantânea, o relógio vai diretamente ao resultado. As demais velocidades usam
atualizações progressivas do Streamlit; por isso, mudar de página durante a animação interrompe
apenas a visualização corrente.

### Velocidades

- **Instantânea:** calcula e apresenta a rodada imediatamente.
- **Rápida:** atualiza o relógio em passos maiores.
- **Normal:** equilíbrio entre fluidez e acompanhamento.
- **Lenta:** acompanha mais minutos e eventos na tela.

O estado corrente da Central da Rodada é guardado em `session_state`. Os cálculos esportivos
ficam em `src/match_engine.py`, a linha do tempo simultânea em `src/live_match_engine.py` e o
campo visual em `src/formation_view.py`.

### Limitações atuais

- A animação depende do ciclo de execução do Streamlit; trocar de página interrompe a animação
  visual, mas resultados já confirmados continuam no SQLite.
- Empréstimos funcionam como cessões até o fim da temporada atual; a devolução automática será
  adicionada numa versão futura.
- A substituição automática continua ativa; no modo Manual também é possível registrar até cinco trocas.

## Expansão de competições e carreira

A versão expandida adiciona:

- 20 clubes fictícios de Série B e 20 de Série C, com elencos gerados;
- Série A, B e C, Copa do Brasil, dez estaduais, Libertadores e Sul-Americana;
- estruturas configuráveis de liga, grupos e mata-mata;
- janelas de transferências editáveis;
- empréstimos de jogadores com taxa, divisão salarial e opção de compra;
- empréstimos bancários com juros, parcelas e saldo devedor;
- fechamento mensal com salários, estádio, custos operacionais e patrocínio;
- páginas de Copas, Janelas, Empréstimos, Competições e Histórico;
- modo manual de partida, avanço por minuto/próximo lance, substituições e planos rápidos.

### Crédito e fechamento mensal

Em **Empréstimos**, abra a guia **Empréstimos e Dívidas**, escolha valor, prazo e juros.
O dinheiro entra no caixa imediatamente. Em **Finanças**, use **Processar Fechamento Mensal**
para descontar folha, custos e parcelas e registrar o relatório.

### Janelas e empréstimos de atletas

As datas são editadas em **Janelas de Transferências**. Compras e empréstimos ficam bloqueados
fora de uma janela ativa. Em **Empréstimos**, escolha atleta, destino, duração, divisão salarial,
taxa e eventual opção de compra.

### Competições

As regras e inscrições ficam nas tabelas normalizadas `competitions`,
`competition_phases`, `competition_groups`, `competition_matches` e
`club_season_registration`. A implementação inicial usa calendários completos para as ligas e
estrutura configurável para copas e continentais.

### Limitações da expansão

- Clubes e elencos adicionais de Série B/C são fictícios e destinam-se ao gameplay.
- Copas e continentais possuem estrutura e páginas, mas o avanço automático de todas as fases
  ainda será aprofundado em versões seguintes.
- Mudanças táticas manuais são registradas durante o jogo; o motor incremental que recalcula
  cada lance após toda intervenção ainda é simplificado.
- Empréstimos de jogadores retornam pela rotina de encerramento, mas ainda não há convocação
  automática diária dessa rotina.

## Como instalar no Windows

1. Instale o Python 3.11 ou mais recente em <https://www.python.org/downloads/>.
   Durante a instalação, marque **Add Python to PATH**.
2. Abra o PowerShell dentro da pasta do projeto.
3. Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, execute uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

4. Instale as dependências:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Inicie o jogo:

```powershell
streamlit run app.py
```

O navegador abrirá em `http://localhost:8501`.

## Acessar pelo celular

1. Deixe o Brasil Manager aberto no computador.
2. Conecte o celular à mesma rede Wi‑Fi.
3. No navegador do celular, acesse o endereço mostrado pelo computador, por exemplo:
   `http://192.168.15.10:8501`.
4. Se o Windows solicitar permissão de firewall, permita somente para **redes privadas**.

O layout mobile possui cards em duas colunas, campo compacto, tabelas com rolagem horizontal e
uma barra inferior com atalhos para Início, Elenco, Escalação, Partida e Classificação. O endereço
IP pode mudar quando o roteador ou o computador for reiniciado.

## Primeiro início

O banco `database/brasil_manager.db` é criado automaticamente. A planilha-modelo é importada e
a temporada é gerada. Escolha um clube na tela inicial, salve sua escalação e tática, depois use
**Partida** para avançar uma rodada.

Para recomeçar completamente, feche o jogo e apague `database/brasil_manager.db`. Ele será
recriado no próximo início.

## Importar sua própria base

Na tela inicial, abra **Atualizar a base por Excel ou CSV**. O Excel pode conter as abas
`clubes`, `jogadores`, `competicoes`, `calendario` e `transferencias`. CSVs usam uma entidade
por arquivo.

Antes de gravar, o jogo verifica:

- colunas obrigatórias;
- IDs duplicados e referências inexistentes;
- números, datas e valores permitidos;
- atributos fora de 0–100;
- idades e placares inconsistentes.

A importação é transacional: se qualquer gravação falhar, nenhuma parte do arquivo é aplicada.

## Estrutura

```text
app.py
pages/                  páginas do jogo
src/database.py         SQLite e persistência
src/data_loader.py      Excel/CSV e carga inicial
src/match_engine.py     simulação
src/league_engine.py    calendário e liga
src/tactic_engine.py    efeitos táticos
src/finance_engine.py   caixa e folha
src/transfer_engine.py  propostas e contratações
```

Todos os clubes e jogadores adicionais são fictícios. Eles existem apenas para tornar a versão
inicial jogável até que uma planilha mais completa seja importada.

## Experiência mobile e carreira

No celular, abra o endereço de rede exibido pelo iniciador. O menu inferior oferece acesso
rápido a **Início**, **Elenco**, **Time**, **Jogar** e **Mais**.

A área **Mais** reúne treino semanal, notícias, relatórios de olheiros, replays textuais,
configurações, regras personalizadas e versões locais do save. As telas foram ajustadas para
toque e leitura em uma coluna, sem depender da barra lateral no navegador do celular.

## Atualização desta versão

- Base inicial com clubes e jogadores das Séries A, B e C.
- Correção do menu mobile para navegar na mesma aba.
- Correção de continuidade da temporada com botão para iniciar a próxima temporada.
- Calendários gerados para Copa do Brasil, Estaduais, Libertadores e Sul-Americana na aba Copas.
- Correção para remover clubes genéricos antigos da Série B/C e usar a base atualizada.
