import requests
import folium
from folium import plugins
import json

class SPTransAPI:
    
    def __init__(self, token):
        self.token = token
        self.base_url = "http://api.olhovivo.sptrans.com.br/v2.1"
        self.authenticated = False
        self.session = requests.Session()
        
    def autenticar(self):
        url = f"{self.base_url}/Login/Autenticar?token={self.token}"
        
        try:
            response = self.session.post(url, data='')
            
            print(f"📡 Autenticando na API SPTrans...")
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
            if response.status_code == 200:
                result = response.text.strip().lower()
                if result == 'true':
                    self.authenticated = True
                    print("✅ Autenticado com sucesso!\n")
                    return True
                else:
                    print("❌ Autenticação falhou - token inválido\n")
                    return False
            else:
                print(f"❌ Erro HTTP: {response.status_code}\n")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao autenticar: {e}\n")
            return False
    
    def buscar_linhas(self, termo):
        if not self.authenticated:
            print("❌ Você precisa autenticar primeiro!")
            return []
        
        url = f"{self.base_url}/Linha/Buscar?termosBusca={termo}"
        
        try:
            response = self.session.get(url)
            
            print(f"🔍 Buscando linhas com termo: '{termo}'")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                linhas = response.json()
                print(f"✅ Encontradas {len(linhas)} linhas\n")
                return linhas
            else:
                print(f"❌ Erro: {response.status_code}\n")
                return []
                
        except Exception as e:
            print(f"❌ Erro: {e}\n")
            return []
    
    def obter_paradas(self, codigo_linha):
        if not self.authenticated:
            print("❌ Você precisa autenticar primeiro!")
            return []
        
        url = f"{self.base_url}/Parada/BuscarParadasPorLinha?codigoLinha={codigo_linha}"
        
        try:
            response = self.session.get(url)
            
            print(f"🚏 Buscando paradas da linha {codigo_linha}...")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                paradas = response.json()
                print(f"✅ Encontradas {len(paradas)} paradas\n")
                return paradas
            else:
                print(f"❌ Erro: {response.status_code}\n")
                return []
                
        except Exception as e:
            print(f"❌ Erro: {e}\n")
            return []
    
    def obter_posicoes(self, codigo_linha):
        if not self.authenticated:
            print("❌ Você precisa autenticar primeiro!")
            return []
        
        url = f"{self.base_url}/Posicao/Linha?codigoLinha={codigo_linha}"
        
        try:
            response = self.session.get(url)
            
            print(f"🚌 Buscando posições em tempo real...")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                dados = response.json()
                
                if isinstance(dados, dict) and 'vs' in dados:
                    veiculos = dados['vs']
                    print(f"✅ {len(veiculos)} ônibus em operação\n")
                    return veiculos
                else:
                    print("ℹ️  Nenhum ônibus em operação no momento\n")
                    return []
            else:
                print(f"❌ Erro: {response.status_code}\n")
                return []
                
        except Exception as e:
            print(f"❌ Erro: {e}\n")
            return []


