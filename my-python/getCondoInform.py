import urllib.request
import pandas as pd
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")


def main():
    url = "https://www.propertyhunt.sg/new-condo-launch/"
    dictDf = {}
    tables = getTableFrom(url)
    for i in range(3):
        tableI = getDataFrom(tables[i])
        dictDf[f"table{i}"] = tableI
        saveJsonTo(dictDf)


def getTableFrom(url):
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    condaStr = mybytes.decode("utf8")
    fp.close()

    soup = BeautifulSoup(condaStr, 'lxml')
    tables = soup.find_all('table')
    return tables


def getDataFrom(parsedTable):
    data = [[''.join(th.stripped_strings)
            for th in parsedTable.find('tr').find_all('th')]]
    linkList = []
    for row in parsedTable.find_all('tr'):
        dataList = []
        for td in row.find_all('td'):
            if td.find('a'):
                link = td.a['href']
                linkList.append(link)
            dataList.append(''.join(td.stripped_strings))
        data.append(dataList)
    df = pd.DataFrame(data[2:], columns=data[0])
    df["Link"] = pd.Series(linkList)
    return df


def saveJsonTo(dictDf, fileName="./DataInJson/CondoInform.json"):
    df = pd.DataFrame.from_dict(dictDf.items())
    df.to_json(fileName, orient='records')


if __name__ == '__main__':
    main()
