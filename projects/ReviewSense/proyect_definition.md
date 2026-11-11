# Customer Experience Intelligence Platform

**Documento:** Definición inicial del proyecto
**Versión:** 0.1  
**Estado:** Diseño inicial  
**Lenguaje principal:** Python

## 1. Objetivo

Construir una plataforma de análisis de contenido orientada a Customer Experience (CX), capaz de recibir reseñas y comentarios provenientes de distintas fuentes, identificar cuáles representan experiencias de clientes y estimar su valoración en una escala de 1 a 5 estrellas.

La plataforma tendrá dos capacidades principales:

1. Recibir reseñas con valoraciones conocidas para construir y mantener datasets etiquetados, validar modelos y habilitar procesos controlados de reentrenamiento.
2. Recibir textos sin valoración, identificar si representan una reseña y, cuando corresponda, inferir una valoración numérica con decimales.

El objetivo técnico es desarrollar una solución progresiva que permita estudiar e implementar conceptos de Machine Learning Engineering, Backend Engineering, Distributed Systems y MLOps.

## 2. Alcance funcional

### 2.1 Ingesta de datos etiquetados

El sistema recibirá reseñas que contienen:

- Texto.
- Rating real.
- Identificador externo.
- Fuente de origen.
- Fecha de publicación, cuando esté disponible.

Estos datos se validarán y almacenarán para su posterior utilización en entrenamiento y evaluación.

La recepción de datos no implica reentrenamiento inmediato.

### 2.2 Análisis de contenido sin etiquetar

El sistema recibirá comentarios o publicaciones de fuentes como redes sociales, plataformas de opiniones y otros canales.

El procesamiento tendrá dos etapas:

1. Clasificación: determinar si el contenido representa una reseña de una experiencia.
2. Regresión: si es una reseña, estimar su valoración entre 1 y 5 estrellas.

La valoración se conservará con decimales.

### 2.3 Mejora continua

Los datos etiquetados incorporados podrán utilizarse para:

- Evaluar el rendimiento de los modelos.
- Detectar cambios en la distribución de los datos.
- Entrenar nuevas versiones.
- Comparar modelos candidatos.
- Promover nuevas versiones bajo criterios de aceptación.

La actualización de modelos será controlada y desacoplada de las solicitudes HTTP.

## 3. Definición de los problemas de Machine Learning

### 3.1 Review Classification

**Objetivo:** identificar si un texto representa una reseña de una experiencia.

- Tipo: clasificación binaria.
- Input: texto.
- Output: `is_review`.
- Etiquetas: `review` y `not_review`.

El modelo deberá entrenarse con ejemplos de ambas categorías.

El dataset Yelp proporciona reseñas positivas para esta tarea, pero no suficientes ejemplos negativos. Será necesario incorporar otra fuente o crear un conjunto adicional de comentarios etiquetados.

### 3.2 Rating Regression

**Objetivo:** estimar el rating que correspondería a una reseña.

- Tipo: regresión supervisada.
- Input: texto.
- Target: rating original entre 1 y 5.
- Output: valor numérico entre 1 y 5.

La fuente inicial de entrenamiento será Yelp Open Dataset.

La predicción no se interpretará como el rating real que habría asignado el autor, sino como una estimación del rating esperado según los patrones aprendidos.

### 3.3 Modelos independientes

Los dos modelos tendrán pipelines, métricas, versiones y ciclos de actualización independientes.

El resultado del clasificador determinará si se ejecuta el regresor.

## 4. Fuentes de datos

### 4.1 Yelp Open Dataset

Archivo principal:

`yelp_academic_dataset_review.json`

Campos iniciales:

- `review_id`
- `user_id`
- `business_id`
- `stars`
- `text`
- `date`

Uso:

- Entrenamiento del Rating Regressor.
- Ejemplos positivos para Review Classification.
- Evaluación y experimentación.

La utilización del dataset debe respetar su acuerdo de uso. No se asumirá que puede redistribuirse o utilizarse comercialmente.

### 4.2 Dataset de comentarios no correspondientes a reseñas

Se incorporará una fuente adicional para entrenar Review Classification.

Deberá contener textos que representen consultas, anuncios, noticias, conversaciones y otros contenidos que no describan una experiencia de consumo.

Se deberá registrar la procedencia y las reglas de etiquetado.

### 4.3 Datos de producción

Los datos recibidos por la API se almacenarán junto con su procedencia, fecha y estado de validación.

Las predicciones sin rating real no se considerarán etiquetas válidas para el entrenamiento supervisado del regresor.

