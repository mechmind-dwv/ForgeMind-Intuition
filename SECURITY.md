# Seguridad en ForgeMind Intuition

## Versiones con soporte

El proyecto se encuentra en fase experimental. Se priorizan correcciones de seguridad para la rama `main` y para la última versión etiquetada cuando exista. Las integraciones full-stack y los despliegues deben evaluarse con una configuración propia antes de manejar datos sensibles.

## Reportar una vulnerabilidad

No publiques vulnerabilidades, tokens, claves, URLs privadas, datos de usuarios ni pruebas de explotación en issues o Discussions públicas. Abre un reporte privado a través de GitHub Security Advisories si está habilitado para el repositorio. Si esa opción no está disponible, contacta directamente con los mantenedores desde la cuenta del proyecto y proporciona únicamente la información necesaria para reproducir el problema.

Incluye una descripción breve, el impacto, las versiones afectadas, pasos de reproducción, condiciones necesarias y una mitigación provisional si la conoces. Puedes omitir datos sensibles y compartirlos solo por un canal privado.

## Credenciales y secretos

Nunca guardes tokens en `.env` versionados, comandos copiados en issues, URLs de Git, capturas, logs o documentación. Si una credencial aparece en un commit o mensaje, revócala inmediatamente, crea una nueva con el mínimo privilegio y revisa el historial. El `.gitignore` del proyecto excluye `.env` y sus variantes, pero esa regla no corrige una credencial ya expuesta.

## Ejecución de código

ForgeMind trabaja con candidatas y oráculos que pueden ejecutar código. No ejecutes entradas no confiables sin aislamiento, límites de recursos y permisos mínimos. La selección de una hipótesis por posterior o ranking no constituye una autorización para ejecutar código destructivo.

## Proceso de respuesta

Los mantenedores confirmarán la recepción cuando sea posible, reproducirán el problema en un entorno aislado, evaluarán impacto y alcance, prepararán una corrección y publicarán una nota cuando la solución esté disponible. No se debe revelar una vulnerabilidad antes de que exista una mitigación razonable.

## Alcance

Esta política cubre el paquete Python, la CLI, el frontend integrado, benchmarks, workflows y documentación oficial del repositorio. Los sistemas externos conectados por cada usuario tienen sus propias políticas y deben reportarse a sus respectivos propietarios.
