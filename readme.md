## Observatorio de Sellos APL – CORFO

Este repositorio contiene la versión estática del tablero **“Número de sellos entregados por CORFO en Acuerdos de Producción Limpia (APL)”**, desarrollado por el Centro de Estudios Regionales de la Universidad Austral de Chile. La aplicación reúne y presenta, mediante Highcharts, los principales indicadores construidos a partir de los registros procesados en `data/processed/`.

### Visualizaciones incluidas

- **Participación sectorial**: gráfico de torta que combina adhesiones y certificaciones por sector económico.
- **Distribución de registros**: columnas apiladas que comparan instalaciones y empresas para adhesión/certificación.
- **Tamaño de empresa**: variwide donde la altura representa empresas y el ancho las instalaciones asociadas a cada segmento (Micro, Pequeña, etc.).
- **Crecimiento histórico**: serie logarítmica con el total anual de empresas que han adherido o certificado APL desde 2002.
- **Series por ámbito**: líneas independientes para adhesiones y certificaciones por año.

Todas las visualizaciones se encuentran integradas en `docs/index.html`, accesibles mediante la barra de navegación superior.

### Cómo visualizar el dashboard

1. Clona el repositorio y sitúate en la carpeta `docs/`.
2. Abre `index.html` en cualquier navegador moderno (Chrome, Edge, Firefox). No se requiere servidor adicional.
3. Alterna entre las secciones usando los enlaces del navbar para cargar el gráfico correspondiente.

### Datos

Los gráficos consumen los CSV procesados ubicados en `data/processed/`, entre ellos:

- `yearly_summary.csv`
- `adhesion_by_year.csv`
- `certification_by_year.csv`
- `adhesion_by_sector.csv`
- `certification_by_sector.csv`
- `adhesion_by_size.csv`

Los valores están precargados en los scripts del dashboard; para refrescar las cifras es necesario recalcular los agregados y actualizar los arreglos dentro de `docs/index.html` (y los HTML individuales si se mantienen para referencia).

### Estructura relevante

```
docs/
├── index.html          # Tablero principal con todas las visualizaciones Highcharts
├── styles.css          # Estilos compartidos del sitio estático
├── *.html              # Archivos individuales originales de cada gráfico (referencia)
├── interactive.js      # (Reservado para futuras interacciones)
└── thumbnail_*.png     # Recursos gráficos
```

### Créditos

Desarrollado por el equipo del Observatorio de Sellos APL – Universidad Austral de Chile.
