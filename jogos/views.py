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

    if genero and genero != "":
        jogos = [j for j in jogos if j["Genre"].lower() == genero.lower()]

    if plataforma and plataforma != "":
        jogos = [j for j in jogos if j["Platform"].lower() == plataforma.lower()]

    if ano and ano.isdigit():
        ano_int = int(ano)
        jogos = [j for j in jogos if j["Year"] == ano_int]

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
        "generos": generos_unicos,
        "plataformas": plataformas_unicas,
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
    })
    
    return render(request, "jogos/dashboard.html", context)


def estatisticas(request):
    jogos = ler_csv()
    
    genero = request.GET.get('genero', '')
    plataforma = request.GET.get('plataforma', '')
    ano = request.GET.get('ano', '')
    
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
    
    if busca:
        jogos = [j for j in jogos if busca.lower() in j.get('Name', '').lower()]
    if genero:
        jogos = [j for j in jogos if j.get('Genre', '').lower() == genero.lower()]
    if plataforma:
        jogos = [j for j in jogos if j.get('Platform', '').lower() == plataforma.lower()]
    
    if ordenar == 'nome':
        jogos.sort(key=lambda x: x.get('Name', '').lower())
    elif ordenar == '-nome':
        jogos.sort(key=lambda x: x.get('Name', '').lower(), reverse=True)
    elif ordenar == 'ano':
        jogos.sort(key=lambda x: (x.get('Year') is None, x.get('Year') == '', x.get('Year')))
    elif ordenar == '-ano':
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