## 5. Arquitectura lógica

### Flujo A: datos etiquetados

`Client -> Labeled Reviews API -> Validation -> Storage -> Dataset Preparation -> Training/Evaluation -> Model Registry`

### Flujo B: inferencia

`Client -> Analysis API -> Review Classifier -> Rating Regressor (if review) -> Response`

### Ciclo de actualización

`New labeled data -> Data validation -> Dataset version -> Candidate training -> Evaluation -> Model promotion -> Serving`

Los procesos de entrenamiento y evaluación serán asíncronos.

## 6. API inicial

### 6.1 Recepción de reseñas etiquetadas

**POST `/v1/feedback/labeled-reviews`**

Ejemplo:

```json
{
  "source": "yelp",
  "reviews": [
    {
      "external_id": "review-123",
      "text": "Amazing food and excellent service!",
      "stars": 5,
      "timestamp": "2026-10-15T12:30:00Z"
    }
  ]
}
```

Respuesta:

```json
{
  "received": 1,
  "accepted": 1,
  "rejected": 0,
  "batch_id": "batch-001",
  "status": "accepted"
}
```

Responsabilidades:

- Validar estructura y campos.
- Verificar rating entre 1 y 5.
- Validar texto y tamaño máximo.
- Detectar duplicados.
- Registrar fuente y procedencia.
- Persistir registros.
- Incorporar registros elegibles al proceso de preparación de datasets.

No ejecutará entrenamiento sincrónico.

### 6.2 Análisis de contenido

**POST `/v1/predictions/analyze`**

Ejemplo:

```json
{
  "source": "social_media",
  "items": [
    {
      "external_id": "post-001",
      "text": "I had a wonderful experience at this hotel!"
    },
    {
      "external_id": "post-002",
      "text": "Does anyone know if the hotel has parking?"
    }
  ]
}
```

Respuesta:

```json
{
  "results": [
    {
      "external_id": "post-001",
      "classification": {
        "is_review": true,
        "probability": 0.97
      },
      "rating": {
        "predicted_stars": 4.65
      },
      "model_versions": {
        "classifier": "review-classifier-1.0",
        "regressor": "rating-regressor-1.0"
      }
    },
    {
      "external_id": "post-002",
      "classification": {
        "is_review": false,
        "probability": 0.96
      },
      "rating": null,
      "model_versions": {
        "classifier": "review-classifier-1.0"
      }
    }
  ]
}
```

Las probabilidades y valoraciones del ejemplo son ilustrativas.

La API deberá:

- Validar requests.
- Soportar múltiples elementos por solicitud.
- Clasificar cada texto.
- Ejecutar regresión solamente cuando corresponda.
- Devolver resultados individualizados.
- Informar las versiones de los modelos utilizados.
- No modificar el rating estimado mediante redondeo.

Se contempla incorporar un estado de incertidumbre para los casos en que el clasificador no pueda determinar con suficiente seguridad si un texto es una reseña.

## 7. Estrategia de Machine Learning

### 7.1 Primeros modelos

Review Classification:

- Baseline simple.
- TF-IDF.
- Logistic Regression.
- Evaluación con precision, recall, F1 y matriz de confusión.

Rating Regression:

- Baseline de predicción del promedio.
- TF-IDF.
- Ridge Regression.
- Evaluación con MAE, RMSE y distribución de errores.

### 7.2 Evaluación

Los datasets se dividirán en entrenamiento, validación y test.

El conjunto de test deberá mantenerse separado de los procesos de selección de hiperparámetros.

Se evaluará una separación temporal para simular la predicción de reseñas futuras.

### 7.3 Reproducibilidad

Cada experimento deberá registrar:

- Código y versión.
- Dataset y versión.
- Features y preprocessing.
- Hiperparámetros.
- Seed cuando corresponda.
- Versiones de librerías.
- Métricas.
- Artefactos generados.

### 7.4 Promoción de modelos

Un modelo candidato solamente podrá reemplazar al modelo vigente si supera criterios de aceptación definidos.

Se contempla:

- Comparación con el modelo actual.
- Validación de calidad.
- Registro de versiones.
- Despliegue controlado.
- Rollback.

## 8. Persistencia

Se utilizará PostgreSQL para almacenar inicialmente:

- Registros etiquetados.
- Procedencia de datos.
- Lotes de ingesta.
- Predicciones.
- Versiones de modelos utilizadas.
- Estado de validación de registros.

Los artefactos de modelos y datasets versionados podrán almacenarse separadamente.

