# 📊 Análisis de Reseñas FlowApp

**Autor:** Diego Arenas (Diegoarenas111@gmail.com)

Limpiador profesional de reseñas de apps. Toma un CSV sucio (~600 filas con emojis, ratings rotos, duplicados) y devuelve: dataset limpio, análisis de palabras frecuentes por rating, stats completos. Sin dependencias externas: solo Python 3.9+.

---

## ⚡ Inicio rápido (3 pasos)

### Paso 1: Descarga y acceso

```bash
# Navega a la carpeta del proyecto
cd /ruta/a/Reto1/resolucion\ de\ reto_Claude

# Verifica que tengas Python 3.9 o superior
python3 --version
# Esperado: Python 3.9+ (se probó con 3.11)
```

### Paso 2: Ejecuta el análisis

**Forma más simple** (recomendada para la primera vez):
```bash
python3 procesar_resenas.py
# Lee de: ../resenas_flowapp.csv (automático)
# Escribe en: ./output/
# Tiempo: ~1 segundo
```

**Con opciones personalizadas**:
```bash
python3 procesar_resenas.py --input otro_dataset.csv --outdir mi_salida/ --top-n 25
```

**Verifica que todo funcione** (tests unitarios):
```bash
python3 tests/test_limpieza.py -v
# Ejecuta 13 checks de limpieza/normalización
# Tiempo: ~0.001s (todo debe pasar ✅)
```

### Paso 3: Revisa los resultados

```bash
cd output/
ls -la
cat resumen_estadistico.json  # estadísticas generales
cat reporte_calidad_datos.json  # qué se limpió/descartó
head -10 palabras_frecuentes_por_rating.csv  # palabras top por rating
```

---

## 📋 Referencia rápida de comandos

```bash
# Correr con parámetros personalizados
python3 procesar_resenas.py --input mi_dataset.csv --outdir salida/ --top-n 20

# Ver logs en tiempo real
python3 procesar_resenas.py 2>&1 | tee reporte.log

# Ejecutar solo los tests
python3 tests/test_limpieza.py -v

# Aumentar el top a 25 palabras por rating
python3 procesar_resenas.py --top-n 25
```

---

## 📁 Qué sale en `output/`

| Archivo | Descripción |
|---|---|
| **resenas_limpias.csv** | Dataset completo procesado: texto limpio, rating normalizado, flags de calidad |
| **reporte_calidad_datos.json** | Auditoría detallada: qué se limpió, descartó y por qué (transaparencia total) |
| **resumen_estadistico.json** | Números: promedio, mediana, moda, desviación estándar, distribución de ratings |
| **palabras_frecuentes_por_rating.csv/.json** | Top-N palabras más frecuentes por cada rating (sin ruido de stopwords) |

## 🎯 Qué "truco" tiene el dataset (y cómo se resolvió)

El CSV es sucio a propósito — parte del reto. Aquí están los problemas encontrados y cómo se manejaron:

| Problema | Casos | Solución |
|----------|-------|----------|
| **Duplicados exactos** | 14 filas | Misma reseña del mismo usuario en la misma fecha. Se elimina, manteniendo la primera. |
| **Ratings vacíos/rotos** | 19 filas | Vacío (9), fuera de rango -1/0/6/7 (7), símbolos `?` o `N/A`. Se marcan como inválidos pero **no se borran**. |
| **Ratings textuales** | 3 filas | `"cinco"` es un 5 válido pero mal formateado. Se recupera automáticamente. |
| **Texto vacío o solo emojis** | 26 filas | Se marca como vacío, se excluye del análisis de palabras, pero la fila se conserva. |

**Principio clave:** Nada se descarta en silencio. Todo queda registrado en `reporte_calidad_datos.json` para auditabilidad total.

---

## 📊 Qué hace exactamente

### Requisitos funcionales (lo que pide el reto)

✅ **Limpieza de texto:** minúsculas, sin emojis/caracteres especiales, espacios duplicados eliminados. Conserva tildes/ñ (quedá español legible, no sopa de caracteres).

✅ **Deduplicación:** elimina filas exactas re-ingresadas por el mismo usuario en la misma fecha.

✅ **Manejo inteligente de ruido:** ratings inválidos, textos vacíos y duplicados no se eliminan silenciosamente — se marcan y se auditan.

✅ **Palabras frecuentes por rating:** top-N palabras para cada nivel (1⭐ a 5⭐), **sin stopwords** (o sea: sin "el/la/que/muy/es", puro ruido).

✅ **Resumen estadístico:** promedio, mediana, moda, desviación estándar, distribución de ratings en números y porcentajes.

✅ **Reporte de calidad:** archivo JSON que explica cada descarte/corrección (transaparencia total).

### Requisitos no funcionales (como lo hace)