def criar_mapa_linha(api, codigo_linha, nome_linha):
    print("="*70)
    print(f"🗺️  GERANDO MAPA PARA: {nome_linha}")
    print("="*70 + "\n")
    
    paradas = api.obter_paradas(codigo_linha)
    
    if not paradas:
        print("⚠️  Não foi possível obter paradas. Verifique o código da linha.")
        return None
    
    veiculos = api.obter_posicoes(codigo_linha)
    
    paradas_validas = [p for p in paradas if p.get('py', 0) != 0 and p.get('px', 0) != 0]
    
    if not paradas_validas:
        print("⚠️  Nenhuma parada com coordenadas válidas encontrada.")
        return None
    
    lats = [p['py'] for p in paradas_validas]
    lons = [p['px'] for p in paradas_validas]
    centro = [sum(lats)/len(lats), sum(lons)/len(lons)]
    
    print(f"📍 Centro do mapa: {centro[0]:.6f}, {centro[1]:.6f}")
    
    mapa = folium.Map(
        location=centro,
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    grupo_paradas = folium.FeatureGroup(name='🚏 Paradas')
    
    for parada in paradas_validas:
        folium.Marker(
            location=[parada['py'], parada['px']],
            popup=folium.Popup(
                f"<b style='font-size:14px;'>{parada['np']}</b><br>"
                f"<b>Código:</b> {parada['cp']}<br>"
                f"<b>Endereço:</b> {parada['ed']}<br>"
                f"<b>Coordenadas:</b> {parada['py']:.6f}, {parada['px']:.6f}",
                max_width=300
            ),
            tooltip=f"🚏 {parada['np']}",
            icon=folium.Icon(color='blue', icon='stop', prefix='fa')
        ).add_to(grupo_paradas)
    
    grupo_paradas.add_to(mapa)
    print(f"✅ {len(paradas_validas)} paradas adicionadas ao mapa (AZUL)")
    
    if veiculos:
        grupo_veiculos = folium.FeatureGroup(name='🚌 Ônibus')
        veiculos_validos = 0
        
        for veiculo in veiculos:
            if veiculo.get('py', 0) != 0 and veiculo.get('px', 0) != 0:
                prefixo = veiculo.get('p', 'N/A')
                hora = veiculo.get('hr', 'N/A')
                acessivel = veiculo.get('a', False)
                
                folium.Marker(
                    location=[veiculo['py'], veiculo['px']],
                    popup=folium.Popup(
                        f"<b style='font-size:14px;'>🚌 Ônibus {prefixo}</b><br>"
                        f"<b>Hora:</b> {hora}<br>"
                        f"<b>Acessível:</b> {'✅ Sim' if acessivel else '❌ Não'}<br>"
                        f"<b>Coordenadas:</b> {veiculo['py']:.6f}, {veiculo['px']:.6f}",
                        max_width=250
                    ),
                    tooltip=f"🚌 Ônibus {prefixo}",
                    icon=folium.Icon(color='red', icon='bus', prefix='fa')
                ).add_to(grupo_veiculos)
                veiculos_validos += 1
        
        grupo_veiculos.add_to(mapa)
        print(f"✅ {veiculos_validos} ônibus adicionados ao mapa (VERMELHO)")
    else:
        print("ℹ️  Nenhum ônibus em circulação no momento")
    
    folium.LayerControl().add_to(mapa)
    
    plugins.Fullscreen(
        position='topright',
        title='Tela cheia',
        title_cancel='Sair da tela cheia'
    ).add_to(mapa)
    
    legenda = f'''
    <div style="
        position: fixed; 
        bottom: 50px; 
        right: 50px; 
        width: 250px;
        background-color: white; 
        border: 3px solid #333;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        padding: 15px;
        font-family: Arial, sans-serif;
        z-index: 9999;
    ">
        <h3 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">
            {nome_linha}
        </h3>
        <div style="margin: 10px 0;">
            <i class="fa fa-stop" style="color: #3498db; font-size: 18px;"></i>
            <span style="margin-left: 10px; font-size: 14px;">
                <b>Paradas:</b> {len(paradas_validas)}
            </span>
        </div>
        <div style="margin: 10px 0;">
            <i class="fa fa-bus" style="color: #e74c3c; font-size: 18px;"></i>
            <span style="margin-left: 10px; font-size: 14px;">
                <b>Ônibus:</b> {len(veiculos) if veiculos else 0}
            </span>
        </div>
    </div>
    '''
    
    mapa.get_root().html.add_child(folium.Element(legenda))
    
    print("\n" + "="*70)
    print("✅ MAPA GERADO COM SUCESSO!")
    print("="*70)
    
    return mapa


def main():
    
    print("\n" + "="*70)
    print(" 🚌 MONITORAMENTO DE FROTA DE ÔNIBUS - API SPTRANS 🚌")
    print("="*70 + "\n")
    
    TOKEN = "18b2210f1fd23dedbcf7e82197fb123d7ed7d72c74f15cfd718b3b1f5e5362ea"
    
    api = SPTransAPI(TOKEN)
    
    if not api.autenticar():
        print("❌ Falha na autenticação. Verifique seu token.")
        return
    
    # ========================================================================
    # ALTERE AQUI A LINHA QUE VOCÊ QUER MONITORAR
    # ========================================================================
    termo_busca = "8000"  # Exemplos: "875N", "8000", "477P", "856P"
    
    # Buscar a linha
    linhas = api.buscar_linhas(termo_busca)
    
    if not linhas:
        print(f"❌ Nenhuma linha encontrada com o termo '{termo_busca}'")
        print("\n💡 Tente outros termos como:")
        print("   - '8000' (Corredor ABD)")
        print("   - '875N' (Jd. Ângela)")
        print("              - '477P' (Lapa)")
        return
    
    print("="*70)
    print("📋 LINHAS ENCONTRADAS:")
    print("="*70)
    
    for i, linha in enumerate(linhas, 1):
        print(f"\n{i}. Letreiro: {linha['lt']}")
        print(f"   Código: {linha['cl']}")
        print(f"   De: {linha['tp']}")
        print(f"   Para: {linha['ts']}")
        print(f"   Sentido: {linha['sl']} (1=Principal→Secundário, 2=Secundário→Principal)")
    
    print("\n" + "="*70)
    
    # Usar primeira linha
    linha = linhas[0]
    
    # Criar mapa
    mapa = criar_mapa_linha(
        api,
        linha['cl'],
        f"{linha['lt']} - {linha['tp']} → {linha['ts']}"
    )
    
    if mapa:
        # Salvar arquivo
        arquivo = f"mapa_linha_{linha['cl']}.html"
        mapa.save(arquivo)
        
        print(f"\n💾 Arquivo salvo: {arquivo}")
        print("🌐 Abra o arquivo no navegador para visualizar o mapa!\n")
        print("="*70 + "\n")
    else:
        print("\n❌ Não foi possível gerar o mapa\n")


# ============================================================================
# EXECUTAR
# ============================================================================

if __name__ == "__main__":
    main()
    