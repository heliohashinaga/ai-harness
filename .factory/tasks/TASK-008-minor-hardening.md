# TASK-008 — Hardening menor: coder lazy + cleaner tolerante a non-str

## Goal

Dois resíduos do review do cleaner (sessão anterior):
1. `build_coder_node(chat=None)` constrói o cliente LLM no *build* e explode
   sem credenciais — o erro deveria aparecer no *invoke* (coder não tem
   modo pass-through, mas construir o grafo offline deveria funcionar).
2. `clean_code_text` trata exceção do `chat`, mas se o `chat` retornar
   não-`str` (ex. `None`), o `None` escapa o fail-safe e quebra na
   validação do `CleanerOutput`.

## Context

- `src/aiharness/agents/coder.py`: `effective = ... default_chat(...)` no
  corpo do builder; `coder_node` usa `effective`.
- `src/aiharness/agents/cleaner.py`: `clean_code_text` retorna
  `chat(...)` direto no `try`.
- Padrão de teste: `tests/unit/test_cleaner.py`
  (`test_cleaner_builds_offline_without_credentials` com
  `monkeypatch.delenv`).

## Acceptance Criteria

- [ ] `build_coder_node()` sem `chat` constrói sem credenciais; a falha
  (sem chave) acontece no invoke, não no build. Teste keyless prova os
  dois comportamentos.
- [ ] `clean_code_text` (e o nó) com `chat` retornando `None`/não-`str`
  devolve o código de entrada inalterado. Teste prova.
- [ ] `.\scripts\verify.ps1` passa; sem dependência nova.

## Constraints

- Minimal diff; sem reescrita unrelated.
- `default_chat` continua existindo (CLI/runners usam direto).
