from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
DISTRIBUTION_OUTPUT_PATH = PROJECT_ROOT / "docs" / "distribution_explorer.html"
TIME_SERIES_OUTPUT_PATH = PROJECT_ROOT / "docs" / "time_series_view.html"
COMPARISON_OUTPUT_PATH = PROJECT_ROOT / "docs" / "comparison_dashboard.html"
SECTOR_OUTPUT_PATH = PROJECT_ROOT / "docs" / "sector_overview.html"
SIZE_OUTPUT_PATH = PROJECT_ROOT / "docs" / "size_distribution.html"


def load_distribution_sources() -> dict[str, pd.DataFrame]:
    return {
        "Adhesión anual": pd.read_csv(DATA_DIR / "adhesion_by_year.csv"),
        "Certificación anual": pd.read_csv(DATA_DIR / "certification_by_year.csv"),
        "Tamaño de empresa": pd.read_csv(DATA_DIR / "adhesion_by_size.csv"),
    }


def load_sector_summary() -> pd.DataFrame:
    adhesion = pd.read_csv(DATA_DIR / "adhesion_by_sector.csv").assign(dataset="Adhesión")
    certification = (
        pd.read_csv(DATA_DIR / "certification_by_sector.csv").assign(dataset="Certificación")
    )
    combined = pd.concat([adhesion, certification], ignore_index=True)
    combined["sector"] = combined["sector"].astype(str).str.strip()
    combined["installations"] = (
        pd.to_numeric(combined["installations"], errors="coerce").fillna(0).astype(int)
    )
    combined["sector"] = combined["sector"].str.replace(
        "Agricultura, ganadería, pesca y silvicultura",
        "Agro, pesca y silvicultura",
        regex=False,
    )
    return combined


def build_figures(datasets: dict[str, pd.DataFrame]) -> dict[str, dict[str, dict[str, object]]]:
    figures: dict[str, dict[str, dict[str, object]]] = {}

    adhesion_columns = {
        "installations": "Instalaciones",
        "companies": "Empresas",
    }

    for name, frame in datasets.items():
        if name in {"Adhesión anual", "Certificación anual"}:
            normalized = frame.copy()
            normalized = normalized.rename(
                columns={
                    "year": "Año",
                    "installations": "Instalaciones",
                    "companies": "Empresas",
                }
            )
            normalized = normalized.melt(
                id_vars="Año",
                value_vars=list(adhesion_columns.values()),
                var_name="Indicador",
                value_name="Valor",
            )
            hist = px.histogram(
                normalized,
                x="Valor",
                color="Indicador",
                nbins=10,
                title=f"Distribución de indicadores - {name}",
            )
            hist.update_traces(opacity=0.75)
            hist.update_layout(xaxis_title="Cantidad", yaxis_title="Frecuencia")
            hist_hover = "Indicador: %{fullData.name}<br>Cantidad: %{x}<br>Frecuencia: %{y}<extra></extra>"
            for trace in hist.data:
                trace.update(hovertemplate=hist_hover)

            box = px.box(
                normalized,
                x="Indicador",
                y="Valor",
                title=f"Boxplot por indicador - {name}",
                color="Indicador",
            )
            box.update_layout(xaxis_title="Indicador", yaxis_title="Cantidad")
            for trace in box.data:
                trace.update(hovertemplate="Indicador: %{x}<br>Valor: %{y}<extra></extra>")

        else:  # Tamaño de empresa
            normalized = frame.copy()
            normalized = normalized.rename(
                columns={
                    "company_size": "Tamaño de empresa",
                    "companies": "Empresas",
                    "installations": "Instalaciones",
                }
            )
            hist = px.histogram(
                normalized,
                x="Empresas",
                color_discrete_sequence=["#1f77b4"],
                nbins=10,
                title="Distribución de empresas por tamaño",
            )
            hist.update_layout(xaxis_title="Empresas", yaxis_title="Frecuencia")
            for trace in hist.data:
                trace.update(hovertemplate="Empresas: %{x}<br>Frecuencia: %{y}<extra></extra>")

            box = px.box(
                normalized,
                y="Instalaciones",
                title="Boxplot de instalaciones por tamaño",
            )
            box.update_layout(yaxis_title="Instalaciones")
            for trace in box.data:
                trace.update(hovertemplate="Instalaciones: %{y}<extra></extra>")

        figures[name] = {
            "hist": json.loads(hist.to_json()),
            "box": json.loads(box.to_json()),
        }

    return figures


