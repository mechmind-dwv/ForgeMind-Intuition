# Triage de alertas Dependabot

## Alcance

Este informe combina la lista de alertas proporcionada desde GitHub y la auditoría local de `frontend/pnpm-lock.yaml`. GitHub había comprobado los manifiestos contra el commit `e3a3f0a`; la auditoría local encontró **122 avisos**: 2 críticos, 39 altos, 72 moderados y 9 bajos. Las pequeñas diferencias con el contador visible en GitHub pueden deberse al momento de actualización o a la agrupación de alertas del panel.

## Prioridad inmediata

| Prioridad | Familia | Severidad | Alcance | Acción recomendada |
|---|---|---:|---|---|
| P0 | `vitest` | 1 crítica | Desarrollo directo | Actualizar a `>=3.2.6`; no exponer Vitest UI a red y mantener `allowWrite`/`allowExec` desactivados fuera de localhost. La PR #3 actualiza Vitest a 4.x, pero debe validarse el toolchain. |
| P0 | `tar` | 1 crítica + 7 altas | Desarrollo/transitiva | Forzar una versión corregida al menos `>=7.5.21` y regenerar lockfile; verificar que no quedan copias transitivas antiguas. |
| P1 | `vite` | 4 altas + 6 moderadas | Desarrollo/transitiva | Actualizar a una línea corregida; la auditoría local indica `>=7.3.5` para las alertas de la línea Vite 7. La PR #3 propone Vite 8 y requiere pruebas de build/dev server. |
| P1 | `axios` | 11 altas + 16 moderadas + 1 baja | Directa | Actualizar al menos a `>=1.18.0` según el advisory local; revisar que el uso de proxy/redirecciones no maneje credenciales sensibles. La PR #2 incluye una actualización de Axios. |
| P1 | `pnpm` | 11 altas + 12 moderadas | Desarrollo directo | Actualizar a `>=10.34.4` o una versión posterior, y revisar el `packageManager`/Corepack. La PR #2 contiene una actualización amplia; confirmar la versión final en lockfile. |
| P1 | `lodash`/`lodash-es` | 2 altas + 4 moderadas | Transitiva | Actualizar a `>=4.18.0` cuando el árbol lo permita; revisar si existe uso de `_.template`, `_.unset` u `_.omit` con datos no confiables. |
| P1 | `rollup`, `form-data`, `picomatch`, `path-to-regexp` | Altas | Transitivas | Regenerar lockfile mediante la actualización de Vite/Express/Axios y comprobar que se resuelven a `rollup>=4.59.0`, `form-data>=4.0.6`, `picomatch>=4.0.4` y `path-to-regexp>=0.1.13`. |

## Decisión sobre las PR abiertas

Las PR #4 y #5 ya fueron fusionadas después de pasar CI y seguridad. La PR #2 agrupa 42 actualizaciones runtime y es la candidata principal para reducir las alertas directas de Axios, Vite, pnpm y otros paquetes, pero incluye saltos mayores como Express 5, React Day Picker 10, Recharts 3 y Nanoid 6. No debe fusionarse sin ejecutar build, typecheck, Vitest y una prueba manual del servidor.

La PR #3 agrupa 17 actualizaciones de desarrollo, incluyendo Vite 8, TypeScript 7 y Vitest 4. Su rama fue actualizada con `main`; sus checks deben terminar en verde antes de considerar la integración. Debido a que contiene el cambio del servidor de desarrollo y del runner de tests, se recomienda validarla separadamente de la PR #2.

## Controles compensatorios

Las vulnerabilidades de Vite y Vitest son de desarrollo, pero el servidor de desarrollo y Vitest UI no deben exponerse a Internet ni a redes no confiables. El servidor Express de producción ya cuenta con rate limiting para el proxy del motor y el fallback SPA. Dependabot, CodeQL, Dependency Review, pip-audit, Gitleaks y Scorecard siguen activos.

## Orden recomendado

Primero, actualizar y validar la PR #3 como toolchain; después, validar la PR #2 como runtime. Si una PR agrupada falla, dividirla en grupos P0/P1 en lugar de fusionarla parcialmente. Finalmente, ejecutar `pnpm audit`, CI, CodeQL y una prueba de producción del frontend/servidor, y volver a comprobar que las alertas críticas y altas desaparecieron.
