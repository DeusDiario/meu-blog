import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Carregando os dados dos arquivos
# AJUSTE OS CAMINHOS ABAIXO PARA ONDE SEUS ARQUIVOS ESTÃO:
y = np.loadtxt(r'C:\Users\possa\Documents\regressão\y.txt')
X_values = np.loadtxt(r'C:\Users\possa\Documents\regressão\X (1).txt')

# Preparando a matriz X para regressão linear
# X = [1, x] para incluir o intercepto
n = len(X_values)
X = np.column_stack([np.ones(n), X_values])

# Calculando os coeficientes usando a fórmula matricial
# β = (X^T X)^(-1) X^T y
XtX = X.T @ X
XtX_inv = np.linalg.inv(XtX)
Xty = X.T @ y
beta = XtX_inv @ Xty

# Extraindo os coeficientes
a = beta[0]  # intercepto
b = beta[1]  # coeficiente angular (slope)

print(f"Coeficientes da regressão linear:")
print(f"Intercepto (a): {a:.4f}")
print(f"Coeficiente angular (b): {b:.4f}")
print(f"\nEquação da reta: y = {a:.4f} + {b:.4f}x")

# Calculando os valores preditos pela reta
y_pred = a + b * X_values

# Criando o gráfico com Plotly
fig = go.Figure()

# Adicionando os pontos dos dados
fig.add_trace(go.Scatter(
    x=X_values,
    y=y,
    mode='markers',
    name='Dados Observados',
    marker=dict(color='#2E86AB', size=6, opacity=0.6)
))

# Adicionando a linha de regressão
fig.add_trace(go.Scatter(
    x=X_values,
    y=y_pred,
    mode='lines',
    name=f'Regressão: y = {a:.2f} + {b:.2f}x',
    line=dict(color='#A23B72', width=3)
))

# Configurando o layout
fig.update_layout(
    title='Regressão Linear: Anos de Estudo vs Salário',
    xaxis_title='Anos de Estudo',
    yaxis_title='Salário',
    template='plotly_white',
    width=900,
    height=600,
    font=dict(size=12),
    showlegend=True
)

# Salvando o gráfico
fig.write_html("grafico.html")
fig.write_image("grafico.png", width=900, height=600)

# Exibindo o gráfico
print("\nGráfico salvo como 'grafico.html' e 'grafico.png'")
fig.show()
