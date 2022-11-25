import pandas as pd
import re


def readBankInformJson(url='./DataInJson/BankInform.json'):
    df = pd.read_json(url)
    df.columns = ['bankName', 'information']
    df = df.set_index('bankName', drop=True)
    return df


def getMorgageResult(rateDf, sora3M, condoPrice, downpayPercentage, morgageYears):
    rateDf = pd.DataFrame(rateDf)
    resultDf = rateDf.copy()
    resultDf["Annual Rate"], \
        resultDf["Amount in SGD (Anuually Payment)"], \
        resultDf["Amount in SGD (Monthly Payment)"] = \
        None, None, None
    morgageAmtY = (condoPrice*(1-downpayPercentage))/morgageYears
    morgageAmtM = (condoPrice*(1-downpayPercentage))/(morgageYears*12)
    for i in range(len(rateDf)):
        calculateRateY = 0
        rate = resultDf.loc[i, "Interest Rates"]
        if "3M Compounded SORA" in rate:
            calculateRateY += sora3M
        calculateRateY += float(re.findall(
            r'[0-9]*[0-9].[0-9]*[0-9]*%', rate)[0][:-1])
        calculateRateY = calculateRateY*0.01
        calculateRateM = calculateRateY/12
        resultDf.loc[i, "Annual Rate"] = calculateRateY
        resultDf.loc[i, "Amount in SGD (Anuually Payment)"] = morgageAmtY + \
            morgageAmtY*calculateRateY
        resultDf.loc[i, "Amount in SGD (Monthly Payment)"] = morgageAmtM + \
            morgageAmtM*calculateRateM
    resultDf.loc[-1] = ["Year 0", None, None, condoPrice *
                        (downpayPercentage), condoPrice*(downpayPercentage)]
    resultDf.index = resultDf.index + 1
    resultDf = resultDf.sort_index()
    print(resultDf)
    return resultDf


def saveJsonTo(dictDf, fileName='./ResultInJson/MorgageCalculationResult.json'):
    df = pd.DataFrame.from_dict(dictDf.items())
    df.to_json(fileName, orient="records")


def main():
    sora3M, condoPrice, downpayPercentage = 2.6, 1000000, 0.25
    morgageYears = 30
    jsonDf = readBankInformJson()
    dictDf = {}
    if downpayPercentage < 0.25:
        raise Exception("The percentage need above 0.25.")
    elif downpayPercentage >= 1:
        raise Exception("Please enter percentage under 1.")
    else:
        for bankName in jsonDf.index:
            df = getMorgageResult(
                jsonDf.loc[jsonDf.index == bankName]["information"][0]["rate"],
                sora3M,
                condoPrice,
                downpayPercentage,
                morgageYears)
            dictDf[bankName] = df
    saveJsonTo(dictDf)


if __name__ == '__main__':
    main()
