import requests, json
import numpy as np
import operator

URL = "https://dolphin.jump-technology.com:8443/api/v1/"
AUTH = ("EPITA_GROUPE4", "vRkt9KhQZThs5hQg")

ALL_ASSETS = {}
VAL_PORTFOLIO = 0.0

def columns_to_str(columns):
    if columns != []:
        return "?columns=" + "&columns=".join(columns)
    return ""

def beautify(jsoned):
    print(json.dumps(jsoned,indent=2))

def get_data(endpointApi, columns=list(), date="2013-06-14"):
    date_str = ""
    if columns == [] :
        date_str = "?date=" + date
    else:
        date_str = "&date=" + date
    response = requests.get(URL + endpointApi + columns_to_str(columns) + date_str, auth=AUTH)
    if response.status_code == 200 and response != "" :
        return json.loads(response.content.decode('utf-8'))
    return ""

def get_portofolio(endpointApi, id):
    response = requests.get(URL + endpointApi + id + "/dyn_amount_compo", auth=AUTH)
    if response.status_code == 200 and response != "" :
        return json.loads(response.content.decode('utf-8'))
    return ""

def convertToEUR(amount, money):
    if money != "EUR":
        response = requests.get(URL + "currency/rate/" + money + "/to/EUR", auth=AUTH)
        if response.status_code == 200 and response != "":
            tmp = json.loads(response.content.decode('utf-8'))
            tmp = np.float(tmp["rate"]["value"].replace(',','.'))
            res = tmp * amount
            return res
        return ""
    else:
        return amount    

def post_data(endpointApi, ratios=list(), assets=list()):
    body = json.dumps({
        "ratio": ratios,
        "asset": assets,
        "bench": None,
        "start_date": "2013-06-14",
        "end_date": "2019-04-18",
        "frequency": None
    })
    response = requests.post(URL + endpointApi, body, auth=AUTH)
    if response.status_code == 200 and response != "" :
        return json.loads(response.content.decode('utf-8'))
    return ""

def filter_assets():
    assets = get_data("asset", columns=["ASSET_DATABASE_ID", "CURRENCY", "LAST_CLOSE_VALUE_IN_CURR", "TYPE"])
    for asset in assets:
        if "LAST_CLOSE_VALUE_IN_CURR" in asset:
            Id = asset["ASSET_DATABASE_ID"]["value"]
            if asset["TYPE"]["value"] not in ["PORTFOLIO", "INDEX"]:
                ALL_ASSETS[Id] = asset

def choose_assets(count=[15], strategy=["SHARPE"]):
    filter_assets()
    all_assets_ratios = post_data("ratio/invoke", ratios=[9, 10, 12, 13], assets=list(ALL_ASSETS))
    assets_ratios = []
    sharpe_ratios = []
    volatility_ratios = []
    rendement_ratios = []
    rendement_annuel_ratios = []
    for asset in all_assets_ratios:
        if all_assets_ratios[asset]["12"]["type"] != "error":
            sharpe_ratios.append(
                (
                    int(asset),
                    float(all_assets_ratios[asset]['12']['value'].replace(',', '.'))
                )
        )
        if all_assets_ratios[asset]["13"]["type"] != "error":
            rendement_ratios.append(
                (
                    int(asset),
                    float(all_assets_ratios[asset]['13']['value'].replace(',', '.'))
                )
        )
        if all_assets_ratios[asset]["9"]["type"] != "error":
            rendement_annuel_ratios.append(
                (
                    int(asset),
                    float(all_assets_ratios[asset]['9']['value'].replace(',', '.'))
                )
        )
        if all_assets_ratios[asset]["10"]["type"] != "error":
            volatility_ratios.append(
                (
                    int(asset),
                    float(all_assets_ratios[asset]['10']['value'].replace(',', '.'))
                )
        )
    sharpe_ratios.sort(key=operator.itemgetter(1), reverse=True)
    volatility_ratios.sort(key=operator.itemgetter(1))
    rendement_ratios.sort(key=operator.itemgetter(1), reverse=True)
    rendement_annuel_ratios.sort(key=operator.itemgetter(1), reverse=True)
    assets_ratios += [sharpe_ratios, volatility_ratios, rendement_ratios, rendement_annuel_ratios]
    selection = []
    for i in range (len(count)):
        if (strategy[i] == "SHARPE"):
            selection += sharpe_ratios[:count[i]]
        elif (strategy[i] == "VOLATILITY"):
            selection += volatility_ratios[:count[i]]
        elif (strategy[i] == "RENDEMENT"):
            selection += rendement_ratios[:count[i]]
        elif (strategy[i] == "RENDEMENT_ANNUEL"):
            selection += rendement_annuel_ratios[:count[i]]
    res = list(dict(selection))
    return res

def calcul_portfolio(assets):
    res = 0.0
    for asset in assets:
        currency = ALL_ASSETS[str(asset[0])]["CURRENCY"]["value"]
        val = float((ALL_ASSETS[str(asset[0])]["LAST_CLOSE_VALUE_IN_CURR"]["value"].replace(" " + currency, "")).replace(',', '.'))
        val = convertToEUR(val, currency)
        res += val * float(asset[1])
    return res