def build_distribution_html(figures: dict[str, dict[str, dict[str, object]]]) -> str:
    dataset_options = list(figures.keys())
    default_dataset = dataset_options[0]

    html = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
    <meta charset=\"utf-8\" />
    <title>Explorador de distribuciones APL</title>
    <script src=\"https://cdn.plot.ly/plotly-2.30.0.min.js\"></script>
    <style>
        body {{ font-family: "Segoe UI", Tahoma, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 24px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1); }}
        h1 {{ text-align: center; margin-bottom: 16px; }}
        .controls {{ display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; margin-bottom: 18px; }}
        label {{ font-weight: 600; margin-right: 8px; }}
        select {{ padding: 6px 10px; border-radius: 6px; border: 1px solid #cbd5e0; }}
        #chart {{ width: 100%; height: 640px; }}
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>Explorador de distribuciones APL</h1>
        <div class=\"controls\">
            <div>
                <label for=\"dataset-select\">Conjunto:</label>
                <select id=\"dataset-select\">
                    {''.join(f'<option value=\"{option}\">{option}</option>' for option in dataset_options)}
                </select>
            </div>
            <div>
                <label for=\"chart-select\">Visualización:</label>
                <select id=\"chart-select\">
                    <option value=\"hist\">Histograma</option>
                    <option value=\"box\">Boxplot</option>
                </select>
            </div>
        </div>
        <div id=\"chart\"></div>
    </div>
    <script>
        const figures = {json.dumps(figures)};
        let currentDataset = {json.dumps(default_dataset)};
        let currentChart = 'hist';

        const datasetSelect = document.getElementById('dataset-select');
        const chartSelect = document.getElementById('chart-select');

        datasetSelect.value = currentDataset;

        function render() {{
            const figure = figures[currentDataset][currentChart];
            Plotly.react('chart', figure.data, figure.layout, {{responsive: true}});
        }}

        datasetSelect.addEventListener('change', (event) => {{
            currentDataset = event.target.value;
            render();
        }});

        chartSelect.addEventListener('change', (event) => {{
            currentChart = event.target.value;
            render();
        }});

        render();
    </script>
</body>
</html>
"""
    return html


def load_time_series_records() -> list[dict[str, int]]:
    frame = pd.read_csv(DATA_DIR / "yearly_summary.csv")
    normalized = frame.copy()
    for column in ["year", "companies_adhesion", "companies_certification"]:
        normalized[column] = (
            pd.to_numeric(normalized[column], errors="coerce").fillna(0).astype(int)
        )

    records: list[dict[str, int]] = []
    for row in normalized.itertuples(index=False):
        year = int(row.year)
        records.append({"year": year, "scope": "Adhesión", "value": int(row.companies_adhesion)})
        records.append({"year": year, "scope": "Certificación", "value": int(row.companies_certification)})
    return records


def build_time_series_html(records: list[dict[str, int]]) -> str:
    years = sorted({item["year"] for item in records})
    if not years:
        raise ValueError("No se encontraron datos para construir la vista de series de tiempo.")

    start_options = "".join(
        f'<option value="{year}"{" selected" if index == 0 else ""}>{year}</option>'
        for index, year in enumerate(years)
    )
    end_options = "".join(
        f'<option value="{year}"{" selected" if index == len(years) - 1 else ""}>{year}</option>'
        for index, year in enumerate(years)
    )

    html = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
    <meta charset=\"utf-8\" />
    <title>Tendencia de empresas APL</title>
    <script src=\"https://cdn.plot.ly/plotly-2.30.0.min.js\"></script>
    <style>
        body {{ font-family: \"Segoe UI\", Tahoma, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 24px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1); }}
        h1 {{ text-align: center; margin-bottom: 16px; }}
        .controls {{ display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; margin-bottom: 18px; }}
        .controls-group {{ display: flex; align-items: center; gap: 8px; }}
        label {{ font-weight: 600; }}
        select {{ padding: 6px 10px; border-radius: 6px; border: 1px solid #cbd5e0; }}
        .checkboxes {{ display: flex; align-items: center; gap: 16px; }}
        #time-series-chart {{ width: 100%; height: 640px; }}
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>Empresas por año</h1>
        <div class=\"controls\">
            <div class=\"controls-group\">
                <label for=\"start-year\">Año inicial:</label>
                <select id=\"start-year\">{start_options}</select>
            </div>
            <div class=\"controls-group\">
                <label for=\"end-year\">Año final:</label>
                <select id=\"end-year\">{end_options}</select>
            </div>
            <div class=\"checkboxes\">
                <label><input type=\"checkbox\" class=\"scope-checkbox\" value=\"Adhesión\" checked /> Adhesión</label>
                <label><input type=\"checkbox\" class=\"scope-checkbox\" value=\"Certificación\" checked /> Certificación</label>
            </div>
        </div>
        <div id=\"time-series-chart\"></div>
    </div>
    <script>
        const records = {json.dumps(records)};
        const startSelect = document.getElementById('start-year');
        const endSelect = document.getElementById('end-year');
        const scopeCheckboxes = Array.from(document.querySelectorAll('.scope-checkbox'));

        function handleYearChange(event) {{
            const startValue = parseInt(startSelect.value, 10);
            const endValue = parseInt(endSelect.value, 10);
            if (startValue > endValue) {{
                if (event.target === startSelect) {{
                    endSelect.value = startSelect.value;
                }} else {{
                    startSelect.value = endSelect.value;
                }}
            }}
            render();
        }}

        function render() {{
            const startYear = parseInt(startSelect.value, 10);
            const endYear = parseInt(endSelect.value, 10);
            const activeScopes = scopeCheckboxes
                .filter((checkbox) => checkbox.checked)
                .map((checkbox) => checkbox.value);

            if (activeScopes.length === 0) {{
                const emptyLayout = {{
                    title: 'Empresas por año',
                    xaxis: {{ title: 'Año' }},
                    yaxis: {{ title: 'Empresas' }},
                    annotations: [{{
                        text: 'Selecciona al menos un ámbito para visualizar la serie.',
                        showarrow: false,
                        x: 0.5,
                        y: 0.5,
                        xref: 'paper',
                        yref: 'paper',
                        font: {{ size: 16 }},
                    }}],
                }};
                Plotly.react('time-series-chart', [], emptyLayout, {{responsive: true}});
                return;
            }}

            const filtered = records.filter((item) =>
                item.year >= startYear && item.year <= endYear && activeScopes.includes(item.scope)
            );

            const tracesMap = new Map();
            filtered.forEach((item) => {{
                if (!tracesMap.has(item.scope)) {{
                    tracesMap.set(item.scope, {{ x: [], y: [], mode: 'lines+markers', name: item.scope }});
                }}
                const trace = tracesMap.get(item.scope);
                trace.x.push(item.year);
                trace.y.push(item.value);
            }});

            const traces = Array.from(tracesMap.values());
            const layout = {{
                title: 'Empresas por año',
                xaxis: {{ title: 'Año', dtick: 1 }},
                yaxis: {{ title: 'Empresas' }},
                legend: {{ title: {{ text: 'Ámbito' }} }},
            }};

            traces.forEach((trace) => {{
                trace.hovertemplate = 'Año: %{{x}}<br>Empresas: %{{y}}<br>Ámbito: ' + trace.name + '<extra></extra>';
            }});

            Plotly.react('time-series-chart', traces, layout, {{responsive: true}});
        }}

        startSelect.addEventListener('change', handleYearChange);
        endSelect.addEventListener('change', handleYearChange);
        scopeCheckboxes.forEach((checkbox) => checkbox.addEventListener('change', render));

        render();
    </script>
</body>
</html>
"""
    return html


def build_comparison_html(
    time_records: list[dict[str, int]], size_frame: pd.DataFrame
) -> str:
    normalized = size_frame.copy()
    normalized["company_size"] = normalized["company_size"].astype(str)
    normalized["companies"] = (
        pd.to_numeric(normalized["companies"], errors="coerce").fillna(0).astype(int)
    )

    size_records = [
        {"company_size": row.company_size, "companies": int(row.companies)}
        for row in normalized.itertuples(index=False)
    ]

    years = sorted({record["year"] for record in time_records})
    if not years:
        raise ValueError(
            "No se encontraron datos de series de tiempo para el panel comparativo."
        )

    html = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
    <meta charset=\"utf-8\" />
    <title>Panel comparativo de empresas APL</title>
    <script src=\"https://cdn.plot.ly/plotly-2.30.0.min.js\"></script>
    <style>
        body {{ font-family: \"Segoe UI\", Tahoma, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 24px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1); }}
        h1 {{ text-align: center; margin-bottom: 16px; }}
        .controls {{ display: flex; justify-content: center; margin-bottom: 18px; gap: 12px; }}
        label {{ font-weight: 600; }}
        select {{ padding: 6px 10px; border-radius: 6px; border: 1px solid #cbd5e0; }}
        #comparison-chart {{ width: 100%; height: 640px; }}
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>Panel comparativo de empresas</h1>
        <div class=\"controls\">
            <label for=\"view-select\">Vista:</label>
            <select id=\"view-select\">
                <option value=\"time\" selected>Serie temporal</option>
                <option value=\"size\">Tamaño de empresa</option>
            </select>
        </div>
        <div id=\"comparison-chart\"></div>
    </div>
    <script>
        const timeRecords = {json.dumps(time_records)};
        const sizeRecords = {json.dumps(size_records)};
        const viewSelect = document.getElementById('view-select');

        function buildTimeTraces() {{
            const tracesMap = new Map();
            timeRecords.forEach((item) => {{
                if (!tracesMap.has(item.scope)) {{
                    tracesMap.set(item.scope, {{ x: [], y: [], mode: 'lines+markers', name: item.scope }});
                }}
                const trace = tracesMap.get(item.scope);
                trace.x.push(item.year);
                trace.y.push(item.value);
            }});

            const traces = Array.from(tracesMap.values());
            traces.forEach((trace) => {{
                trace.hovertemplate = 'Año: %{{x}}<br>Empresas: %{{y}}<br>Ámbito: ' + trace.name + '<extra></extra>';
            }});
            return traces;
        }}

        function buildTimeLayout() {{
            return {{
                title: 'Empresas por año',
                xaxis: {{ title: 'Año', dtick: 1 }},
                yaxis: {{ title: 'Empresas' }},
                legend: {{ title: {{ text: 'Ámbito' }} }},
            }};
        }}

        function buildSizeTrace() {{
            const trace = {{
                type: 'bar',
                x: sizeRecords.map((item) => item.company_size),
                y: sizeRecords.map((item) => item.companies),
                text: sizeRecords.map((item) => item.companies),
                textposition: 'outside',
                marker: {{ color: '#1f77b4' }},
                hovertemplate: 'Tamaño de empresa: %{{x}}<br>Empresas: %{{y}}<extra></extra>',
                name: 'Empresas',
            }};
            return [trace];
        }}

        function buildSizeLayout() {{
            return {{
                title: 'Empresas por tamaño de empresa (Adhesión)',
                xaxis: {{ title: 'Tamaño de empresa' }},
                yaxis: {{ title: 'Empresas' }},
                showlegend: false,
            }};
        }}

        function render() {{
            if (viewSelect.value === 'size') {{
                Plotly.react('comparison-chart', buildSizeTrace(), buildSizeLayout(), {{responsive: true}});
                return;
            }}

            Plotly.react('comparison-chart', buildTimeTraces(), buildTimeLayout(), {{responsive: true}});
        }}

        viewSelect.addEventListener('change', render);

        render();
    </script>
</body>
</html>
"""
    return html


def build_sector_html(frame: pd.DataFrame) -> str:
    processed = frame.copy()
    sector_totals = (
        processed.groupby("sector")["installations"].sum().sort_values(ascending=False)
    )
    sector_order = sector_totals.index.tolist()

    dataset_payload: dict[str, list[int]] = {}
    for dataset, group in processed.groupby("dataset"):
        data_map = group.set_index("sector")["installations"].to_dict()
        dataset_payload[dataset] = [int(data_map.get(sector, 0)) for sector in sector_order]

    preferred_order = ["Adhesión", "Certificación"]
    dataset_labels = [label for label in preferred_order if label in dataset_payload]
    dataset_labels.extend(
        label for label in dataset_payload if label not in dataset_labels
    )

    checkbox_markup = "".join(
        f'<label><input type="checkbox" class="dataset-checkbox" value="{dataset}" checked /> {dataset}</label>'
        for dataset in dataset_labels
    )

    html = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
    <meta charset=\"utf-8\" />
    <title>Instalaciones por sector económico</title>
    <script src=\"https://cdn.plot.ly/plotly-2.30.0.min.js\"></script>
    <style>
        body {{ font-family: \"Segoe UI\", Tahoma, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 24px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1); }}
        h1 {{ text-align: center; margin-bottom: 16px; }}
        .controls {{ display: flex; flex-wrap: wrap; gap: 16px; justify-content: center; margin-bottom: 18px; }}
        .controls label {{ font-weight: 600; display: flex; align-items: center; gap: 6px; }}
        #sector-chart {{ width: 100%; height: 720px; }}
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>Instalaciones por sector económico</h1>
        <div class=\"controls\">
            {checkbox_markup}
        </div>
        <div id=\"sector-chart\"></div>
    </div>
    <script>
        const sectorOrder = {json.dumps(sector_order)};
        const datasetPayload = {json.dumps(dataset_payload)};
        const datasetCheckboxes = Array.from(document.querySelectorAll('.dataset-checkbox'));

        function render() {{
            const activeDatasets = datasetCheckboxes
                .filter((checkbox) => checkbox.checked)
                .map((checkbox) => checkbox.value);

            if (activeDatasets.length === 0) {{
                const emptyLayout = {{
                    title: 'Instalaciones por sector económico',
                    xaxis: {{ title: 'Instalaciones' }},
                    yaxis: {{ title: 'Sector', categoryorder: 'array', categoryarray: sectorOrder }},
                    annotations: [{{
                        text: 'Selecciona al menos un tipo para visualizar las instalaciones.',
                        showarrow: false,
                        x: 0.5,
                        y: 0.5,
                        xref: 'paper',
                        yref: 'paper',
                        font: {{ size: 16 }},
                    }}],
                }};
                Plotly.react('sector-chart', [], emptyLayout, {{responsive: true}});
                return;
            }}

            const traces = activeDatasets.map((dataset) => {{
                const values = datasetPayload[dataset] || [];
                return {{
                    type: 'bar',
                    orientation: 'h',
                    x: values,
                    y: sectorOrder,
                    name: dataset,
                    text: values,
                    textposition: 'outside',
                    hovertemplate: 'Sector: %{{y}}<br>Instalaciones: %{{x}}<br>Tipo: ' + dataset + '<extra></extra>',
                }};
            }});

            const layout = {{
                title: 'Instalaciones por sector económico',
                xaxis: {{ title: 'Instalaciones' }},
                yaxis: {{
                    title: 'Sector',
                    categoryorder: 'array',
                    categoryarray: sectorOrder,
                }},
                barmode: 'group',
                legend: {{ title: {{ text: 'Tipo' }} }},
            }};

            Plotly.react('sector-chart', traces, layout, {{responsive: true}});
        }}

        datasetCheckboxes.forEach((checkbox) => checkbox.addEventListener('change', render));

        render();
    </script>
</body>
</html>
"""
    return html


def build_size_html(frame: pd.DataFrame) -> str:
    normalized = frame.copy()
    normalized["company_size"] = normalized["company_size"].astype(str)
    normalized["companies"] = (
        pd.to_numeric(normalized["companies"], errors="coerce").fillna(0).astype(int)
    )
    normalized["installations"] = (
        pd.to_numeric(normalized["installations"], errors="coerce").fillna(0).astype(int)
    )

    size_order = (
        normalized.sort_values("companies", ascending=False)["company_size"].tolist()
    )

    metric_payload = {
        "Empresas": normalized.set_index("company_size")["companies"].reindex(size_order).astype(int).tolist(),
        "Instalaciones": normalized.set_index("company_size")["installations"].reindex(size_order).astype(int).tolist(),
    }

    checkbox_markup = "".join(
        f'<label><input type="checkbox" class="metric-checkbox" value="{metric}" checked /> {metric}</label>'
        for metric in metric_payload
    )

    html = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
    <meta charset=\"utf-8\" />
    <title>Empresas e instalaciones por tamaño de empresa</title>
    <script src=\"https://cdn.plot.ly/plotly-2.30.0.min.js\"></script>
    <style>
        body {{ font-family: \"Segoe UI\", Tahoma, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 24px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1); }}
        h1 {{ text-align: center; margin-bottom: 16px; }}
        .controls {{ display: flex; flex-wrap: wrap; gap: 16px; justify-content: center; margin-bottom: 18px; }}
        .controls label {{ font-weight: 600; display: flex; align-items: center; gap: 6px; }}
        #size-chart {{ width: 100%; height: 640px; }}
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>Empresas e instalaciones por tamaño de empresa</h1>
        <div class=\"controls\">
            {checkbox_markup}
        </div>
        <div id=\"size-chart\"></div>
    </div>
    <script>
        const sizeOrder = {json.dumps(size_order)};
        const metricPayload = {json.dumps(metric_payload)};
        const metricCheckboxes = Array.from(document.querySelectorAll('.metric-checkbox'));

        function render() {{
            const activeMetrics = metricCheckboxes
                .filter((checkbox) => checkbox.checked)
                .map((checkbox) => checkbox.value);

            if (activeMetrics.length === 0) {{
                const emptyLayout = {{
                    title: 'Empresas e instalaciones por tamaño de empresa',
                    xaxis: {{ title: 'Tamaño de empresa', categoryorder: 'array', categoryarray: sizeOrder }},
                    yaxis: {{ title: 'Cantidad' }},
                    annotations: [{{
                        text: 'Selecciona al menos un indicador para visualizar la comparación.',
                        showarrow: false,
                        x: 0.5,
                        y: 0.5,
                        xref: 'paper',
                        yref: 'paper',
                        font: {{ size: 16 }},
                    }}],
                }};
                Plotly.react('size-chart', [], emptyLayout, {{responsive: true}});
                return;
            }}

            const traces = activeMetrics.map((metric) => {{
                const values = metricPayload[metric] || [];
                return {{
                    type: 'bar',
                    x: sizeOrder,
                    y: values,
                    name: metric,
                    text: values,
                    textposition: 'outside',
                    hovertemplate: 'Tamaño de empresa: %{{x}}<br>' + metric + ': %{{y}}<extra></extra>',
                }};
            }});

            const layout = {{
                title: 'Empresas e instalaciones por tamaño de empresa',
                xaxis: {{ title: 'Tamaño de empresa', categoryorder: 'array', categoryarray: sizeOrder }},
                yaxis: {{ title: 'Cantidad' }},
                barmode: 'group',
                legend: {{ title: {{ text: 'Tipo' }} }},
            }};

            Plotly.react('size-chart', traces, layout, {{responsive: true}});
        }}

        metricCheckboxes.forEach((checkbox) => checkbox.addEventListener('change', render));

        render();
    </script>
</body>
</html>
"""
    return html


def main() -> None:
    docs_dir = DISTRIBUTION_OUTPUT_PATH.parent
    docs_dir.mkdir(parents=True, exist_ok=True)

    distribution_sources = load_distribution_sources()
    figures = build_figures(distribution_sources)
    DISTRIBUTION_OUTPUT_PATH.write_text(
        build_distribution_html(figures), encoding="utf-8"
    )

    time_series_records = load_time_series_records()
    TIME_SERIES_OUTPUT_PATH.write_text(
        build_time_series_html(time_series_records), encoding="utf-8"
    )

    size_frame = distribution_sources["Tamaño de empresa"].copy()
    COMPARISON_OUTPUT_PATH.write_text(
        build_comparison_html(time_series_records, size_frame.copy()), encoding="utf-8"
    )
    SIZE_OUTPUT_PATH.write_text(
        build_size_html(size_frame), encoding="utf-8"
    )

    sector_frame = load_sector_summary()
    SECTOR_OUTPUT_PATH.write_text(
        build_sector_html(sector_frame), encoding="utf-8"
    )

    print(f"Archivo HTML generado en: {DISTRIBUTION_OUTPUT_PATH}")
    print(f"Archivo HTML generado en: {TIME_SERIES_OUTPUT_PATH}")
    print(f"Archivo HTML generado en: {COMPARISON_OUTPUT_PATH}")
    print(f"Archivo HTML generado en: {SECTOR_OUTPUT_PATH}")
    print(f"Archivo HTML generado en: {SIZE_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
