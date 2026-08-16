# Automatización de seguridad

ForgeMind usa varios controles automatizados que trabajan como un bot de seguridad distribuido. Cada control tiene una responsabilidad distinta y permisos mínimos.

| Control | Función | Cuándo actúa | Política |
|---|---|---|---|
| Dependabot | Propone actualizaciones de Python, frontend y GitHub Actions | Semanalmente | Agrupa cambios y limita pull requests abiertos |
| CodeQL | Detecta patrones de vulnerabilidad en Python y TypeScript/JavaScript | Push, pull request y agenda semanal | Publica resultados SARIF en GitHub Security |
| Dependency Review | Revisa cambios de dependencias en pull requests | Cada pull request | Falla ante vulnerabilidades altas y licencias prohibidas |
| pip-audit | Comprueba dependencias Python instaladas | Push, pull request y agenda semanal | Falla si encuentra vulnerabilidades auditables |
| Gitleaks | Busca secretos en el historial y el árbol | Push, pull request y agenda semanal | No imprime valores secretos en los logs |
| OpenSSF Scorecard | Evalúa prácticas de seguridad del repositorio | Push a `main` y agenda semanal | Publica un resultado SARIF; no modifica código |

El bot **no fusiona pull requests, no publica releases y no modifica secretos**. Las alertas deben revisarse junto con las pruebas de CI y el contexto de la vulnerabilidad. Una actualización de Dependabot solo se acepta después de comprobar la suite del paquete Python, el build del frontend y los cambios de contrato.

Los workflows usan `GITHUB_TOKEN` con permisos declarados. El workflow de CI solo lee el contenido; el workflow de seguridad escribe únicamente resultados de seguridad y lee acciones o pull requests cuando es necesario. Las acciones externas deben mantenerse en versiones revisadas y actualizarse mediante Dependabot.

## Respuesta operativa

Una alerta crítica o alta bloquea la revisión hasta confirmar si afecta a una ruta desplegada. Una alerta media requiere triage y una fecha de resolución. Una alerta baja se registra para la siguiente ventana de mantenimiento. Si Gitleaks encuentra un secreto, debe revocarse inmediatamente y no debe copiarse el valor al issue, al commit ni a los logs.

## Rate limiting del servidor Express

El servidor frontend aplica un límite de **60 solicitudes por minuto** al proxy `/api/engine` y de **120 solicitudes por 15 minutos** al fallback SPA que usa `sendFile()`. Las respuestas incluyen cabeceras estándar de rate limiting y devuelven HTTP 429 al superar el umbral. El límite es por instancia y dirección IP; en un despliegue horizontal debe complementarse con un almacén compartido o un gateway perimetral para obtener una cuota global. La prueba `frontend/server/rate-limit.test.ts` verifica el rechazo del fallback tras 120 solicitudes.

## Política de runtime de GitHub Actions

Las acciones principales se mantienen en versiones compatibles con Node.js 24: `actions/checkout@v7`, `actions/setup-python@v7`, `github/codeql-action@v4`, `actions/dependency-review-action@v5`, `gitleaks/gitleaks-action@v3`, `ossf/scorecard-action@v2.4.4` y `softprops/action-gh-release@v3`. Las versiones modernas de checkout y setup-python requieren runners de Actions `v2.327.1` o posterior. GitHub-hosted `ubuntu-latest` satisface este requisito; los runners self-hosted deben actualizarse antes de aplicar estos cambios.
