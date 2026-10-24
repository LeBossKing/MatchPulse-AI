# Task 6: Azure setup and deployment verification

The adapter, configuration checks, and simulated integration tests are implemented. Your subscription balance, resource permissions, model quota, and actual deployment access must be checked in your account. No Azure resource is created by this repository.

The default mock workflow and Task 5 sample dashboard continue to work without Azure. Task 7 connects dashboard selections to backend processing in API mode; Samples remains an explicit offline option.

## 1. Check your subscription

Open [Azure Portal](https://portal.azure.com), then **Subscriptions**, and select the subscription you intend to use. Confirm it is active and check its remaining credit. For Azure for Students, Microsoft documents the credit balance in the Azure Sponsorship portal; see the [education FAQ](https://learn.microsoft.com/en-us/azure/education-hub/faq).

Azure for Students advertises Azure OpenAI access and $100 credit usable within 12 months. This does not establish that a particular deployment has quota in your subscription and region. Check the actual model/deployment availability before changing your subscription.

## 2. Create or reuse one model deployment

1. Open [Microsoft Foundry](https://ai.azure.com) and select the correct subscription and resource/project. Create a Foundry or Azure OpenAI resource if you do not already have one.
2. In the model catalog (**Discover → Models** in the current Foundry portal), choose an Azure OpenAI text model that supports both **Responses** and **structured outputs**. A suitable first option is `gpt-4.1-mini` if it is offered with available quota in your account. Availability depends on region and subscription.
3. Create one deployment with a name such as `matchpulse-tactical`. Use a consumption deployment supported by your subscription and review the displayed pricing/quota before creating it. This example name is a suggestion; the code does not create it.
4. Open that deployment's details, under **Build → Models** in the current portal. Copy its **resource endpoint**, **deployment name**, and **resource API key** into your local backend configuration.

The adapter accepts public Azure resource endpoints such as `https://YOUR-RESOURCE.openai.azure.com/` or `https://YOUR-RESOURCE.services.ai.azure.com/`. It also accepts these with `/openai/v1/` appended. A project URL containing `/api/projects/...` is not the resource endpoint this adapter needs. Sovereign-cloud endpoints and Microsoft Entra authentication require a separate adapter change.

## 3. Configure the backend

From the repository root:

```bash
cd backend
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

If `.env` does not exist, copy `.env.example` to `.env` once. Preserve any existing configuration. Edit `backend/.env` locally:

```dotenv
APP_ENV=development
FRONTEND_ORIGIN=http://localhost:5173
LLM_PROVIDER=mock

AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=matchpulse-tactical
AZURE_OPENAI_API_KEY=YOUR-RESOURCE-KEY
AZURE_OPENAI_TIMEOUT_SECONDS=15
AZURE_OPENAI_MAX_OUTPUT_TOKENS=2048
```

Replace the three Azure values with your actual resource details. The deployment setting is the name you assigned in Foundry, not automatically the model's catalog name. Keep the key in the ignored backend `.env`; do not commit it, put it in a `VITE_*` variable, or paste it into chat. Environment variables already set in your shell take precedence over `.env`.

## 4. Run the offline check

From `backend/`, with the virtual environment active:

```bash
python scripts/check_azure.py
```

Expected status: `configuration_ready`, with `deployment_access: not_checked`. This checks local field shapes only and makes no network request. Missing/invalid fields produce `configuration_required` or `settings_invalid` and a nonzero exit code. Credentials and raw input values are omitted from the report.

## 5. Verify actual deployment access

```bash
python scripts/check_azure.py --live
```

This sends **one actual model request**, consuming deployment tokens. It does not retry automatically or fall back to mock. It can run while `LLM_PROVIDER=mock`, so leave the normal API on mock until verification succeeds.

A successful report includes these fields; its elapsed time varies:

```json
{
  "check": "azure_openai",
  "live_requested": true,
  "deployment_access": "verified",
  "provider_enabled": false,
  "provider": "azure",
  "event_id": "evt-064",
  "evidence_count": 14,
  "validation_status": "validated",
  "status": "live_verified"
}
```

`provider_enabled: false` is expected while the normal API is configured for mock. `live_verified` establishes that one request reached the deployment, produced a structured candidate, and passed the same local trust checks used by event processing. It does not query credit balance or quota inventory, or guarantee future service availability. `candidate_rejected` means Azure responded but its claims failed trust checks; do not treat it as a successful analysis check.

## 6. Enable Azure processing

After `live_verified`, change `LLM_PROVIDER=azure` in `backend/.env` and restart FastAPI:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In Postman, send the existing `POST http://127.0.0.1:8000/events/process` request:

```json
{
  "match_id": "match-demo-01",
  "event_id": "evt-064",
  "audience": "analyst",
  "language": "en"
}
```

Check `result_source: runtime`, `provider: azure`, and `agent_trace[1].output.actual_provider: azure`. Source facts remain length 44.28, progression 40, and one annotated line bypassed. Inspect validation and warnings as well as the HTTP status.

Only the Tactical Explainer calls Azure. Match Intelligence computes source facts locally; Trust & Personalization checks the candidate locally and renders controlled English/French templates. This milestone does not claim three independent LLM calls or free-form model-generated explanations.

The normal API deliberately recovers from expected Azure failures with `provider: fallback` and a visible reason. HTTP 200 or a healthy `/health` response therefore does not establish Azure access. The dashboard starts in API mode and shows provider provenance. Select Samples explicitly to use the offline corpus. See [runtime integration](integration.md).

## Diagnostics

| Safe reason/status | What to check |
| --- | --- |
| `configuration_required` / `azure_configuration` | Endpoint, actual deployment name, and key in backend configuration. No Azure request is made for this failure. |
| `settings_invalid` | The listed setting names, especially timeout (2–60 seconds), output limit (256–8192), and provider (`mock` or `azure`). |
| `azure_auth` | Resource API key and endpoint belong to the same resource. |
| `azure_forbidden` | Resource access, network rules, and whether key authentication is enabled. This adapter uses a resource API key. |
| `azure_deployment` | Deployment exists on this endpoint and its name matches exactly. |
| `azure_rate_limit` | Deployment quota and current rate usage in your subscription. |
| `azure_bad_request` | Selected model supports Responses and strict structured outputs. |
| `azure_network` / `azure_timeout` | Connectivity, DNS/proxy, resource network access, and deployment availability. |
| `azure_incomplete` | Output token limit and model completion behavior. |
| `azure_refusal` / `azure_invalid_response` | Model compatibility; the returned content was not published as an insight. |
| `candidate_rejected` | Structured claims conflicted with canonical evidence/rules. Inspect the normal API's trust trace; no unchecked claims are accepted. |
| `azure_server` / `azure_http` | Service availability or an unexpected response from the configured endpoint. |

Diagnostics use safe local codes instead of returning upstream error bodies. Share the preflight JSON when troubleshooting; do not share the key or your `.env`.

## Completion checks

- Active subscription and remaining credit checked in your own account.
- One compatible deployment exists with usable quota.
- Offline check returns `configuration_ready`.
- Explicit live check returns `live_verified` without fallback.
- After enabling Azure and restarting FastAPI, Postman shows `provider: azure` and an accepted candidate.
- Default mock mode and the sample dashboard still work independently of Azure.

Run the automated checks from `backend/`:

```bash
python -m pytest -q
python scripts/export_contract.py --check
python scripts/export_dashboard_samples.py --check
```

Automated Azure tests use HTTPX mock transports. They verify requests, trust rejection, timeouts, HTTP failures, fallback provenance, and secret-safe diagnostics without calling your subscription. They do not replace the live check.

## Microsoft references

- [Azure for Students](https://azure.microsoft.com/en-us/free/students)
- [Education credit FAQ](https://learn.microsoft.com/en-us/azure/education-hub/faq)
- [Deploy models in Foundry](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/deploy-foundry-models)
- [Azure OpenAI v1 lifecycle and resource endpoints](https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle)
- [Responses API: supported models, regions, and request format](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses)
- [Structured outputs and supported JSON Schema subset](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs)
- [Azure OpenAI quotas and limits](https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits)
