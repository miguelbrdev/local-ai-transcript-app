## Plan: Entender flujo para extender la app

Objetivo: comprender el proyecto en el orden real en que se ejecuta para poder añadir funcionalidad sin romper el flujo actual. Enfoque recomendado: estudiar primero runtime y contratos, luego hacer trazas guiadas por cada camino de usuario (audio y texto), y terminar con un mapa de puntos de extensión + riesgos.

**Steps**

1. Preparar entorno mental del sistema (inicio y dependencias).

- Leer README para confirmar arquitectura, puertos y comandos de ejecución.
- Verificar que frontend llama a backend mediante proxy /api y no por URL hardcodeada.
- Resultado esperado: entender qué proceso vive en cada puerto y cómo se comunican.

2. Fase 1. Ciclo de vida al arrancar (orden exacto de ejecución).

- Backend primero: revisar startup en FastAPI (lifespan), inicialización de TranscriptionService, carga de Whisper y conexión LLM.
- Frontend después: revisar montaje de React y primer useEffect para cargar system prompt.
- Dependencia: esta fase bloquea la comprensión de las siguientes porque explica estados iniciales y errores de disponibilidad.

3. Fase 2. Contratos API y estados compartidos.

- Enumerar endpoints y payloads reales: /api/status, /api/system-prompt, /api/transcribe, /api/clean.
- Mapear shape de respuestas backend vs interfaces del frontend para detectar desalineaciones.
- Resultado esperado: tener un contrato único de entrada/salida antes de tocar funcionalidad.

4. Fase 3. Flujo de usuario A (audio: grabación/subida).

- Seguir evento UI -> creación Blob/FormData -> POST /api/transcribe -> transcribe() Whisper -> respuesta rawText.
- Seguir bifurcación useLLM=true -> POST /api/clean -> clean_with_llm() -> cleanedText.
- Identificar dónde se setean estados de loading, errores y limpieza de temporales.
- Dependencia: depende de Fase 1 y 2.

5. Fase 4. Flujo de usuario B (texto pegado).

- Seguir TextInputZone -> onTextSubmit -> setRawText directo -> (opcional) /api/clean.
- Comparar con flujo A para saber qué lógica se comparte y cuál diverge.
- Resultado esperado: detectar mejor punto para agregar features que afecten ambos caminos.

6. Fase 5. Puntos de extensión (dónde agregar tu funcionalidad).

- Clasificar extensiones por capa: UI, API, servicio de IA, configuración.
- Definir estrategia de mínimo riesgo: feature flag o toggle en SettingsPanel, endpoint nuevo o extensión de payload.
- Trazar impacto en tipos de frontend y validación backend.

7. Fase 6. Validación y checklist previo a implementar.

- Ejecutar smoke tests manuales para ambos caminos (audio y texto) con LLM on/off.
- Confirmar fallback cuando falla LLM y comportamiento ante errores de red/permisos de micrófono.
- Salida: checklist de no-regresión para usar después de cada cambio funcional.

**Relevant files**

- /workspaces/ai-transcript-app/README.md — arquitectura, puertos, comandos y limitaciones operativas.
- /workspaces/ai-transcript-app/backend/app.py — entrypoint FastAPI, lifespan, CORS y endpoints.
- /workspaces/ai-transcript-app/backend/transcription.py — integración Whisper + cliente OpenAI-compatible + fallback.
- /workspaces/ai-transcript-app/backend/system_prompt.txt — reglas actuales de limpieza LLM.
- /workspaces/ai-transcript-app/frontend/vite.config.ts — proxy /api y timeouts de peticiones largas.
- /workspaces/ai-transcript-app/frontend/src/main.tsx — bootstrap de React.
- /workspaces/ai-transcript-app/frontend/src/App.tsx — orquestación de estados y flujos principales.
- /workspaces/ai-transcript-app/frontend/src/types/index.ts — contratos de props y respuestas esperadas.
- /workspaces/ai-transcript-app/frontend/src/components/RecordButton.tsx — inicio/parada de grabación.
- /workspaces/ai-transcript-app/frontend/src/components/UploadZone.tsx — drag and drop / selector de audio.
- /workspaces/ai-transcript-app/frontend/src/components/TextInputZone.tsx — camino de texto manual.
- /workspaces/ai-transcript-app/frontend/src/components/SettingsPanel.tsx — control de LLM y edición de prompt.
- /workspaces/ai-transcript-app/frontend/src/components/TranscriptionResults.tsx — renderizado de resultados y copia.
- /workspaces/ai-transcript-app/frontend/src/components/TextBox.tsx — componente base de input/display con loading/copy.

**Verification**

1. Confirmar secuencia startup: backend reporta ready y frontend obtiene default_prompt sin error.
2. Probar flujo audio con LLM on: se ve rawText y luego cleanedText.
3. Probar flujo audio con LLM off: se ve solo rawText y copy funcional.
4. Probar flujo texto con LLM on/off y comparar transiciones de estado.
5. Forzar error de backend (LLM no disponible) y validar fallback/mensajes.
6. Verificar que archivos temporales de audio se limpian tras transcribir.

**Decisions**

- Incluye: comprensión profunda del flujo actual, contratos, estados y puntos de extensión.
- Excluye: implementación de nuevas features en este paso.
- Supuesto: la app corre en local con frontend en 3000 y backend en 8000.

**Further Considerations**

1. Elegir tipo de primera feature para guiar diseño:
   Opción A: feature de UI (bajo riesgo).
   Opción B: feature en endpoint/backend (riesgo medio).
   Opción C: feature de pipeline IA/prompt (riesgo medio-alto).
2. Si la feature impacta ambos caminos (audio/texto), centralizar lógica compartida en App para evitar duplicación.
3. Si la feature depende de proveedor LLM, mantener compatibilidad OpenAI-format como restricción de diseño.