Las entidades y esquemas se definirán durante la etapa de implementación.

## 9. Stack tecnológico objetivo

| Área | Tecnología |
|---|---|
| Lenguaje | Python |
| API | FastAPI |
| ML | scikit-learn |
| NLP inicial | TF-IDF |
| Base de datos | PostgreSQL |
| Experiment tracking | MLflow |
| Model registry | MLflow |
| Workers | Python |
| Contenedores | Docker |
| Mensajería futura | Kafka |
| Orquestación futura | Airflow |
| Infraestructura futura | AWS |
| Orquestación de contenedores futura | Kubernetes |

Las tecnologías se incorporarán de manera incremental, evitando complejidad prematura.

## 10. Monitoring y mejora continua

Se monitorizarán tres dimensiones:

### Infraestructura

- Latencia.
- Throughput.
- Errores HTTP.
- Consumo de CPU y memoria.
- Disponibilidad.

### Datos

- Cambios de distribución.
- Valores faltantes.
- Longitud de textos.
- Cambios de idioma.
- Calidad de las fuentes.

### Modelos

- Métricas de clasificación.
- MAE y RMSE de regresión.
- Data drift.
- Concept drift.
- Rendimiento cuando se disponga de ratings reales.

Las predicciones sin etiqueta no permitirán calcular directamente el error real del modelo.

## 11. Consideraciones de seguridad y calidad

- Validación estricta de entradas.
- Límites de tamaño y cantidad de registros.
- Protección de datos personales.
- Control de acceso a endpoints de ingesta.
- Trazabilidad de procedencia.
- Detección de duplicados.
- Registro de versiones de modelos.
- Separación de datos de entrenamiento y evaluación.
- Evitar que datos no verificados ingresen directamente al conjunto de entrenamiento.

## 12. Roadmap de implementación

1. Exploración de datasets y definición de etiquetas.
2. Entrenamiento y evaluación de Review Classifier.
3. Entrenamiento y evaluación de Rating Regressor.
4. Construcción de pipelines reproducibles.
5. Implementación de API y persistencia.
6. Procesamiento asíncrono y MLflow.
7. Model Registry y promoción controlada.
8. Docker y despliegue.
9. Kafka, Airflow y procesamiento distribuido.
10. Kubernetes, AWS y monitoring.
11. Drift detection y retraining.

## 13. Criterios iniciales de éxito

El MVP deberá poder:

- Recibir reseñas etiquetadas.
- Validar y almacenar registros.
- Entrenar ambos modelos.
- Evaluar ambos modelos con conjuntos independientes.
- Recibir comentarios sin rating.
- Identificar si un texto representa una reseña.
- Inferir ratings decimales cuando corresponda.
- Devolver versiones de modelos utilizadas.
- Mantener separados los procesos de inferencia y entrenamiento.

## 14. Principio arquitectónico

La plataforma deberá separar claramente:

- Data ingestion.
- Dataset preparation.
- Model training.
- Model evaluation.
- Model registry.
- Model serving.
- Monitoring.

Esta separación permitirá evolucionar cada componente independientemente y escalar la solución sin convertir la API de inferencia en un sistema de entrenamiento acoplado.

**Fin del documento — Versión 0.1**


-----


Me parece una mejora importante. Estás separando dos situaciones que tienen distinta naturaleza y, sobre todo, distintos niveles de confianza sobre el origen del contenido.

También agregás algo interesante desde el punto de vista de ML Engineering: la posibilidad de comparar sistemáticamente un modelo entrenado con una API de LLM como evaluador alternativo. Esto nos permitirá estudiar diferencias entre modelos especializados y modelos fundacionales.

Mantendría intacta la documentación anterior y aplicaría únicamente los siguientes cambios.

# 1. Nuevo diseño de los endpoints

Pasamos de dos endpoints principales a tres endpoints, dos de inferencia y uno de ingesta etiquetada.

A. Ingesta de reseñas con rating conocido

`POST /v1/feedback/labeled-reviews`

Recibe reseñas con estrellas reales. Alimenta datasets de entrenamiento y evaluación.

B. Inferencia sobre reseñas verificadas como tales

`POST /v1/predictions/reviews`

Recibe textos que ya sabemos que son reseñas. Ejecuta directamente nuestro Rating Regressor.

C. Análisis de contenido de fuentes heterogéneas

`POST /v1/predictions/content`

Recibe comentarios de redes sociales y otras fuentes. Ejecuta una API de LLM que devuelve clasificación y rating estimado estructurados.

