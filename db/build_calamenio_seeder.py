#!/usr/bin/env python3
"""Genera el archivo de seeds de Calameno a partir del Excel original."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
EXCEL_CANDIDATES = sorted(BASE_DIR.glob("inventarios angel*.xlsx"))
if not EXCEL_CANDIDATES:
    raise FileNotFoundError("No se encontró el Excel de inventarios Calameño.")
EXCEL_PATH = EXCEL_CANDIDATES[0]
OUTPUT_PATH = Path(__file__).with_name("seeds_calamenio.sql")

CATEGORY_MAP = {
    "alimentacion": "Abarrotes y despensa",
    "verduras": "Verduras frescas",
    "condimentos": "Condimentos y salsas",
    "postres": "Postres y repostería",
    "helados": "Helados",
    "congelados": "Congelados",
    "bebidas": "Bebidas no alcohólicas",
    "aguas": "Aguas y minerales",
    "piscos": "Licores - Pisco",
    "ron": "Licores - Ron",
    "jugos": "Jugos y concentrados",
    "destilados": "Licores - Destilados",
    "whisky": "Whisky",
    "vinos": "Vinos",
    "espumantes": "Espumantes",
    "insumo oficina": "Insumos de oficina",
    "bar": "Bar y refrescos",
    "articulos de aseo": "Aseo y limpieza",
    "cervezas": "Cervezas",
    "audio": "Audio y eventos",
    "taller": "Taller y mantenimiento",
    "carnes rojas": "Carnes rojas",
    "plasticos": "Plásticos y desechables",
}

BAR_SECTION_CATEGORY = {
    "BEBIDAS": "Bebidas no alcohólicas",
    "AGUAS": "Aguas y minerales",
    "PISCOS": "Licores - Pisco",
    "RON": "Licores - Ron",
    "JUGOS": "Jugos y concentrados",
    "LICORES": "Licores - Destilados",
    "WHISKY": "Whisky",
    "VINOS": "Vinos",
    "ESPUMANTES": "Espumantes",
    "CERVESAS": "Cervezas",
}

LOCATION_PREFERENCE = {
    "Camara Fria Calameno": {
        "Verduras frescas",
        "Congelados",
        "Carnes rojas",
        "Helados",
    },
    "Operaciones Calameno": {
        "Insumos de oficina",
        "Audio y eventos",
        "Taller y mantenimiento",
    },
    "Bar Calameno": {
        "Bar y refrescos",
    },
}

BAR_ONLY_CATEGORIES = {
    "Bebidas no alcohólicas",
    "Aguas y minerales",
    "Cervezas",
    "Jugos y concentrados",
    "Licores - Pisco",
    "Licores - Ron",
    "Licores - Destilados",
    "Whisky",
    "Vinos",
    "Espumantes",
}

LOCATION_PERSON = {
    "Bodega Calameno": "Angel Calameno",
    "Camara Fria Calameno": "Equipo Cocina Calameno",
    "Bar Calameno": "Equipo Bar Calameno",
    "Operaciones Calameno": "Equipo Operaciones Calameno",
}

MOVEMENT_TIMESTAMP = "2025-11-01 08:00:00+00"

WORD_REPLACEMENTS = {
    "acite": "aceite",
    "ketchut": "ketchup",
    "colunma": "columna",
    "columna2": "",
    "columna4": "",
    "columna8": "",
}

ACCENT_REPLACEMENTS = {
    "aji": "ají",
    "ajies": "ajíes",
    "limon": "limón",
    "pina": "piña",
    "cana": "caña",
    "caneria": "cañería",
    "conac": "coñac",
    "azucar": "azúcar",
    "cafe": "café",
    "cafes": "cafés",
    "te": "té",
    "mani": "maní",
    "pinacolada": "piña colada",
}

UOM_DEFS = {
    "kg": ("Kilogramo", "Peso en kilogramos para alimentos y perecibles"),
    "L": ("Litro", "Volumen expresado en litros"),
    "pz": ("Unidad", "Piezas individuales o empaques contados"),
}

MASS_FALLBACK_CATEGORIES = {"Verduras frescas"}

SKIP_KEYWORDS = {"producto", "proveedor", "marca", "descripcion", "total"}


@dataclass
class MeasureInfo:
    uom: str
    unit_size: float
    label: str


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value).replace("\n", " ").replace("\r", " ").strip()
    if not text:
        return ""
    text = text.replace("�", "ñ")
    text = re.sub(r"\s+", " ", text)
    if text.lower() == "nan":
        return ""
    return text


def format_name(value: object) -> str:
    text = clean_text(value).lower()
    if not text:
        return ""
    for wrong, right in WORD_REPLACEMENTS.items():
        text = text.replace(wrong, right)
    for wrong, right in ACCENT_REPLACEMENTS.items():
        text = re.sub(rf"\b{re.escape(wrong)}\b", right, text)
    formatted = text.title()
    return formatted.strip()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    seen: Dict[str, int] = {}
    new_cols: List[str] = []
    for col in df.columns:
        if isinstance(col, str):
            normalized = re.sub(r"[^0-9a-zA-Z]+", "_", col.strip().lower())
            normalized = re.sub(r"_+", "_", normalized).strip("_")
            if not normalized:
                normalized = "col"
        else:
            normalized = f"col_{len(new_cols)}"
        count = seen.get(normalized, 0)
        if count:
            normalized = f"{normalized}_{count}"
        seen[normalized] = count + 1
        new_cols.append(normalized)
    df.columns = new_cols
    rename_map = {}
    for col in df.columns:
        if col.startswith("gramaje"):
            rename_map[col] = "gramaje"
        elif col.startswith("gramajes"):
            rename_map[col] = "gramaje"
        elif col.startswith("stock_total"):
            rename_map[col] = "stock_total"
        elif col == "stock_t":
            rename_map[col] = "stock_total"
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def pick_stock_column(df: pd.DataFrame) -> str | None:
    for candidate in ("stock_total", "stock_t", "stock"):
        if candidate in df.columns:
            return candidate
    return None


def pick_measure_column(df: pd.DataFrame) -> str | None:
    if "gramaje" in df.columns:
        return "gramaje"
    return None


def parse_number(value: object) -> float | None:
    text = clean_text(value)
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return None


def format_measure_label(text: str) -> str:
    clean = clean_text(text)
    if not clean:
        return ""
    clean = clean.replace(",", ".").lower()
    clean = clean.replace("gramos", "gramos").replace("gramo", "gramo")
    clean = clean.replace("kilos", "kilo")
    clean = clean.replace("litros", "litro")
    clean = clean.replace(" lts", " litro")
    clean = clean.replace("mls", "ml")
    clean = clean.replace("  ", " ")
    clean = re.sub(r"\s*x\s*", " x ", clean)
    return clean.strip().title()


def extract_first_number(text: str) -> float | None:
    match = re.search(r"(\d+(?:[.,]\d+)?)", text)
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", "."))
    except ValueError:
        return None


def convert_amount(value: float, unit: str) -> Tuple[float, str]:
    unit = unit.lower()
    if unit in {"kg", "kilo", "kilos"}:
        return value, "kg"
    if unit in {"g", "gr", "gramo", "gramos"}:
        return value / 1000.0, "kg"
    if unit in {"l", "lt", "lts", "litro", "litros"}:
        return value, "L"
    if unit in {"ml", "cc"}:
        return value / 1000.0, "L"
    if unit in {"gal", "galon", "galón"}:
        return value * 3.785, "L"
    return 1.0, "pz"


def parse_measure(raw: str, category: str) -> MeasureInfo:
    clean = clean_text(raw)
    lowered = clean.lower()
    label = format_measure_label(clean)

    if not clean and category in MASS_FALLBACK_CATEGORIES:
        return MeasureInfo("kg", 1.0, "")
    if not clean:
        return MeasureInfo("pz", 1.0, "")

    pack_match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*(kg|kilo|g|gram|gr|l|lt|litro|ml|cc)\s*x\s*(\d+(?:[.,]\d+)?)",
        lowered,
    )
    if pack_match:
        size = float(pack_match.group(1).replace(",", "."))
        unit = pack_match.group(2)
        qty = float(pack_match.group(3).replace(",", "."))
        base, uom = convert_amount(size, unit)
        return MeasureInfo(uom, base * qty, label)

    reverse_pack = re.search(
        r"(\d+(?:[.,]\d+)?)\s*x\s*(\d+(?:[.,]\d+)?)\s*(kg|kilo|g|gram|gr|l|lt|litro|ml|cc)",
        lowered,
    )
    if reverse_pack:
        qty = float(reverse_pack.group(1).replace(",", "."))
        size = float(reverse_pack.group(2).replace(",", "."))
        unit = reverse_pack.group(3)
        base, uom = convert_amount(size, unit)
        return MeasureInfo(uom, base * qty, label)

    units_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(uni|unid|und|unidad)", lowered)
    if units_match:
        count = float(units_match.group(1).replace(",", "."))
        return MeasureInfo("pz", count, label or f"{int(count)} unidades")

    range_match = re.match(r"(\d+(?:[.,]\d+)?)\s*/\s*(\d+(?:[.,]\d+)?)", lowered)
    if range_match:
        low = float(range_match.group(1).replace(",", "."))
        high = float(range_match.group(2).replace(",", "."))
        avg = (low + high) / 2.0
        base, uom = convert_amount(avg, "g")
        return MeasureInfo(uom, base, label)

    if any(token in lowered for token in ("kg", "kilo")):
        number = extract_first_number(lowered) or 1.0
        return MeasureInfo("kg", number, label)
    if any(token in lowered for token in ("gram", "gr")):
        number = extract_first_number(lowered) or 0.0
        return MeasureInfo("kg", number / 1000.0, label)
    if any(token in lowered for token in ("litro", " lt", " l ")):
        number = extract_first_number(lowered) or 1.0
        return MeasureInfo("L", number, label)
    if "ml" in lowered or "cc" in lowered:
        number = extract_first_number(lowered) or 0.0
        return MeasureInfo("L", number / 1000.0, label)
    if "lata" in lowered or "botella" in lowered or "pack" in lowered:
        return MeasureInfo("pz", 1.0, label)

    numeric_only = re.fullmatch(r"\d+(?:[.,]\d+)?", lowered)
    if numeric_only:
        number = float(numeric_only.group(0).replace(",", "."))
        if number >= 100:
            return MeasureInfo("L", number / 1000.0, label or f"{number:g} Ml")

    return MeasureInfo("pz", 1.0, label)


def build_product_name(product: str, descriptor: str, measure_label: str) -> str:
    base = format_name(product)
    detail = format_name(descriptor)
    if detail and detail.lower() not in base.lower():
        if base.lower().endswith("s") and base.lower()[:-1] == detail.lower():
            base = detail
        else:
            base = f"{base} {detail}"
    if measure_label:
        formatted = measure_label
        if formatted.lower() not in base.lower():
            base = f"{base} {formatted}"
    return re.sub(r"\s+", " ", base).strip()


def determine_category(sheet_key: str, bar_section: str | None) -> str:
    if sheet_key == "bar" and bar_section:
        return BAR_SECTION_CATEGORY.get(bar_section, CATEGORY_MAP["bar"])
    return CATEGORY_MAP.get(sheet_key, "Otros Calameno")


def determine_location(category: str, sheet_key: str) -> str:
    if sheet_key == "bar":
        return "Bar Calameno"
    for location, categories in LOCATION_PREFERENCE.items():
        if category in categories:
            return location
    if category in BAR_ONLY_CATEGORIES:
        return "Bar Calameno"
    return "Bodega Calameno"


def should_skip_product(product: str) -> bool:
    lowered = product.strip().lower()
    if not lowered:
        return True
    if lowered in SKIP_KEYWORDS:
        return True
    if lowered.startswith("columna"):
        return True
    if re.fullmatch(r"[0-9.]+", lowered):
        return True
    return False


def choose_brand(brands: Iterable[str]) -> str:
    cleaned = [b for b in brands if b]
    if not cleaned:
        return "Sin Marca"
    priority = [b for b in cleaned if b.lower() != "sin marca"]
    candidates = priority or cleaned
    return sorted(candidates)[0]


def pick_supplier(value: str) -> str:
    if not value:
        return ""
    if value.lower() in {"sin proveedor", "varios"}:
        return ""
    return value


def assign_sku(products: Dict[Tuple[str, str, str], Dict]) -> List[Dict]:
    ordered = sorted(products.values(), key=lambda p: (p["category"], p["name"]))
    for index, record in enumerate(ordered, start=1):
        record["sku"] = f"CAL-{index:04d}"
        record["brand"] = choose_brand(record["brands"])
    return ordered


def escape(value: str) -> str:
    return value.replace("'", "''")


def build_sql(
    products: List[Dict],
    stock_entries: List[Dict],
    providers: List[str],
    categories: List[str],
) -> str:
    uom_values = ",\n  ".join(
        f"('{escape(name)}', '{abbr}', '{escape(desc)}')"
        for abbr, (name, desc) in UOM_DEFS.items()
    )
    category_values = ",\n  ".join(f"('{escape(cat)}')" for cat in categories)
    brand_set = sorted({prod["brand"] for prod in products})
    brand_values = ",\n  ".join(f"('{escape(brand)}')" for brand in brand_set)
    provider_values = ",\n  ".join(f"('{escape(prov)}')" for prov in providers)
    location_values = ",\n  ".join(
        [
            "('Bodega Calameno')",
            "('Camara Fria Calameno')",
            "('Bar Calameno')",
            "('Operaciones Calameno')",
        ]
    )
    persona_values = ",\n  ".join(
        f"('{escape(name)}')" for name in sorted(set(LOCATION_PERSON.values()))
    )

    product_values = ",\n    ".join(
        f"('{prod['sku']}', '{escape(prod['name'])}', '{prod['uom']}', "
        f"'{escape(prod['brand'])}', '{escape(prod['category'])}')"
        for prod in products
    )

    movement_values = []
    for entry in stock_entries:
        if entry["quantity"] <= 0 or not entry.get("sku"):
            continue
        provider_literal = (
            f"(SELECT id FROM proveedores WHERE nombre = '{escape(entry['supplier'])}')"
            if entry["supplier"]
            else "NULL"
        )
        sku = escape(entry["sku"])
        movement_values.append(
            "("
            f"TIMESTAMPTZ '{MOVEMENT_TIMESTAMP}', "
            f"'ingreso', "
            f"(SELECT id FROM productos WHERE sku = '{sku}'), "
            "NULL, "
            f"(SELECT id FROM locaciones WHERE nombre = '{escape(entry['location'])}'), "
            f"(SELECT id FROM personas WHERE nombre = '{escape(entry['persona'])}'), "
            f"{provider_literal}, "
            f"{entry['quantity']:.3f}, "
            f"'{escape(entry['note'])}'"
            ")"
        )
    movement_values_sql = ",\n  ".join(movement_values)

    sql_parts = [
        "-- Archivo generado automáticamente por build_calamenio_seeder.py",
        "BEGIN;",
        "\n-- Unidades de medida",
        f"INSERT INTO uoms (nombre, abreviatura, descripcion)\nVALUES\n  {uom_values}\nON CONFLICT (nombre) DO NOTHING;",
        "\n-- Categorías",
        f"INSERT INTO categorias (nombre)\nVALUES\n  {category_values}\nON CONFLICT (nombre) DO NOTHING;",
        "\n-- Marcas",
        f"INSERT INTO marcas (nombre)\nVALUES\n  {brand_values}\nON CONFLICT (nombre) DO NOTHING;",
        "\n-- Proveedores",
        f"INSERT INTO proveedores (nombre)\nVALUES\n  {provider_values}\nON CONFLICT (nombre) DO NOTHING;",
        "\n-- Locaciones",
        f"INSERT INTO locaciones (nombre)\nVALUES\n  {location_values}\nON CONFLICT (nombre) DO NOTHING;",
        "\n-- Personas",
        f"INSERT INTO personas (nombre)\nVALUES\n  {persona_values}\nON CONFLICT (nombre) DO NOTHING;",
        "\n-- Productos Calameno",
        "WITH producto_data AS (",
        "  SELECT * FROM (VALUES",
        f"    {product_values}",
        "  ) AS d (sku, nombre, uom_abrev, marca, categoria)",
        ")\nINSERT INTO productos (sku, nombre, activo, uom_id, marca_id, categoria_id)\nSELECT",
        "  d.sku,",
        "  d.nombre,",
        "  TRUE,",
        "  (SELECT id FROM uoms WHERE abreviatura = d.uom_abrev),",
        "  (SELECT id FROM marcas WHERE nombre = d.marca),",
        "  (SELECT id FROM categorias WHERE nombre = d.categoria)",
        "FROM producto_data d",
        "ON CONFLICT (sku) DO UPDATE SET nombre = EXCLUDED.nombre;",
    ]

    if movement_values_sql:
        sql_parts.extend(
            [
                "\n-- Movimientos iniciales",
                "INSERT INTO movimientos (fecha, tipo, producto_id, from_locacion_id, to_locacion_id, persona_id, proveedor_id, cantidad, nota)\nVALUES",
                f"  {movement_values_sql};",
            ]
        )

    sql_parts.append("COMMIT;")
    return "\n".join(sql_parts)


def process_sheet(
    workbook: pd.ExcelFile,
    sheet_name: str,
    product_map: Dict[Tuple[str, str, str], Dict],
    stock_entries: List[Dict],
    provider_set: set[str],
):
    sheet_key = sheet_name.strip().lower()
    if sheet_key not in CATEGORY_MAP and sheet_key != "bar":
        return

    df = workbook.parse(sheet_name, header=3)
    df = normalize_columns(df)

    if "producto" not in df.columns:
        return

    stock_col = pick_stock_column(df)
    if not stock_col:
        return

    gramaje_col = pick_measure_column(df)
    descriptor_col = "descripcion" if "descripcion" in df.columns else None

    current_bar_section: str | None = None
    for row in df.itertuples(index=False):
        raw_product = clean_text(getattr(row, "producto", ""))
        if sheet_key == "bar":
            header_key = raw_product.strip().upper()
            if header_key in BAR_SECTION_CATEGORY:
                current_bar_section = header_key
                continue
        if should_skip_product(raw_product):
            continue

        stock_value = parse_number(getattr(row, stock_col, None))
        if stock_value is None:
            continue

        descriptor = clean_text(getattr(row, descriptor_col, "")) if descriptor_col else ""
        raw_measure = clean_text(getattr(row, gramaje_col, "")) if gramaje_col else ""
        section_for_row = current_bar_section
        if sheet_key == "bar" and raw_product.strip().lower() in {"ice", "hielo"}:
            section_for_row = None
        category = determine_category(sheet_key, section_for_row)
        measure = parse_measure(raw_measure, category)
        name = build_product_name(raw_product, descriptor, measure.label)
        brand = format_name(getattr(row, "marca", ""))
        supplier = format_name(getattr(row, "proveedor", ""))
        supplier = pick_supplier(supplier)

        key = (name, category, measure.uom)
        if key not in product_map:
            product_map[key] = {
                "name": name,
                "category": category,
                "uom": measure.uom,
                "brands": set(),
                "key": key,
            }
        if brand:
            product_map[key]["brands"].add(brand)

        location = determine_location(category, sheet_key)
        persona = LOCATION_PERSON[location]
        quantity = round((stock_value or 0.0) * (measure.unit_size or 1.0), 3)
        note = f"Carga inicial {sheet_name} ({category})"
        if quantity > 0:
            stock_entries.append(
                {
                    "key": key,
                    "quantity": quantity,
                    "location": location,
                    "persona": persona,
                    "supplier": supplier,
                    "note": note,
                }
            )
            if supplier:
                provider_set.add(supplier)


def main() -> None:
    workbook = pd.ExcelFile(EXCEL_PATH)
    product_map: Dict[Tuple[str, str, str], Dict] = {}
    stock_entries: List[Dict] = []
    provider_set: set[str] = set()

    for sheet_name in workbook.sheet_names:
        process_sheet(workbook, sheet_name, product_map, stock_entries, provider_set)

    products = assign_sku(product_map)
    sku_lookup = {record["key"]: record["sku"] for record in products}
    for entry in stock_entries:
        entry["sku"] = sku_lookup.get(entry["key"])
    providers = sorted(provider_set)
    if not providers:
        providers = ["Proveedores Varios Calameno"]
    elif "Proveedores Varios Calameno" not in providers:
        providers.append("Proveedores Varios Calameno")

    categories = sorted({prod["category"] for prod in products})
    sql = build_sql(products, stock_entries, providers, categories)
    OUTPUT_PATH.write_text(sql, encoding="utf-8")
    print(f"Generados {len(products)} productos y {len(stock_entries)} movimientos en {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
