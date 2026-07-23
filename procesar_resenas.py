#!/usr/bin/env python3
"""Pipeline de limpieza y análisis de reseñas de FlowApp.

Requisitos funcionales cubiertos:
  FR1 Limpieza de texto (minúsculas, sin emojis/caracteres especiales, sin
      espacios redundantes).
  FR2 Deduplicación de filas exactas (misma reseña re-ingresada a propósito).
  FR3 Manejo explícito y trazable de nulos y ratings inválidos (nunca se
      descartan en silencio).
  FR4 Palabras más frecuentes por nivel de rating (excluyendo stopwords).
  FR5 Resumen estadístico: media, mediana, moda, desviación estándar y
      distribución de ratings.
  FR6 Reporte de calidad de datos (auditoría de lo corregido/descartado).

Uso:
    python3 procesar_resenas.py [--input RUTA_CSV] [--outdir DIR] [--top-n N]

Sin dependencias externas: solo librería estándar (funciona en cualquier
entorno con Python 3.9+, sin necesidad de instalar pandas).
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from limpieza import (
    clave_duplicado_exacto,
    limpiar_texto,
    normalizar_rating,
    tokenizar_para_frecuencia,
)

logger = logging.getLogger("procesar_resenas")

COLUMNAS_ESPERADAS = {"usuario", "fecha", "texto", "rating"}


def leer_filas(ruta_csv: Path) -> list[dict]:
    with ruta_csv.open(encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        columnas = set(lector.fieldnames or [])
        faltantes = COLUMNAS_ESPERADAS - columnas
        if faltantes:
            raise ValueError(f"Faltan columnas esperadas en el CSV: {faltantes}")
        return list(lector)


def procesar(filas_crudas: list[dict]) -> tuple[list[dict], dict]:
    """Limpia, normaliza y deduplica. Devuelve (filas_procesadas, reporte)."""
    vistos: set[tuple] = set()
    filas_procesadas: list[dict] = []

    duplicados_exactos_eliminados = 0
    textos_vacios = 0
    ratings_invalidos_detalle: Counter = Counter()
    ratings_recuperados_texto: Counter = Counter()

    for fila in filas_crudas:
        usuario = fila.get("usuario") or ""
        fecha = fila.get("fecha") or ""
        texto_original = fila.get("texto") or ""
        rating_raw = fila.get("rating") or ""

        clave = clave_duplicado_exacto(usuario, fecha, rating_raw, texto_original)
        if clave in vistos:
            duplicados_exactos_eliminados += 1
            continue
        vistos.add(clave)

        texto_limpio = limpiar_texto(texto_original)
        if not texto_limpio:
            textos_vacios += 1

        rating = normalizar_rating(rating_raw)
        if not rating.valido:
            ratings_invalidos_detalle[rating.valor_original or "(vacío)"] += 1
        elif rating.recuperado_de_texto:
            ratings_recuperados_texto[rating.valor_original] += 1

        filas_procesadas.append({
            "usuario": usuario,
            "fecha": fecha,
            "texto_original": texto_original,
            "texto_limpio": texto_limpio,
            "rating_original": rating_raw,
            "rating_normalizado": rating.valor,
            "rating_invalido": not rating.valido,
            "texto_vacio": not texto_limpio,
        })

    reporte_calidad = {
        "filas_leidas": len(filas_crudas),
        "filas_duplicadas_exactas_eliminadas": duplicados_exactos_eliminados,
        "filas_finales": len(filas_procesadas),
        "textos_vacios": textos_vacios,
        "ratings_invalidos_total": sum(ratings_invalidos_detalle.values()),
        "ratings_invalidos_detalle": dict(ratings_invalidos_detalle),
        "ratings_recuperados_de_texto": dict(ratings_recuperados_texto),
    }
    return filas_procesadas, reporte_calidad


def calcular_resumen_estadistico(filas: list[dict]) -> dict:
    ratings_validos = [
        f["rating_normalizado"] for f in filas
        if not f["rating_invalido"] and f["rating_normalizado"] is not None
    ]
    total_validos = len(ratings_validos)
    if total_validos == 0:
        return {"total_ratings_validos": 0}

    distribucion = Counter(ratings_validos)
    return {
        "total_ratings_validos": total_validos,
        "ratings_excluidos_del_resumen": len(filas) - total_validos,
        "promedio": round(statistics.mean(ratings_validos), 3),
        "mediana": statistics.median(ratings_validos),
        "moda": statistics.multimode(ratings_validos),
        "desviacion_estandar": (
            round(statistics.stdev(ratings_validos), 3) if total_validos > 1 else 0.0
        ),
        "distribucion_absoluta": {k: distribucion[k] for k in sorted(distribucion)},
        "distribucion_porcentual": {
            k: round(100 * v / total_validos, 2) for k, v in sorted(distribucion.items())
        },
    }


def calcular_palabras_frecuentes_por_rating(filas: list[dict], top_n: int) -> dict:
    contadores: dict[int, Counter] = defaultdict(Counter)
    for f in filas:
        if f["rating_invalido"] or f["texto_vacio"]:
            continue
        tokens = tokenizar_para_frecuencia(f["texto_limpio"])
        contadores[f["rating_normalizado"]].update(tokens)

    return {
        str(rating): contadores[rating].most_common(top_n)
        for rating in sorted(contadores)
    }


def escribir_csv_limpio(filas: list[dict], ruta: Path) -> None:
    campos = [
        "usuario", "fecha", "texto_original", "texto_limpio",
        "rating_original", "rating_normalizado", "rating_invalido", "texto_vacio",
    ]
    with ruta.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


def escribir_palabras_frecuentes_csv(palabras_por_rating: dict, ruta: Path) -> None:
    with ruta.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["rating", "palabra", "frecuencia"])
        for rating, pares in palabras_por_rating.items():
            for palabra, frecuencia in pares:
                escritor.writerow([rating, palabra, frecuencia])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path,
        default=Path(__file__).resolve().parent.parent / "resenas_flowapp.csv",
        help="Ruta al CSV crudo de reseñas.",
    )
    parser.add_argument(
        "--outdir", type=Path, default=Path(__file__).resolve().parent / "output",
        help="Carpeta donde escribir los resultados.",
    )
    parser.add_argument(
        "--top-n", type=int, default=15,
        help="Cantidad de palabras top a reportar por rating.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    args.outdir.mkdir(parents=True, exist_ok=True)

    logger.info("Leyendo %s", args.input)
    filas_crudas = leer_filas(args.input)

    filas, reporte_calidad = procesar(filas_crudas)
    logger.info(
        "Filas leídas=%d duplicadas_eliminadas=%d finales=%d",
        reporte_calidad["filas_leidas"],
        reporte_calidad["filas_duplicadas_exactas_eliminadas"],
        reporte_calidad["filas_finales"],
    )
    logger.info(
        "Ratings inválidos=%d (detalle: %s) | recuperados de texto=%s | textos vacíos=%d",
        reporte_calidad["ratings_invalidos_total"],
        reporte_calidad["ratings_invalidos_detalle"],
        reporte_calidad["ratings_recuperados_de_texto"],
        reporte_calidad["textos_vacios"],
    )

    # Aserciones de calidad de datos: si alguna falla, el pipeline se detiene
    # en vez de publicar resultados silenciosamente corruptos.
    assert reporte_calidad["filas_finales"] <= reporte_calidad["filas_leidas"]
    assert reporte_calidad["filas_finales"] + reporte_calidad["filas_duplicadas_exactas_eliminadas"] \
        == reporte_calidad["filas_leidas"]

    resumen = calcular_resumen_estadistico(filas)
    palabras_por_rating = calcular_palabras_frecuentes_por_rating(filas, args.top_n)

    escribir_csv_limpio(filas, args.outdir / "resenas_limpias.csv")
    escribir_palabras_frecuentes_csv(palabras_por_rating, args.outdir / "palabras_frecuentes_por_rating.csv")
    (args.outdir / "reporte_calidad_datos.json").write_text(
        json.dumps(reporte_calidad, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.outdir / "resumen_estadistico.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.outdir / "palabras_frecuentes_por_rating.json").write_text(
        json.dumps(palabras_por_rating, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    logger.info("Resultados escritos en %s", args.outdir)


if __name__ == "__main__":
    main()