La diferencia principal es que el segundo endpoint no necesita clasificar si el texto es una reseña. Esa información ya viene garantizada por la fuente.

El tercero utiliza un LLM para resolver ambas tareas en una sola interacción.

# 2. Cambios en la arquitectura

La arquitectura de inferencia quedaría así:

Contenido entrante

Texto + fuente de origen

Fuente confiable

Reviews

Formulario de reseñas, Yelp u otra fuente que garantice que es una review.

Rating Regressor

Modelo ML propio

Rating decimal

Fuente incierta

Social / comentarios

Redes sociales, foros y fuentes heterogéneas.

LLM API

Clasificación + estimación de estrellas en una llamada.

Resultado estructurado

Resultados normalizados

Clasificación + rating estimado + procedencia + versión del modelo

# 3. Modificaciones puntuales a la documentación

Estos son los apartados que cambiaría en el documento v0.1.

### Sección 1 — Objetivo

Reemplazar la descripción de las dos capacidades de inferencia por:

- Inferencia directa sobre reseñas cuya naturaleza está garantizada por la fuente.
- Análisis de contenido heterogéneo mediante una API de LLM que determina si el contenido es una reseña y, en caso afirmativo, estima su valoración.

La ingesta de datos etiquetados sigue siendo independiente.

### Sección 2 — Alcance funcional

Agregar dos subsecciones:

2.2 Inferencia sobre reseñas verificadas

El sistema recibe textos que provienen de fuentes que garantizan que el contenido es una reseña. Ejecuta directamente el Rating Regressor, sin necesidad de clasificación previa.

2.3 Análisis de contenido heterogéneo

El sistema recibe textos de fuentes en las que no se puede garantizar que sean reseñas.

Una API de LLM deberá producir una respuesta estructurada que contenga:

- Si el contenido representa una reseña.
- Una valoración estimada entre 1 y 5, con decimales, cuando corresponda.
- Una explicación breve de la clasificación, opcional.
- Un estado de incertidumbre cuando el modelo no pueda determinarlo.

La inferencia de rating se realizará en la misma interacción con el LLM, no mediante una segunda llamada.

### Sección 3 — Definición de los problemas de ML

Aquí haría una modificación conceptual importante.

- Rating Regression: continúa siendo nuestro modelo ML entrenado con Yelp.
- Review Classification: deja de ser inicialmente un modelo ML propio obligatorio y pasa a ser una capacidad proporcionada por el LLM en el flujo de contenido heterogéneo.

Podremos desarrollar posteriormente un clasificador propio para compararlo con el LLM, pero no será necesario para el MVP.

### Sección 4 — Fuentes de datos

Agregar una distinción entre:

- Datos con rating real: Yelp y fuentes verificadas.
- Datos sin rating real: comentarios y publicaciones de redes sociales.
- Datos con valoración inferida por LLM: resultados generados por el proveedor externo.

Esta última categoría no debe confundirse con datos etiquetados.

### Sección 5 — Arquitectura lógica

Reemplazar el flujo B anterior por dos flujos independientes:

Flujo B: reseñas verificadas

`Client -> Reviews API -> Rating Regressor -> Prediction Response`

Flujo C: contenido heterogéneo

`Client -> Content API -> LLM API -> Structured Response -> Normalized Result`

El flujo de entrenamiento permanece sin cambios.

### Sección 6 — API inicial

Esta es la modificación más importante desde el punto de vista de implementación.

Endpoint 1 — Sin cambios

`POST /v1/feedback/labeled-reviews`

Endpoint 2 — Nuevo

`POST /v1/predictions/reviews`

Request:

```
{
  "source": "verified_review_form",
  "items": [
    {
      "external_id": "review-001",
      "text": "The food was excellent and the service was great."
    }
  ]
}
```

Response:

```
{
  "results": [
    {
      "external_id": "review-001",
      "predicted_stars": 4.72,
      "prediction_method": "ml_regression",
      "model_version": "rating-regressor-1.0"
    }
  ]
}
```

Endpoint 3 — Nuevo

`POST /v1/predictions/content`

Request:

```
{
  "source": "social_media",
  "items": [
    {
      "external_id": "post-001",
      "text": "I had an amazing experience at this hotel!"
    },
    {
      "external_id": "post-002",
      "text": "Does anyone know if this hotel has parking?"
    }
  ]
}
```

Respuesta estructurada del LLM (contrato conceptual):

