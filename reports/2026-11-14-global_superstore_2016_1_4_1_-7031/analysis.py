import os
import pandas as pd
import numpy as np
import html
import json

# SETTINGS
WORK_DIR = '/content/sprk/run-7031'
INPUT_FILE = os.path.join(WORK_DIR, 'input.xlsx')
OUTPUT_FILE = os.path.join(WORK_DIR, 'report.html')

# LOAD DATA
orders = pd.read_excel(INPUT_FILE, sheet_name='Orders')

# KPIs
kpi_total_sales = orders['Sales'].sum()
kpi_total_profit = orders['Profit'].sum()
kpi_total_orders = orders['Order ID'].nunique()
kpi_total_customers = orders['Customer ID'].nunique()
kpi_avg_discount = orders['Discount'].mean()

# INSIGHTS
most_profitable_region = orders.groupby('Region')['Profit'].sum().idxmax()
most_profitable_region_profit = orders.groupby('Region')['Profit'].sum().max()
most_sales_category = orders.groupby('Category')['Sales'].sum().idxmax()
most_sales_category_sales = orders.groupby('Category')['Sales'].sum().max()
most_orders_segment = orders['Segment'].value_counts().idxmax()
most_orders_segment_count = orders['Segment'].value_counts().max()

insights = [
    f"Total sales: ${kpi_total_sales:,.0f}",
    f"Total profit: ${kpi_total_profit:,.0f}",
    f"Most profitable region: {most_profitable_region} (${most_profitable_region_profit:,.0f})",
    f"Category with highest sales: {most_sales_category} (${most_sales_category_sales:,.0f})",
    f"Segment with most orders: {most_orders_segment} ({most_orders_segment_count:,} orders)"
]

# BAR CHART: Top 15 Product Name by Sales, filter by Category
bar_category = 'Product Name'
bar_value = 'Sales'
bar_filter = 'Category'
bar_top_n = 15
bar_data = {}
for filter_val in ['All'] + list(orders[bar_filter].dropna().unique()):
    if filter_val == 'All':
        df = orders
    else:
        df = orders[orders[bar_filter] == filter_val]
    top = df.groupby(bar_category)[bar_value].sum().sort_values(ascending=False).head(bar_top_n)
    bar_data[filter_val] = {
        'x': [html.escape(str(x)) for x in top.index],
        'y': [float(y) for y in top.values]
    }

# PIE CHART: Segment by Sales, filter by Region
pie_category = 'Segment'
pie_value = 'Sales'
pie_filter = 'Region'
pie_data = {}
for filter_val in ['All'] + list(orders[pie_filter].dropna().unique()):
    if filter_val == 'All':
        df = orders
    else:
        df = orders[orders[pie_filter] == filter_val]
    group = df.groupby(pie_category)[pie_value].sum().sort_values(ascending=False)
    top = group.head(7)
    other = group.iloc[7:].sum()
    labels = [html.escape(str(x)) for x in top.index]
    values = [float(y) for y in top.values]
    if other > 0:
        labels.append('Other')
        values.append(float(other))
    pie_data[filter_val] = {'labels': labels, 'values': values}

# Prepare dropdown options
bar_filter_options = ['All'] + list(orders[bar_filter].dropna().unique())
pie_filter_options = ['All'] + list(orders[pie_filter].dropna().unique())

# Prepare KPIs for display
kpis = [
    {'label': 'Total Sales', 'value': f"${kpi_total_sales:,.0f}"},
    {'label': 'Total Profit', 'value': f"${kpi_total_profit:,.0f}"},
    {'label': 'Total Orders', 'value': f"{kpi_total_orders:,}"},
    {'label': 'Total Customers', 'value': f"{kpi_total_customers:,}"},
    {'label': 'Avg. Discount', 'value': f"{kpi_avg_discount:.2%}"}
]

# Preview table
preview = orders.head(10).copy()
preview = preview.applymap(lambda x: html.escape(str(x)))
preview_table = '\n'.join([
    '<tr>' + ''.join([f'<th>{html.escape(str(col))}</th>' for col in preview.columns]) + '</tr>'
] + [
    '<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>' for row in preview.values.tolist()
])

# DATA BLOCK
data_block = json.dumps({
    'bar_data': bar_data,
    'pie_data': pie_data,
    'bar_filter_options': bar_filter_options,
    'pie_filter_options': pie_filter_options
})

