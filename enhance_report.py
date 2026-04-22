#!/usr/bin/env python3
"""
enhance_report.py — Injeta cabeçalho, metadados e estilos
customizados no relatório HTML gerado pelo OWASP ZAP.

Uso:
  python3 enhance_report.py \
    --input  zap-reports/zap-report.html \
    --output zap-reports/zap-report-enhanced.html \
    --title  "Relatório de Segurança" \
    --target "http://localhost:8080" \
    --date   "22/04/2026 10:30 UTC" \
    --commit "abc1234" \
    --branch "main"
"""

import argparse
import os
import re
import sys
from datetime import datetime


BANNER_STYLE = """
<style id="zap-custom-overrides">
  /* ── Reset e base ─────────────────────────────────── */
  *, *::before, *::after { box-sizing: border-box; }

  body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    background: #0d1117 !important;
    color: #e6edf3 !important;
    margin: 0 !important;
  }

  /* ── Banner de cabeçalho ──────────────────────────── */
  #zap-custom-banner {
    background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
    border-bottom: 2px solid #30363d;
    padding: 1.5rem 2rem;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 1rem;
  }
  #zap-custom-banner .logo {
    display: flex;
    align-items: center;
    gap: .75rem;
  }
  #zap-custom-banner .logo svg {
    width: 40px;
    height: 40px;
    flex-shrink: 0;
  }
  #zap-custom-banner h1 {
    font-size: 1.3rem;
    font-weight: 700;
    color: #58a6ff;
    margin: 0;
  }
  #zap-custom-banner .meta {
    display: flex;
    flex-wrap: wrap;
    gap: .5rem 1.5rem;
    margin-left: auto;
    font-size: .8rem;
    color: #8b949e;
  }
  #zap-custom-banner .meta span strong {
    color: #e6edf3;
  }

  /* ── Badges de severidade ────────────────────────── */
  .risk-high, [class*="high" i] td:first-child,
  td.risk-high { color: #f85149 !important; font-weight: 600 !important; }

  .risk-medium, [class*="medium" i] td:first-child,
  td.risk-medium { color: #d29922 !important; font-weight: 600 !important; }

  .risk-low, [class*="low" i] td:first-child,
  td.risk-low { color: #3fb950 !important; font-weight: 600 !important; }

  .risk-info, [class*="informational" i] td:first-child,
  td.risk-info { color: #58a6ff !important; }

  /* ── Tabelas ─────────────────────────────────────── */
  table {
    background: #161b22 !important;
    border-collapse: collapse !important;
    width: 100% !important;
  }
  th {
    background: #1c2333 !important;
    color: #8b949e !important;
    padding: .6rem 1rem !important;
    border-bottom: 1px solid #30363d !important;
    font-size: .8rem !important;
    text-transform: uppercase !important;
    letter-spacing: .04em !important;
  }
  td {
    padding: .55rem 1rem !important;
    border-bottom: 1px solid #21262d !important;
    font-size: .875rem !important;
    color: #e6edf3 !important;
    vertical-align: top !important;
  }
  tr:hover td { background: #1c2333 !important; }

  /* ── Cards / painéis ─────────────────────────────── */
  .alertsum, .alertdetail, div[id^="alert"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    margin: 1rem 2rem !important;
    padding: 1rem 1.5rem !important;
  }

  h2, h3 { color: #58a6ff !important; }

  /* ── Rodapé customizado ──────────────────────────── */
  #zap-custom-footer {
    text-align: center;
    padding: 1.5rem;
    font-size: .78rem;
    color: #8b949e;
    border-top: 1px solid #30363d;
    margin-top: 2rem;
  }
  #zap-custom-footer a { color: #58a6ff; text-decoration: none; }
</style>
"""


def build_banner(title: str, target: str, date: str, commit: str, branch: str) -> str:
    shield_svg = """<svg viewBox="0 0 24 24" fill="none"
      stroke="#58a6ff" stroke-width="1.8"
      stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>"""

    return f"""
<div id="zap-custom-banner">
  <div class="logo">
    {shield_svg}
    <h1>{title}</h1>
  </div>
  <div class="meta">
    <span>🎯 Target: <strong>{target}</strong></span>
    <span>📅 Data: <strong>{date}</strong></span>
    <span>🌿 Branch: <strong>{branch}</strong></span>
    <span>📦 Commit: <strong>{commit[:8] if commit else 'N/A'}</strong></span>
    <span>🔧 Scanner: <strong>OWASP ZAP</strong></span>
  </div>
</div>
"""


def build_footer() -> str:
    return f"""
<div id="zap-custom-footer">
  Relatório gerado por
  <a href="https://owasp.org/www-project-zap/" target="_blank" rel="noopener">OWASP ZAP</a>
  via GitHub Actions &mdash; {datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC
</div>
"""


def enhance(args: argparse.Namespace) -> None:
    if not os.path.isfile(args.input):
        print(f"[AVISO] Arquivo de entrada não encontrado: {args.input}")
        print("        Gerando relatório de fallback...")
        html = generate_fallback_report(args)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[OK] Relatório de fallback salvo em: {args.output}")
        return

    with open(args.input, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    # Injetar estilos customizados antes do </head>
    html = re.sub(
        r"(</head>)",
        BANNER_STYLE + r"\1",
        html,
        count=1,
        flags=re.IGNORECASE,
    )

    # Injetar banner após o <body>
    banner = build_banner(args.title, args.target, args.date, args.commit, args.branch)
    html = re.sub(
        r"(<body[^>]*>)",
        r"\1" + banner,
        html,
        count=1,
        flags=re.IGNORECASE,
    )

    # Injetar rodapé antes do </body>
    footer = build_footer()
    html = re.sub(
        r"(</body>)",
        footer + r"\1",
        html,
        count=1,
        flags=re.IGNORECASE,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Relatório customizado salvo em: {args.output}")


def generate_fallback_report(args: argparse.Namespace) -> str:
    """Cria um relatório HTML mínimo quando o ZAP não gerou saída."""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <title>{args.title}</title>
  {BANNER_STYLE}
</head>
<body>
  {build_banner(args.title, args.target, args.date, args.commit, args.branch)}
  <div style="padding:2rem; text-align:center; color:#8b949e;">
    <h2 style="color:#d29922;">⚠️ Relatório ZAP não disponível</h2>
    <p style="margin-top:.75rem;">
      O scan foi concluído, mas o relatório HTML principal não foi gerado.<br/>
      Verifique os logs do workflow para mais detalhes.
    </p>
  </div>
  {build_footer()}
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Customiza o relatório HTML do OWASP ZAP")
    parser.add_argument("--input",  required=True, help="Caminho do relatório HTML gerado pelo ZAP")
    parser.add_argument("--output", required=True, help="Caminho do relatório HTML de saída")
    parser.add_argument("--title",  default="Relatório de Segurança — OWASP ZAP")
    parser.add_argument("--target", default="N/A")
    parser.add_argument("--date",   default=datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC"))
    parser.add_argument("--commit", default="N/A")
    parser.add_argument("--branch", default="N/A")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    enhance(args)


if __name__ == "__main__":
    main()
