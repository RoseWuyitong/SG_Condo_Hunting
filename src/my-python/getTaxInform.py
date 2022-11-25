import re
from urllib.request import Request, urlopen
import pandas as pd
from bs4 import BeautifulSoup
import warnings
import datetime
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")


def main():
    url = "http://www.iras.gov.sg/taxes/property-tax/property-owners/property-tax-rates"
    dictDf = {}
    tables = getTableFrom(url)
    for i in range(3):
        tableI, headerI = getDataFrom(tables[i])
        dictDf[headerI] = tableI
    saveJsonTo(dictDf)
    savePngTo(dictDf)


def getTableFrom(url):
    req = Request(
        url=url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    webpage = urlopen(req).read()
    condaStr = webpage.decode("utf8")

    soup = BeautifulSoup(condaStr, 'lxml')
    tables = soup.find_all('table')
    return tables


def getDataFrom(parsedTable):
    data = [[''.join(th.stripped_strings)
            for th in parsedTable.find('tr').find_all('th')]]
    header = re.findall("\d{1,2} [A-Z][a-z]+ \d{4}", data[0][1])[0]
    header = datetime.datetime.strptime(
        header, '%d %b %Y').strftime('%d-%b-%Y')
    for row in parsedTable.find_all('tr'):
        firstRow, secRow = [], []
        for td in row.find_all('td'):
            try:
                first, sec = "\n".join(
                    td.find('p').stripped_strings).split('\n')
            except:
                first = "\n".join(td.find('p').stripped_strings).split('\n')[0]
                sec = None
            firstRow.append(''.join(re.findall('[0-9]+|None', str(first))))
            secRow.append(''.join(re.findall('[0-9]+|None', str(sec))))
        if "" not in firstRow:
            data.append(firstRow)
        data.append(secRow)
    df = pd.DataFrame(data[3:], columns=data[0])
    return df, header


def saveJsonTo(dictDf, fileName="./DataInJson/TaxInform.json"):
    df = pd.DataFrame.from_dict(dictDf.items())
    df.to_json(fileName, orient="index")


def savePngTo(dictDf, fileName="./GraphInPng/TaxInformCompare.png"):
    xTicker, xLim, y1Ticker, y1Lim, y2Ticker, y2Lim = [], [], [], [], [], []
    colors = ["#FA8072", "#FF0000", "#8B0000"]
    c1 = iter(colors)
    c2 = iter(colors)
    width = iter([3, 4, 5])

    for date, df in dict(reversed(dictDf.items())).items():
        x = [
            0] + list(df.iloc[:-1, 0:1].applymap(lambda _: (int(_)/1000)).iloc[:, 0].values)
        y1 = [
            0] + list(df.iloc[:-1, 2:3].applymap(lambda _: (int(_))).iloc[:, 0].values)
        y2 = list(df.iloc[:, 1:2].applymap(
            lambda _: (int(_))).iloc[:, 0].values)

        for i in range(1, len(df)):
            x[i] = x[i-1]+x[i]
            y1[i] = y1[i-1]+y1[i]

        xLim.append(x[-1])
        y1Lim.append(y1[-1])
        y2Lim.append(y2[-1])
        xTicker = list(set(xTicker+x))
        y1Ticker = list(set(y1Ticker+y1))
        y2Ticker = list(set(y2Ticker+y2))

        plt.figure(1, figsize=(8, 10))
        plt.stackplot(x+[10**4], y1+[(10**7-x[-1])*y2[-1] *
                      0.01+y1[-1]], labels=[date], colors=next(c1))
        plt.plot(x[1:], y1[1:], 'o', color='black', label='_nolegend_')
        for i in range(1, len(x)):
            plt.text(x[i]+1, y1[i]+1, f'{str(y2[i])}%', fontsize='large')
        plt.xlim([0, max(xLim)+5])
        plt.ylim([0, max(y1Lim)+1000])
        plt.xticks(xTicker, fontsize='large')
        plt.yticks(y1Ticker, fontsize='large')
        plt.grid(True)
        plt.xlabel("Annual Value (in Thousand)", fontsize='large')
        plt.ylabel("Property Tax Payable", fontsize='large')
        plt.title("Cumulative Owner-occupier Tax Amount", fontsize='large')
        plt.legend(bbox_to_anchor=(0.107, 1.105), loc='upper center')
        plt.savefig("./GraphInPng/TaxInformGraph_Amount.png")

        plt.figure(2, figsize=(10, 8))
        plt.step(x+[10**10], y2+[y2[-1]], label=date, where='post',
                 color=next(c2), linewidth=next((iter(width))))
        for i in range(1, len(x)):
            plt.text(x[i]+2, y2[i]+0.3, f'{str(y2[i])}%', fontsize='large')
        plt.xlim([0, max(xLim)+8])
        plt.ylim([0, max(y2Lim)+2])
        plt.xticks(xTicker, fontsize='large')
        plt.yticks(y2Ticker, fontsize='large')
        plt.grid(True)
        plt.xlabel("Annual Value (in Thousand)", fontsize='large')
        plt.ylabel("Property Tax Payable", fontsize='large')
        plt.title("Owner-occupier Tax in Percentage", fontsize='large')
        plt.legend(bbox_to_anchor=(0.105, 1.132), loc='upper center')
        plt.savefig("./GraphInPng/TaxInformGraph_Percent.png")


if __name__ == '__main__':
    main()