# HTML TEMPLATE
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Global Superstore 2016 Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f8f8f8; }
        .container { max-width: 1200px; margin: 30px auto; background: #fff; padding: 24px; border-radius: 8px; box-shadow: 0 2px 8px #0001; }
        h1 { margin-top: 0; }
        .subtitle { color: #555; margin-bottom: 24px; }
        .kpis { display: flex; gap: 24px; margin-bottom: 24px; }
        .kpi-card { background: #f0f4f8; padding: 18px 24px; border-radius: 8px; flex: 1; text-align: center; }
        .kpi-label { color: #888; font-size: 15px; }
        .kpi-value { font-size: 1.6em; font-weight: bold; margin-top: 6px; }
        .charts { display: flex; gap: 24px; }
        .chart-block { flex: 1; background: #fafbfc; padding: 18px; border-radius: 8px; }
        .dropdown { margin-bottom: 8px; }
        .insights { margin: 32px 0 18px 0; }
        .insights ul { margin: 0; padding-left: 20px; }
        .preview-table { width: 100%; border-collapse: collapse; margin-top: 18px; }
        .preview-table th, .preview-table td { border: 1px solid #ddd; padding: 6px 8px; font-size: 13px; }
        .preview-table th { background: #f0f0f0; }
    </style>
</head>
<body>
<div class="container">
    <h1>__TITLE__</h1>
    <div class="subtitle">__SUBTITLE__</div>
    <div class="kpis">__KPIS__</div>
    <div class="charts">
        <div class="chart-block">
            <div class="dropdown">
                <label for="bar-filter">Category:</label>
                <select id="bar-filter"></select>
            </div>
            <div id="bar-chart" style="height:400px;"></div>
        </div>
        <div class="chart-block">
            <div class="dropdown">
                <label for="pie-filter">Region:</label>
                <select id="pie-filter"></select>
            </div>
            <div id="pie-chart" style="height:400px;"></div>
        </div>
    </div>
    <div class="insights">
        <h3>Key Insights</h3>
        <ul>__INSIGHTS__</ul>
    </div>
    <h3>Preview of First 10 Orders</h3>
    <table class="preview-table">__PREVIEW__</table>
</div>
<script>
const DATA = __DATA__;

function fillDropdown(id, options) {
    const sel = document.getElementById(id);
    sel.innerHTML = '';
    options.forEach(opt => {
        const o = document.createElement('option');
        o.value = opt;
        o.textContent = opt;
        sel.appendChild(o);
    });
}

function drawBar(filter) {
    const d = DATA.bar_data[filter] || DATA.bar_data['All'];
    Plotly.react('bar-chart', [{
        x: d.x,
        y: d.y,
        type: 'bar',
        marker: {color: '#1f77b4'},
    }], {
        title: 'Top 15 Products by Sales',
        xaxis: {title: 'Product Name', automargin: true},
        yaxis: {title: 'Sales'},
        margin: {b: 120}
    });
}

function drawPie(filter) {
    const d = DATA.pie_data[filter] || DATA.pie_data['All'];
    Plotly.react('pie-chart', [{
        labels: d.labels,
        values: d.values,
        type: 'pie',
        textinfo: 'label+percent',
        automargin: true
    }], {
        title: 'Sales by Segment',
        showlegend: true
    });
}

document.addEventListener('DOMContentLoaded', function() {
    fillDropdown('bar-filter', DATA.bar_filter_options);
    fillDropdown('pie-filter', DATA.pie_filter_options);
    drawBar('All');
    drawPie('All');
    document.getElementById('bar-filter').addEventListener('change', function() {
        drawBar(this.value);
    });
    document.getElementById('pie-filter').addEventListener('change', function() {
        drawPie(this.value);
    });
});
</script>
</body>
</html>
'''

# Fill markers
html_out = html_template
html_out = html_out.replace('__TITLE__', 'Global Superstore 2016 Dashboard')
html_out = html_out.replace('__SUBTITLE__', 'Interactive dashboard for sales, profit, and orders (2016)')
html_out = html_out.replace('__KPIS__', ''.join([
    f'<div class="kpi-card"><div class="kpi-label">{html.escape(k["label"])}</div><div class="kpi-value">{html.escape(str(k["value"]))}</div></div>' for k in kpis
]))
html_out = html_out.replace('__INSIGHTS__', ''.join([f'<li>{html.escape(i)}</li>' for i in insights]))
html_out = html_out.replace('__PREVIEW__', preview_table)
html_out = html_out.replace('__DATA__', data_block)

# Save
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html_out)

size = os.path.getsize(OUTPUT_FILE)
print(f"DONE: report.html size {size} bytes")
