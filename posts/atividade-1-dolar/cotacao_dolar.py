import requests
import pandas as pd
import plotly.graph_objects as go
import calendar
from datetime import datetime, timedelta

def obter_cotacao_dolar(periodo):
    
    first_date = datetime.strptime(periodo, "%m%Y")
    
    last_day = calendar.monthrange(first_date.year, first_date.month)[1]
    last_date = first_date.replace(day=last_day)
    
    data_inicial = first_date.strftime("%m-%d-%Y")
    data_final = last_date.strftime("%m-%d-%Y")
    
    url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='{data_inicial}'&@dataFinalCotacao='{data_final}'&$format=json"
    
    print(f"Consultando cotações de {first_date.strftime('%B/%Y')}...")
    print(f"Período: {data_inicial} até {data_final}")
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'value' in data and len(data['value']) > 0:
            df = pd.DataFrame(data['value'])
            
            df['dataHoraCotacao'] = pd.to_datetime(df['dataHoraCotacao'])
            df['data'] = df['dataHoraCotacao'].dt.date
            
            df = df.sort_values('dataHoraCotacao')
            
            print(f"Total de registros obtidos: {len(df)}")
            return df
        else:
            print("Nenhum dado encontrado para o período.")
            return None
    else:
        print(f"Erro na requisição: {response.status_code}")
        return None


def preencher_dias_faltantes(df):
    
    if df is None or len(df) == 0:
        return df
    
    data_min = df['data'].min()
    data_max = df['data'].max()
    
    todos_dias = pd.date_range(start=data_min, end=data_max, freq='D')
    
    df_completo = pd.DataFrame({'data': todos_dias.date})
    
    df_por_dia = df.groupby('data').agg({
        'cotacaoCompra': 'mean',
        'cotacaoVenda': 'mean'
    }).reset_index()
    
    df_completo = df_completo.merge(df_por_dia, on='data', how='left')
    
    # Preenche valores faltantes com o valor anterior (forward fill)
    df_completo['cotacaoCompra'] = df_completo['cotacaoCompra'].fillna(method='ffill')
    df_completo['cotacaoVenda'] = df_completo['cotacaoVenda'].fillna(method='ffill')
    
    return df_completo


def plotar_grafico_cotacao(df, periodo):    
    if df is None or len(df) == 0:
        print("Sem dados para plotar")
        return
    
    df_completo = preencher_dias_faltantes(df)
    
    data_ref = datetime.strptime(periodo, "%m%Y")
    mes_ano = data_ref.strftime("%B de %Y").title()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_completo['data'],
        y=df_completo['cotacaoCompra'],
        mode='lines+markers',
        name='Cotação de Compra',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=5)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_completo['data'],
        y=df_completo['cotacaoVenda'],
        mode='lines+markers',
        name='Cotação de Venda',
        line=dict(color='#ff7f0e', width=2),
        marker=dict(size=5)
    ))
    
    media_compra = df_completo['cotacaoCompra'].mean()
    max_compra = df_completo['cotacaoCompra'].max()
    min_compra = df_completo['cotacaoCompra'].min()
    
    fig.update_layout(
        title=f'Cotação do Dólar (USD/BRL) - {mes_ano}',
        xaxis_title='Data',
        yaxis_title='Cotação (R$)',
        hovermode='x unified',
        template='plotly_white',
        height=600,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    fig.add_annotation(
        text=f"Média: R$ {media_compra:.4f}<br>Máxima: R$ {max_compra:.4f}<br>Mínima: R$ {min_compra:.4f}",
        xref="paper", yref="paper",
        x=0.98, y=0.02,
        showarrow=False,
        bgcolor="white",
        bordercolor="gray",
        borderwidth=1,
        xanchor='right',
        yanchor='bottom'
    )
    
    fig.show()
    
    print(f"\n📊 Estatísticas da Cotação de Compra:")
    print(f"   Média: R$ {media_compra:.4f}")
    print(f"   Máxima: R$ {max_compra:.4f}")
    print(f"   Mínima: R$ {min_compra:.4f}")
    print(f"   Variação: R$ {max_compra - min_compra:.4f}")

if __name__ == "__main__":

    periodo = "082021"
    

    df_cotacoes = obter_cotacao_dolar(periodo)
    
    if df_cotacoes is not None:
        plotar_grafico_cotacao(df_cotacoes, periodo)
