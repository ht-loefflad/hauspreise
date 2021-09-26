# TODO: Check data for cities and their adjunct rural areas
import pandas as pd
import time
import bs4 as bs
import urllib.request
import json

# def transpose(list):
#     transposed_list = [[list[x][y] for x in range(len(list))] for y in range(len(list[0]))]
#     return transposed_list


def grab_data(table_number, house_price=1):
    table_soup = soup.find_all('tbody')[table_number]  # Grab table
    table_soup = table_soup.find_all('tr')
    df = pd.DataFrame([[td.findChildren(text=True)[0] for td in tr.findAll("td")] for tr in table_soup],
                      columns=["Quarter", "Price", "Change"]
                      )
    df["House Price"] = pd.Series([house_price] * len(table_soup), index=df.index)
    return df


def add_id(GEN, RS):
    data["GEN"] = pd.Series([str(GEN)] * len(data), index=data.index)
    data["RS"] = pd.Series([str(RS)] * len(data), index=data.index)


with open('data/landkreise_simplify200.geojson', encoding="utf-8") as response:
    counties = json.load(response)

# print(counties["features"][0]["properties"])

county_names = []
for county in counties["features"]:
    county_name = [county["properties"]['GEN'], county["properties"]['RS']]
    # county_name = county_name.replace(" ", "+")
    county_names.append(county_name)

Kreise = pd.DataFrame(county_names[:], columns=['GEN', 'RS'])
Kreise2 = pd.DataFrame(county_names[:], columns=['GEN', 'RS'])
# print(Kreise.head())

# replace umlauts
Kreise2["GEN"] = Kreise2["GEN"].str.replace("ä", "ae")
Kreise2["GEN"] = Kreise2["GEN"].str.replace("ö", "oe")
Kreise2["GEN"] = Kreise2["GEN"].str.replace("ü", "ue")
Kreise2["GEN"] = Kreise2["GEN"].str.replace("Ä", "Ae")
Kreise2["GEN"] = Kreise2["GEN"].str.replace("Ö", "Oe")
Kreise2["GEN"] = Kreise2["GEN"].str.replace("Ü", "Ue")
Kreise2["GEN"] = Kreise2["GEN"].str.replace("ß", "ss")
Kreise.loc[:, 'hp_download_successful'] = pd.Series([0] * len(Kreise), index=Kreise.index)
Kreise.loc[:, 'wp_download_successful'] = pd.Series([0] * len(Kreise), index=Kreise.index)
Kreise.loc[:, 'reason'] = pd.Series([0] * len(Kreise), index=Kreise.index)

print(Kreise.iloc[0:10, 0])
price = pd.DataFrame()
quarter = ["2018/Q3", "2018/Q4", "2019/Q1", "2019/Q2", "2019/Q3", "2019/Q4", "2020/Q1", "2020/Q2", "2020/Q3"]

start = time.time()
for index, row in Kreise.iterrows():      # Full data set: len(Kreise)
    print(f"Loop {index} startet. {row['GEN']}")
    try:
        county = Kreise2.iloc[index, 0].replace(" ", "+")
        soup = bs.BeautifulSoup(
            urllib.request.urlopen(f'https://www.homeday.de/de/preisatlas/{county}'), features="lxml")
        empty_house_price, empty_flat_price = soup.find_all('p', attrs={"class", "price-block__price__average"})
        if empty_house_price.text != "Ø -/m²" and empty_flat_price.text != "Ø -/m²":
            data = grab_data(0)
            data = data.append(grab_data(1, house_price=0))
            add_id(row["GEN"], row["RS"])
            price = price.append(data, ignore_index=True)
            Kreise.at[index, "hp_download_successful"] = 1
            Kreise.at[index, "wp_download_successful"] = 1
        elif empty_house_price.text != "Ø -/m²" and empty_flat_price.text == "Ø -/m²":
            data = grab_data(0)
            add_id(row["GEN"], row["RS"])
            price = price.append(data, ignore_index=True)
            Kreise.at[index, "hp_download_successful"] = 1
        elif empty_house_price.text == "Ø -/m²" and empty_flat_price.text != "Ø -/m²":
            data = grab_data(0, house_price=0)
            add_id(row["GEN"], row["RS"])
            price = price.append(data, ignore_index=True)
            Kreise.at[index, "wp_download_successful"] = 1
    except Exception as e:
        Kreise.at[index, "hp_download_successful"] = 0
        Kreise.at[index, "wp_download_successful"] = 0
        Kreise.loc[index, "reason"] = str(e)
        print(str(e))
price.to_csv("data/price.csv")
Kreise.to_csv("data/Kreise_count.csv")

end = time.time()

print("FERTIG!")


print(Kreise["hp_download_successful"].sum())
print(Kreise["wp_download_successful"].sum())

print(end - start)

# # # # # # # # Grabbing data in an alternative Fashion
# def grab_data(table_number, RS, house_price=1):
#     table_soup = soup.find_all('tbody')[table_number]  # Grab table
#     table_soup = table_soup.find_all('tr')
#     df = pd.DataFrame([[td.findChildren(text=True)[0] for td in tr.findAll("td")] for tr in table_soup],
#                       columns=["Quarter", "Price", "Change"]
#                       )
#     # temporary_list = [[td.findChildren(text=True)[0] for td in tr.findAll("td")] for tr in table_soup]
#     # temporary_dictionary = {}
#     # for row in temporary_list:
#     #     temporary_dictionary[row[0]] = row[1]
#     # # print(d)
#     # df2 = pd.DataFrame(temporary_dictionary, index=[RS])
#     # print(df2)
#     df["House Price"] = pd.Series([house_price] * len(table_soup), index=df.index)
#     return df