🔒 **Reproducibilidad:** mismo input → siempre mismo output. Sin aleatoriedad, sin depender del orden de archivos.

🔒 **Auditabilidad:** cada fila modificada/excluida queda registrada con su motivo. Nunca pierde información.

🔒 **Portabilidad:** cero dependencias — solo Python stdlib. Funciona en cualquier máquina con Python 3.9+.

🔒 **Configurabilidad:** parámetros por CLI (`--input`, `--outdir`, `--top-n`), sin tocar el código.

🔒 **Testabilidad:** lógica de limpieza en funciones puras (`limpieza.py`), I/O separada (`procesar_resenas.py`). 13 tests automáticos.

🔒 **UTF-8 nativo:** emojis, tildes, ñ andan bien de inicio a fin.

🔒 **Fail-fast:** si falta una columna del CSV, el script aborta con error claro. Aserciones internas verifican que los números cierren antes de escribir.

---

## 🏗️ Estructura del código

```
resolucion de reto_Claude/
│
├── procesar_resenas.py        # 🎬 Script principal: orquesta todo
│                              #    → lee CSV → limpia → analiza → escribe resultados
│
├── limpieza.py                # 🧹 Funciones de limpieza (puras, testeables)
│                              #    → limpiar_texto(), normalizar_rating()
│                              #    → tokenizar_para_frecuencia(), dedup keys
│
├── stopwords_es.py            # 📍 Lista de palabras vacías en español
│                              #    (usada para evitar ruido en top-words)
│
├── tests/
│   └── test_limpieza.py       # ✅ 13 tests unitarios (stdlib, sin dependencias)
│
├── output/  (creada al correr)
│   ├── resenas_limpias.csv
│   ├── reporte_calidad_datos.json
│   ├── resumen_estadistico.json
│   ├── palabras_frecuentes_por_rating.csv
│   └── palabras_frecuentes_por_rating.json
│
└── README.md (este archivo)
```

### Por qué esta estructura

- **Separación de responsabilidades:** `limpieza.py` no sabe de archivos (puro cálculo), `procesar_resenas.py` hace I/O.
- **Testeable:** puedes probar la limpieza sin tocar el CSV.
- **Reutilizable:** alguien más puede importar `limpieza.py` en su propio script.
- **Mantenible:** cada archivo hace una cosa bien.

---

## 📈 Ejemplo de salida

Después de correr `python3 procesar_resenas.py`, verás algo así:

```
INFO: Leyendo /ruta/a/resenas_flowapp.csv
INFO: Filas leídas=597 duplicadas_eliminadas=14 finales=583
INFO: Ratings inválidos=19 (detalle: {'(vacío)': 9, '-1': 2, ...}) 
       | recuperados de texto={'cinco': 3} 
       | textos vacíos=26
INFO: Resultados escritos en ./output
```

**Archivo: `resumen_estadistico.json`**
```json
{
  "total_ratings_validos": 564,
  "promedio": 3.871,
  "mediana": 4.0,
  "moda": [5],
  "desviacion_estandar": 1.196,
  "distribucion_absoluta": {
    "1": 34,
    "2": 53,
    "3": 81,
    "4": 180,
    "5": 216
  },
  "distribucion_porcentual": {
    "1": 6.03,
    "2": 9.4,
    "3": 14.36,
    "4": 31.91,
    "5": 38.3
  }
}
```

**Archivo: `palabras_frecuentes_por_rating.csv`** (muestra)
```
rating,palabra,frecuencia
1,experiencia,11
1,recomiendo,10
1,dinero,10
1,app,9
1,terrible,9
5,excelente,42
5,funciona,38
5,perfecta,35
5,encanta,28
```

---

## ❓ Preguntas frecuentes

**P: ¿Qué pasa si no tengo Python 3.9?**
R: Baja Python 3.11+ de [python.org](https://python.org). Este código es compatible con 3.9-3.13.

**P: ¿Por qué no usas Pandas?**
R: El dataset es pequeño (597 filas). Pandas es overkill. Stdlib es más rápido aquí y **sin dependencias**.

**P: ¿Puedo cambiar la ruta del input/output?**
R: Sí, usa `--input` y `--outdir`:
```bash
python3 procesar_resenas.py --input /ruta/otro.csv --outdir /salida/
```

**P: ¿Qué hacen los tests?**
R: Verifican que `limpiar_texto()`, `normalizar_rating()`, etc. funcionen correctamente. Son la red de seguridad.

**P: ¿Cómo veo logs más detallados?**
R: Cambia el nivel en `procesar_resenas.py` línea ~52 de `INFO` a `DEBUG`.

---

## 🤝 Contacto

Si hay problemas o mejoras, contacta: **Diego Arenas** (Diegoarenas111@gmail.com)
