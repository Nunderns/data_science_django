import csv
import os
from django.conf import settings

def ler_csv():
    caminho = os.path.join(settings.BASE_DIR, 'jogos', 'data', 'jogos.csv')
    jogos = []

    with open(caminho, encoding='utf-8') as arquivo:
        leitor_csv = csv.DictReader(arquivo)
        for row in leitor_csv:
            rout = {}
            rout["Rank"] = int(row["Rank"])
            rout["Name"] = row["Name"]
            rout["Platform"] = row["Platform"]
            try:
                rout["Year"] = int(row["Year"]) if row["Year"] != 'N/A' else None
            except (ValueError, TypeError):
                rout["Year"] = None
            rout["Genre"] = row["Genre"]
            rout["Publisher"] = row["Publisher"]
            rout["NA_Sales"] = float(row["NA_Sales"])
            rout["EU_Sales"] = float(row["EU_Sales"])
            rout["JP_Sales"] = float(row["JP_Sales"])
            rout["Other_Sales"] = float(row["Other_Sales"])
            rout["Global_Sales"] = float(row["Global_Sales"])
            jogos.append(rout)
    return jogos