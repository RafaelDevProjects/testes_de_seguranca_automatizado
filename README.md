# 🛡️ OWASP ZAP — GitHub Actions Security Scan

Pipeline de segurança automatizado usando **OWASP ZAP** para escanear aplicações web e gerar relatórios HTML detalhados.

---

## 📁 Estrutura do Projeto

```
.
├── .github/
│   └── workflows/
│       └── zap-scan.yml          # ← Workflow principal do GitHub Actions
├── app/
│   └── index.html                # ← Aplicação web alvo do scan
├── scripts/
│   └── enhance_report.py         # ← Script Python para customizar o HTML
├── zap/
│   └── rules.tsv                 # ← Regras de alertas do ZAP (IGNORE/WARN/FAIL)
└── README.md
```

---

## ⚙️ Como Funciona

```
Push / PR / Agendamento (cron)
        │
        ▼
┌───────────────────────┐
│  1. Checkout do repo  │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│  2. Iniciar app local │  → python -m http.server 8080
│     (porta 8080)      │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│  3. OWASP ZAP Scan    │  → baseline | full | api
│   (Docker container)  │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│  4. Gerar relatórios  │  → HTML + JSON + Markdown
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│  5. Customizar HTML   │  → enhance_report.py
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│  6. Upload Artifacts  │  → 30 dias de retenção
│  + Comentar no PR     │
└───────────────────────┘
```

---

## 🚀 Modos de Scan

| Modo        | Ação no ZAP                                    | Velocidade | Uso recomendado            |
|-------------|------------------------------------------------|------------|----------------------------|
| `baseline`  | Scan passivo (spider + alertas automáticos)    | ~2 min     | Todo PR e push             |
| `full`      | Scan ativo + passivo (ataque simulado)         | ~10-30 min | Release semanal            |
| `api`       | Scan de API REST/OpenAPI/GraphQL               | ~5 min     | Endpoints de API           |

### Executar manualmente (workflow_dispatch)

1. Acesse **Actions → 🛡️ OWASP ZAP Security Scan**
2. Clique em **Run workflow**
3. Escolha o tipo: `baseline`, `full` ou `api`

---

## 📊 Relatórios Gerados

Após cada execução, os seguintes arquivos ficam disponíveis nos **Artifacts** do workflow:

| Arquivo                       | Descrição                               |
|-------------------------------|-----------------------------------------|
| `zap-report.html`             | Relatório HTML padrão do ZAP            |
| `zap-report-enhanced.html`    | Relatório HTML com tema customizado     |
| `zap-report.json`             | Dados brutos em JSON (integração CI/CD) |
| `zap-report.md`               | Resumo em Markdown (comentário no PR)   |
| `zap-console.log`             | Log completo do scan                    |

---

## 🔧 Configurar Regras (`zap/rules.tsv`)

```tsv
# ID_Regra <TAB> Ação <TAB> Comentário
10020   WARN    # Anti-clickjacking Header
40012   FAIL    # XSS Reflected — quebra o build
10015   IGNORE  # Heartbleed — não aplicável
```

| Ação     | Efeito                                  |
|----------|-----------------------------------------|
| `IGNORE` | Oculta o alerta completamente           |
| `WARN`   | Registra como aviso, não quebra o build |
| `FAIL`   | Quebra o build se a vulnerabilidade for encontrada |

---

## 🌐 Adaptar para sua Aplicação

### Trocar o alvo do scan

No arquivo `.github/workflows/zap-scan.yml`, altere:

```yaml
env:
  APP_PORT: 8080          # porta da sua aplicação
  TARGET_URL: http://localhost:8080
```

### Usar um servidor diferente (Node.js, Flask, etc.)

Substitua o step **"Iniciar aplicação web local"**:

```yaml
# Node.js / Express
- name: 🚀 Iniciar aplicação
  run: |
    npm install
    npm start &
    echo "APP_PID=$!" >> $GITHUB_ENV

# Flask / Python
- name: 🚀 Iniciar aplicação
  run: |
    pip install -r requirements.txt
    python app.py &
    echo "APP_PID=$!" >> $GITHUB_ENV
```

### Escanear URL externa (staging/homologação)

```yaml
env:
  TARGET_URL: https://staging.meusite.com
```
> ⚠️ Não execute scan ativo (`full`) em ambientes de produção sem autorização!

---

## 🔒 Permissões Necessárias

```yaml
permissions:
  contents: read       # Ler o código do repositório
  issues: write        # Criar issues com vulnerabilidades
  pull-requests: write # Comentar nos PRs com o resumo
```

---

## 📦 Dependências

- **GitHub Actions** — Runner Ubuntu Latest
- **OWASP ZAP** — [`ghcr.io/zaproxy/zaproxy:stable`](https://github.com/zaproxy/zaproxy/pkgs/container/zaproxy)
- **Python 3.11** — Para servidor local e script de customização
- **Docker** — Disponível por padrão no runner `ubuntu-latest`

---

## 📋 Exemplo de Saída no PR

```
🛡️ OWASP ZAP — Resultado do Scan de Segurança

WARN: Anti-clickjacking Header [10020] x 3
WARN: X-Content-Type-Options Header Missing [10021] x 3
WARN: Content Security Policy (CSP) Header Not Set [10038] x 3
INFO: Storable and Cacheable Content [10049] x 2

Commit: `abc12345`
Branch: `feature/login`
Target: `http://localhost:8080`

📎 Ver relatório completo nos artefatos
```
