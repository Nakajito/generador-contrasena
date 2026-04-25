# CLAUDE.md — Directrices optimizadas

## Modo Plan (por defecto)
- Usar modo plan si tarea >3 pasos o decisiones arquitectónicas.
- Ante cualquier desvío: parar y replanificar.
- Incluir verificación en el plan, no solo construcción.
- Especificar detalles por adelantado.

## Subagentes (contexto limpio)
- Investigación, exploración o análisis paralelo → subagente.
- Un subagente por tarea, ejecución enfocada.

## Mejora continua
- Tras cada corrección del usuario: actualizar `tasks/lessons.md` con el patrón.
- Escribir reglas para evitar repetir el mismo error.
- Revisar lecciones al inicio de cada sesión.

## Verificación antes de finalizar
- No marcar tarea completa sin evidencia de funcionamiento.
- Comparar comportamiento entre versión principal y cambios.
- Preguntar: "¿Un ingeniero senior aprobaría esto?".
- Ejecutar tests, revisar logs, demostrar corrección.

## Elegancia equilibrada
- Para cambios no triviales: pausar y preguntar "¿hay forma más elegante?".
- Si un fix se siente improvisado: "Implementar la solución elegante con lo que sé ahora".
- Omitir esto solo para fixes obvios y simples.

## Corrección autónoma de bugs
- Dado un reporte de bug: simplemente arreglarlo sin pedir ayuda.
- Apuntar a logs, errores, tests fallidos → resolverlos.
- Cero cambio de contexto requerido por el usuario.
- Arreglar CI fallida sin instrucciones adicionales.

## Gestión de tareas
1. Plan → `tasks/todo.md` con ítems verificables.
2. Verificar plan antes de implementar.
3. Marcar progreso.
4. Explicar cambios al final de cada paso.
5. Documentar resultados en `tasks/todo.md`.
6. Lecciones → `tasks/lessons.md`.

## Principios fundamentales
- **Simplicidad**: cambios mínimos, código mínimo afectado.
- **Sin pereza**: encontrar causa raíz, nada temporal. Estándares senior.
- **Impacto mínimo**: tocar solo lo necesario, evitar regresiones.