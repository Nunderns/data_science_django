import json
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.safestring import mark_safe
from .utils import ler_csv
from statistics import mean
from collections import defaultdict
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncYear

def dashboard(request):
    jogos = ler_csv()

    genero = request.GET.get("genero")
    plataforma = request.GET.get("plataforma")
    ano = request.GET.get("ano")
    ocultar_na = request.GET.get("ocultar_na") == "on"

    if genero and genero != "":
        jogos = [j for j in jogos if j["Genre"].lower() == genero.lower()]

    if plataforma and plataforma != "":
        jogos = [j for j in jogos if j["Platform"].lower() == plataforma.lower()]

    if ano and ano.isdigit():
        ano_int = int(ano)
        jogos = [j for j in jogos if j["Year"] == ano_int]
    if ocultar_na:
        jogos = [j for j in jogos if all(j.get(key) is not None and str(j.get(key)).upper() != 'N/A' 
                                      for key in ['Name', 'Platform', 'Year', 'Genre', 'Publisher', 'Global_Sales'])]

    genero_vendas = defaultdict(list)
    for j in jogos:
        genero_vendas[j["Genre"]].append(float(j["Global_Sales"]))
    
    genero_ordenado = sorted(
        [(k, sum(v)/len(v)) for k, v in genero_vendas.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    labels = [g[0] for g in genero_ordenado]
    valores = [round(g[1], 2) for g in genero_ordenado]

    plataformas = {}
    for j in jogos:
        plataformas[j["Platform"]] = plataformas.get(j["Platform"], 0) + 1
    
    plataformas_ordenadas = sorted(plataformas.items(), key=lambda x: x[1], reverse=True)
    plataformas_labels = [p[0] for p in plataformas_ordenadas]
    plataformas_quantidades = [p[1] for p in plataformas_ordenadas]

    vendas_por_ano = defaultdict(float)
    for j in jogos:
        if j["Year"]:
            vendas_por_ano[j["Year"]] += float(j["Global_Sales"])
    
    anos_ordenados = sorted(vendas_por_ano.items())
    anos_labels = [str(a[0]) for a in anos_ordenados]
    anos_vendas = [round(a[1], 2) for a in anos_ordenados]

    top_jogos = sorted(
        jogos,
        key=lambda x: float(x["Global_Sales"]),
        reverse=True
    )[:10]
    top10_labels = [j["Name"] for j in top_jogos]
    top10_values = [float(j["Global_Sales"]) for j in top_jogos]
    
    # Calcular estatísticas adicionais
    if jogos:
        maior_venda = max(float(j.get('Global_Sales', 0)) for j in jogos)
        vendas_globais = [float(j.get('Global_Sales', 0)) for j in jogos if j.get('Global_Sales')]
        total_vendas = sum(vendas_globais)
        media_vendas = total_vendas / len(vendas_globais) if vendas_globais else 0
        
        # Encontrar ano mais lucrativo
        vendas_por_ano = {}
        for j in jogos:
            if j.get('Year'):
                vendas_por_ano[j['Year']] = vendas_por_ano.get(j['Year'], 0) + float(j.get('Global_Sales', 0))
        ano_mais_lucrativo = max(vendas_por_ano.items(), key=lambda x: x[1])[0] if vendas_por_ano else "N/A"
        
        # Encontrar gênero mais popular
        genero_contagem = {}
        for j in jogos:
            if j.get('Genre'):
                genero_contagem[j['Genre']] = genero_contagem.get(j['Genre'], 0) + 1
        genero_popular = max(genero_contagem.items(), key=lambda x: x[1])[0] if genero_contagem else "N/A"
    else:
        maior_venda = 0
        total_vendas = 0
        media_vendas = 0
        ano_mais_lucrativo = "N/A"
        genero_popular = "N/A"

    todos_jogos = ler_csv()
    generos_unicos = sorted(list(set([j['Genre'] for j in todos_jogos if j.get('Genre')])))
    plataformas_unicas = sorted(list(set([j['Platform'] for j in todos_jogos if j.get('Platform')])))
    
    print("Dados dos gráficos:")
    print(f"Labels: {labels}")
    print(f"Valores: {valores}")
    print(f"Plataformas: {plataformas_labels}")
    print(f"Quantidades: {plataformas_quantidades}")
    print(f"Anos: {anos_labels}")
    print(f"Vendas por ano: {anos_vendas}")
    print(f"Top 10 labels: {top10_labels}")
    print(f"Top 10 values: {top10_values}")
    
    context = {
        "jogos": jogos[:100],
        "labels": labels,
        "valores": valores,
        "plataformas_labels": plataformas_labels,
        "plataformas_quantidades": plataformas_quantidades,
        "plataformas_unicas": len(plataformas),
        "anos_labels": anos_labels,
        "anos_vendas": anos_vendas,
        "top10_labels": top10_labels,
        "top10_values": top10_values,
        "labels_json": mark_safe(json.dumps(labels)),
        "valores_json": mark_safe(json.dumps(valores)),
        "plataformas_labels_json": mark_safe(json.dumps(plataformas_labels)),
        "plataformas_quantidades_json": mark_safe(json.dumps(plataformas_quantidades)),
        "anos_labels_json": mark_safe(json.dumps(anos_labels)),
        "anos_vendas_json": mark_safe(json.dumps(anos_vendas)),
        "top10_labels_json": mark_safe(json.dumps(top10_labels)),
        "top10_values_json": mark_safe(json.dumps(top10_values)),
        "filtro_genero": genero or "",
        "filtro_plataforma": plataforma or "",
        "filtro_ano": ano or "",
        "filtro_ocultar_na": ocultar_na,
        "generos": generos_unicos,
        "plataformas": plataformas_unicas,
        "anos": sorted(list(set([j['Year'] for j in todos_jogos if j.get('Year') is not None])), reverse=True),
    }
    
    context.update({
        "labels": labels,
        "valores": valores,
        "plataformas_labels": plataformas_labels,
        "plataformas_quantidades": plataformas_quantidades,
        "anos_labels": anos_labels,
        "anos_vendas": anos_vendas,
        "top10_labels": top10_labels,
        "top10_values": top10_values,
        "maior_venda": round(maior_venda, 2),
        "vendas_totais": round(total_vendas, 2),
        "media_vendas": round(media_vendas, 2),
        "ano_mais_lucrativo": ano_mais_lucrativo,
        "genero_popular": genero_popular,
        "plataformas_unicas": len(plataformas) if 'plataformas' in locals() else 0
    })
    
    return render(request, "jogos/dashboard.html", context)


def estatisticas(request):
    jogos = ler_csv()
    
    genero = request.GET.get('genero', '')
    plataforma = request.GET.get('plataforma', '')
    ano = request.GET.get('ano', '')
    ocultar_na = request.GET.get('ocultar_na') == 'on'
    
    if genero:
        jogos = [j for j in jogos if j.get('Genre', '').lower() == genero.lower()]
    if plataforma:
        jogos = [j for j in jogos if j.get('Platform', '').lower() == plataforma.lower()]
    if ano:
        try:
            ano_int = int(ano)
            jogos = [j for j in jogos if j.get('Year') == ano_int]
        except (ValueError, TypeError):
            pass
            
    # Filtrar registros com valores N/A se a opção estiver ativada
    if ocultar_na:
        jogos = [j for j in jogos if all(j.get(key) is not None and str(j.get(key)).upper() != 'N/A' 
                                      for key in ['Name', 'Platform', 'Year', 'Genre', 'Publisher', 'Global_Sales'])]
    
    generos = defaultdict(float)
    for jogo in jogos:
        if 'Genre' in jogo and 'Global_Sales' in jogo:
            try:
                generos[jogo['Genre']] += float(jogo['Global_Sales'])
            except (ValueError, TypeError):
                continue
    
    generos_ordenados = sorted(generos.items(), key=lambda x: x[1], reverse=True)
    generos_labels = [g[0] for g in generos_ordenados]
    generos_valores = [round(g[1], 2) for g in generos_ordenados]
    
    plataformas = defaultdict(float)
    for jogo in jogos:
        if 'Platform' in jogo and 'Global_Sales' in jogo:
            try:
                plataformas[jogo['Platform']] += float(jogo['Global_Sales'])
            except (ValueError, TypeError):
                continue
    
    plataformas_ordenadas = sorted(plataformas.items(), key=lambda x: x[1], reverse=True)[:10]
    plataformas_labels = [p[0] for p in plataformas_ordenadas]
    plataformas_valores = [round(p[1], 2) for p in plataformas_ordenadas]
    
    vendas_ano = defaultdict(float)
    for jogo in jogos:
        if 'Year' in jogo and jogo['Year'] and 'Global_Sales' in jogo:
            try:
                vendas_ano[jogo['Year']] += float(jogo['Global_Sales'])
            except (ValueError, TypeError):
                continue
    
    anos_ordenados = sorted(vendas_ano.items())
    anos_labels = [str(a[0]) for a in anos_ordenados if a[0]]
    anos_valores = [round(a[1], 2) for a in anos_ordenados if a[0]]
    
    todos_jogos = ler_csv()
    generos_unicos = sorted(list(set([j['Genre'] for j in todos_jogos if j.get('Genre')])))
    plataformas_unicas = sorted(list(set([j['Platform'] for j in todos_jogos if j.get('Platform')])))
    
    return render(request, 'jogos/estatisticas.html', {
        'generos': generos_unicos,
        'plataformas': plataformas_unicas,
        'filtro_genero': genero,
        'filtro_plataforma': plataforma,
        'filtro_ano': ano,
        'generos_labels': generos_labels,
        'generos_valores': generos_valores,
        'plataformas_labels': plataformas_labels,
        'plataformas_valores': plataformas_valores,
        'anos_labels': anos_labels,
        'anos_valores': anos_valores,
    })


def lista_jogos(request):
    jogos = ler_csv()
    
    busca = request.GET.get('busca', '').strip()
    genero = request.GET.get('genero', '')
    plataforma = request.GET.get('plataforma', '')
    ordenar = request.GET.get('ordenar', '-vendas')
    ocultar_na = request.GET.get('ocultar_na') == 'on'
    
    if busca:
        jogos = [j for j in jogos if busca.lower() in j.get('Name', '').lower()]
    if genero:
        jogos = [j for j in jogos if j.get('Genre', '').lower() == genero.lower()]
    if plataforma:
        jogos = [j for j in jogos if j.get('Platform', '').lower() == plataforma.lower()]
    if ocultar_na:
        jogos = [j for j in jogos if all(j.get(key) is not None and str(j.get(key, '')).upper() != 'N/A' 
                                      for key in ['Name', 'Platform', 'Year', 'Genre', 'Publisher', 'Global_Sales'])]
    
    if ordenar == 'nome':
        jogos.sort(key=lambda x: x.get('Name', '').lower())
    elif ordenar == '-nome':
        jogos.sort(key=lambda x: x.get('Name', '').lower(), reverse=True)
    elif ordenar == 'ano':
        if ocultar_na:
            jogos.sort(key=lambda x: x.get('Year', 0))
        else:
            jogos.sort(key=lambda x: (x.get('Year') is None, x.get('Year') == '', x.get('Year')))
    elif ordenar == '-ano':
        if ocultar_na:
            jogos.sort(key=lambda x: x.get('Year', 0), reverse=True)
        else:
            jogos.sort(key=lambda x: (x.get('Year') is None, x.get('Year') == '', x.get('Year')), reverse=True)
    elif ordenar == 'vendas':
        jogos.sort(key=lambda x: float(x.get('Global_Sales', 0)))
    else:
        jogos.sort(key=lambda x: float(x.get('Global_Sales', 0)), reverse=True)
    
    paginador = Paginator(jogos, 25)
    pagina = request.GET.get('pagina')
    jogos_paginados = paginador.get_page(pagina)
    
    todos_jogos = ler_csv()
    generos_unicos = sorted(list(set([j['Genre'] for j in todos_jogos if j.get('Genre')])))
    plataformas_unicas = sorted(list(set([j['Platform'] for j in todos_jogos if j.get('Platform')])))
    
    return render(request, 'jogos/lista_jogos.html', {
        'jogos': jogos_paginados,
        'busca': busca,
        'generos': generos_unicos,
        'plataformas': plataformas_unicas,
        'filtro_genero': genero,
        'filtro_plataforma': plataforma,
    })