def calcul_ratio(assets):
    ratios = []
    res = calcul_portfolio(assets)
    for asset in assets:
        currency = ALL_ASSETS[str(asset[0])]["CURRENCY"]["value"]
        val = float((ALL_ASSETS[str(asset[0])]["LAST_CLOSE_VALUE_IN_CURR"]["value"].replace(" " + currency, "")).replace(',', '.'))
        val = convertToEUR(val, currency)
        ratios.append((asset[0], float(val * float(asset[1] * 100/ res))))
    ratios.sort(key=operator.itemgetter(1), reverse=True)
    return ratios

def calcul_quantities(assets):
    quantities = []
    ratios = calcul_ratio(assets)
    max_ratio = ratios[0]
    ratios = dict(ratios)
    for asset in assets:
        if asset[0] != max_ratio[0]:
            quantities.append((asset[0], round(max_ratio[1] * asset[1] / ratios[asset[0]])))
        else:
            quantities.append((asset[0], 10))
    return quantities

def put_portfolio(portfolio):
    response = requests.put(URL + 'portfolio/1823/dyn_amount_compo', data=json.dumps(portfolio), auth=AUTH)
    response = requests.put(URL + 'portfolio/1823/dyn_amount_compo', data=json.dumps(portfolio), auth=AUTH)
    return response

def generate_portfolio(assets):
    tmp = []
    for asset in assets:
        tmp.append({
            "asset": {
                "asset": asset[0],
                "quantity": asset[1]
            }
        })
    portfolio = {
        "label": "EPITA_PTF_4",
        "currency": {
            "code": "EUR"
        },
        "type": "front",
        "values": {
            "2013-06-14": tmp
        }
    }
    return portfolio

def check_action(assets):
    res = 0.0
    total = calcul_portfolio(assets)
    for asset in assets:
        if ALL_ASSETS[str(asset[0])]["TYPE"]["value"] == "STOCK":
            currency = ALL_ASSETS[str(asset[0])]["CURRENCY"]["value"]
            val = float((ALL_ASSETS[str(asset[0])]["LAST_CLOSE_VALUE_IN_CURR"]["value"].replace(" " + currency, "")).replace(',', '.'))
            val = convertToEUR(val, currency)
            res += val * float(asset[1])
    print("Ratio action : ", res * 100 / total, "%")
    return (res * 100 / total)

def check_nav(assets):
    total = calcul_portfolio(assets)
    som = 0.0
    ratios = []
    for asset in assets:
        res = 0.0
        currency = ALL_ASSETS[str(asset[0])]["CURRENCY"]["value"]
        val = float((ALL_ASSETS[str(asset[0])]["LAST_CLOSE_VALUE_IN_CURR"]["value"].replace(" " + currency, "")).replace(',', '.'))
        val = convertToEUR(val, currency)
        res = val * float(asset[1]) * 100 / total
        som += res
        ratios.append((asset[0], res))
    for i in ratios:
        print("L'asset ", i[0], " représente ", i[1], "% de votre portefeuille")
    print("TOTAL des pourcentages : ", som)
    return (ratios)

def get_sharp():
    url = "https://dolphin.jump-technology.com:8443/api/v1/ratio/invoke"
    body = {
	    "ratio": [12],
	    "asset": [1823],
	    "start_date": "2013-06-14",
	    "end_date": "2019-04-18"
    }
    body = json.dumps(body)
    response = requests.post(url, body, auth=AUTH)
    response = json.loads(response.content.decode('utf-8'))
    return response["1823"]["12"]["value"]

def optimisation(res):
    COEFF = 4
    sharpe = get_sharp()
    res = dict(res)
    for asset in res:
        res[asset] = round(res[asset] * COEFF)
        put_portfolio(generate_portfolio(list(res.items())))
        new = get_sharp()
        if new > sharpe :
            sharpe = new
        elif new < sharpe :
            res[asset] = round(res[asset] / (COEFF * 2))
            put_portfolio(generate_portfolio(list(res.items())))
            new = get_sharp()
            if new > sharpe :
                sharpe = new
            else :
                res[asset] = round(res[asset] * COEFF)
        else :
            res[asset] = round(res[asset] / COEFF)
        print(sharpe)
    return list(res.items())


def main():
    test = choose_assets([25, 0, 0, 0], ["SHARPE", "VOLATILITY", "RENDEMENT", "RENDEMENT_ANNUEL"])
    l = []
    for i in range(len(test)):
        l.append((test[i], 10))
    res = calcul_quantities(l)
    portfolio = generate_portfolio(res)
    put_portfolio(portfolio)
    res = optimisation(res)
    portfolio = generate_portfolio(res)
    put_portfolio(portfolio)
    check_nav(res)
    check_action(res)
     

if __name__ == '__main__':
    main()