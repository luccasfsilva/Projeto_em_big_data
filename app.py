# app.py

from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Carregue seus dados (exemplo: CSV local)
df = pd.read_csv('seus_dados.csv')

app = dash.Dash(__name__)
server = app.server  # para deploy em Flask, etc.

app.layout = html.Div([
    html.H1('Dashboard Dinâmico'),
    html.Label('Escolha uma categoria:'),
    dcc.Dropdown(
        id='dropdown-cat',
        options=[{'label': cat, 'value': cat} for cat in df['categoria'].unique()],
        value=df['categoria'].unique()[0]
    ),
    dcc.Graph(id='grafico-principal')
])

@app.callback(
    Output('grafico-principal', 'figure'),
    Input('dropdown-cat', 'value')
)
def atualizar_grafico(categoria_selecionada):
    dados_filtrados = df[df['categoria'] == categoria_selecionada]
    fig = px.bar(dados_filtrados, x='x', y='y', title=f'Categoria: {categoria_selecionada}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
