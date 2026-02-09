# VComputacional - Slack

Bot de monitoramento de fluxo de restaurantes que envia notificações automáticas para o Slack com informações sobre ocupação em tempo real durante as refeições (Café da Manhã, Almoço e Jantar).

## Tecnologias

- Python 3.11
- Docker e Docker Compose
- Slack SDK
- Schedule (agendamento de tarefas)

## Como Rodar Localmente

### Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.11 ou superior (para desenvolvimento local)
- Bot do Slack configurado com permissões de envio de mensagens

### Instalação

```bash
# Clone o repositório
git clone https://github.com/empresa/vcomputacional-slack.git

# Entre na pasta
cd vcomputacional-slack

# Crie o arquivo de variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# Suba o container
docker-compose up -d
```

### Rodando sem Docker

```bash
# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python main.py
```

## Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| SLACK_BOT_TOKEN | Token do bot do Slack | xoxb-xxxx-xxxx |
| SLACK_CHANNEL_ID | ID do canal de destino | C0123456789 |
| API_URL | URL base da API de contagem | https://api.exemplo.com |
| API_KEY | Chave de autenticação da API | sua-api-key |
| RESTAURANT_CAPACITIES | Capacidades dos restaurantes (JSON) | {"Restaurante A": 200} |
| TZ | Timezone da aplicação | America/Recife |

## Estrutura de Pastas

```
├── main.py              # Ponto de entrada da aplicação
├── requirements.txt     # Dependências Python
├── Dockerfile           # Configuração do container
├── docker-compose.yaml  # Orquestração de containers
├── data/
│   ├── capacities.json  # Capacidades por restaurante
│   └── state.json       # Estado persistente (gerado automaticamente)
├── logs/                # Arquivos de log
└── src/
    ├── api/             # Cliente da API de contagem
    ├── log/             # Configuração de logging
    ├── services/        # Lógica de negócio (agrupamento por restaurante)
    └── slack/           # Integração com Slack (envio de mensagens)
```

## Funcionamento

O bot monitora automaticamente o fluxo de pessoas nos restaurantes durante os horários de refeição:

- **Café da Manhã**: 07:00 - 10:30
- **Almoço**: 12:00 - 15:30
- **Jantar**: 19:00 - 22:00

A cada intervalo de 30 minutos, o sistema consulta a API de contagem, calcula o headcount atual e envia um resumo formatado para o canal do Slack configurado.

## Deploy

O deploy é feito através do Docker. Para atualizar:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Contato

Dúvidas? Fale com o time de Analytics.