```
{
  "results": [
    {
      "external_id": "post-001",
      "is_review": true,
      "predicted_stars": 4.8,
      "explanation": "The author describes a positive personal experience."
    },
    {
      "external_id": "post-002",
      "is_review": false,
      "predicted_stars": null,
      "explanation": "The author is asking for information."
    }
  ]
}
```

Los valores son ilustrativos.

Importante: la respuesta del proveedor LLM deberá validarse contra un esquema JSON estricto. No debemos confiar ciegamente en que el proveedor siempre devolverá un JSON válido.

### Sección 7 — Estrategia de Machine Learning

Agregar una nueva línea de experimentación:

Comparación entre Rating Regressor y LLM

Cuando dispongamos de un conjunto de reseñas con ratings reales, enviaremos exactamente los mismos textos a ambos sistemas:

- Modelo propio de regresión.
- LLM con instrucciones de estimación de estrellas.

Compararemos:

| Métrica              | Modelo ML       | LLM        |
| -------------------- | --------------- | ---------- |
| MAE                  | Sí              | Sí         |
| RMSE                 | Sí              | Sí         |
| Error por rating     | Sí              | Sí         |
| Latencia             | Sí              | Sí         |
| Coste por predicción | Infraestructura | Tokens/API |
| Consistencia         | Sí              | Sí         |

Así podremos determinar si el LLM realmente aporta valor o si nuestro modelo especializado es suficientemente bueno.

Una precaución: los ratings que devuelve el LLM son predicciones, no etiquetas reales. No los utilizaremos automáticamente para evaluar el modelo ML como si fueran ground truth.

### Sección 8 — Persistencia

Agregar a las predicciones:

- Método de inferencia (`ml_regression` o `llm`).
- Proveedor LLM.
- Modelo LLM utilizado.
- Versión del prompt.
- Versión del esquema de respuesta.
- Rating estimado.
- Clasificación de contenido.
- Fecha de predicción.

Esto será fundamental para comparar resultados a lo largo del tiempo.

### Sección 9 — Stack tecnológico

Agregar:

| Componente                          | Tecnología                       |
| ----------------------------------- | -------------------------------- |
| Inferencia de contenido heterogéneo | API de LLM externa               |
| Structured output                   | JSON Schema / Structured Outputs |
| Integración LLM                     | Cliente HTTP o SDK del proveedor |

No necesitamos decidir todavía entre OpenAI, Anthropic u otro proveedor.

### Sección 10 — Monitoring

Agregar métricas específicas para el LLM:

- Latencia de respuesta.
- Errores de API.
- Consumo de tokens.
- Coste por solicitud.
- Respuestas inválidas.
- Distribución de clasificaciones.
- Diferencias entre el rating del LLM y el rating real cuando esté disponible.

### Sección 12 — Roadmap

Agregar una etapa de integración LLM después de construir el primer Rating Regressor:

1. Construcción del regresor propio.
2. Implementación del endpoint de reseñas verificadas.
3. Integración del LLM para contenido heterogéneo.
4. Comparación de resultados entre ambos enfoques.
5. Incorporación de monitoring y evaluación.

### Sección 13 — Criterios de éxito

Reemplazar los criterios relacionados con un único endpoint de análisis por:

- Recibir reseñas verificadas y estimar ratings directamente.
- Recibir contenido heterogéneo y clasificarlo mediante LLM.
- Obtener ratings decimales para los contenidos identificados como reseñas.
- Registrar qué motor produjo cada predicción.
- Comparar el rendimiento de ambos métodos utilizando datos con ratings reales.

# 4. Una oportunidad técnica que agregaría al proyecto

Hay algo particularmente interesante en esta nueva arquitectura: podemos convertir el LLM en un benchmark para nuestro modelo ML.

Por ejemplo:

Misma reseña, dos predicciones

Ejemplo ilustrativo

Rating real de Yelp

# 4.0

Modelo propio

# 4.2

Error absoluto: 0.2

LLM

# 3.7

Error absoluto: 0.3

Con suficientes ejemplos podremos responder preguntas interesantes:

- ¿El LLM es mejor que nuestro modelo?
- ¿Es más consistente?
- ¿Tiene sesgos hacia ratings positivos?
- ¿En qué idiomas funciona mejor?
- ¿Conviene utilizar el LLM para todos los textos o reservarlo para casos ambiguos?
- ¿Podemos reemplazarlo por un clasificador propio más económico?

Esto es muy relevante para un puesto de AI Platform: no se trata solamente de consumir modelos, sino de medirlos, compararlos y decidir dónde conviene utilizar cada uno.