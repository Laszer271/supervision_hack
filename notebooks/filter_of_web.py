import requests
from bs4 import BeautifulSoup


#DANE BEZPOŚREDNIO NA STRONIE

# url_bankowy = 'https://www.ing.pl/indywidualni/tabele-i-regulaminy/oprocentowanie/rachunki-oszczednosciowe-lokaty'
# url_bankowy = "https://www.pocztowy.pl/indywidualni/oprocentowanie"
url_bankowy = "https://www.credit-agricole.pl/oprocentowanie" #- z tabelek 

# LINKI PDF 

# url_bankowy = "https://online.banknowy.pl/portal_online/dokumenty"
# url_bankowy = "https://www.bankmillennium.pl/klienci-indywidualni/wsparcie/cenniki-i-regulaminy"


response = requests.get(url_bankowy, )
response.encoding = 'utf-8'
# soup = BeautifulSoup(response.text, 'html.parser')
soup = BeautifulSoup(response.text, 'lxml')


#-----------------------------------------HANDLOWANIE TABEL 


def analyzisOfTables():
    table_words_lokata = []
    table_words_oszczed = []
    tbody_elements = soup.find_all('table')
    if tbody_elements:
        for tbody in tbody_elements:
            # Find all text within the tbody element
            text_inside_tbody = tbody.get_text()

            # Check if the word "lokata" is present
            if ('lokat' and "%") in text_inside_tbody.lower():
                # If found, append the content of the tbody to the list
                table_words_lokata.append(tbody.get_text().strip())

            # Check if the word "lokata" is present
            if ('oszczęd' and "%") in text_inside_tbody.lower():
                # If found, append the content of the tbody to the list
                table_words_oszczed.append(tbody.get_text().strip())
    else:
        print("Nie znalazłem tbody")

    return table_words_lokata,table_words_oszczed
# ----------------------------------------------        



# ----------------------------------------------HANDLOWANIE LINKOW
def getLinks():
    links = soup.find_all("a", href=True)
    links_lokata = []
    links_oszczed = []

    # Iteracja przez wszystkie elementy <a> z atrybutem href w dokumencie
    for link in links:
        if "lokat" in link.get("href", "").lower() or "lokat" in link.get_text(separator=' ').lower():
            # print("href_link", link.get("href"))
            # print("text_link", link.get_text())
            links_lokata.append({"text":link.get_text(),"href":link.get("href")})
        elif "oszczęd" in link.get("href", "").lower() or "oszczęd" in link.get_text(separator=' ').lower():
            # print("href_oszczednosc", link.get("href"))
            # print("text_oszczednosc", link.get_text())
            links_oszczed.append({"text":link.get_text(separator=' '),"href":link.get("href")})
        else:
            continue
    return links_lokata,links_oszczed

# ----------------------------------------------        





# ----------------------------------------------HANDLOWANIE DIVOW / MAIN / SECTION
start_divs = soup.find("body")
div_list = []
lokata_data_end = []
oszczed_data_end = []
links_lokata=[]
links_oszczed=[]
layout = -1

def find_last_divs(divs,layout,isLokata,isOszczednosciowe,layout_lokata,layout_oszczed):
    layout+=1
    dzieci = divs.findChildren(['div', 'section', 'main'],recursive=False)
    i=-1
    for dziecko in dzieci:
        i+=1
        text = dziecko.get_text()
        if (("lokat" and "%") or ("oszczęd" and "%")) in text.lower():
            # print(dziecko.get_text().strip())
            word_count_with_locat = sum(1 for word in dziecko.get_text().strip().lower().split() if "lokat" in word.lower())
            word_count_with_oszczed = sum(1 for word in dziecko.get_text().strip().lower().split() if "oszczęd" in word.lower())
            word_count_with_proc = sum(1 for word in dziecko.get_text().strip().lower().split() if "%" in word.lower())

            #Jezeli konta oszczednosciowe w ogole nie zostały wspomniane na stronie
            if i==0 and layout ==0 and word_count_with_oszczed == 0:
                print("Nie znalazłem oszczędnościowych")
                isOszczednosciowe = False

            #Jezeli konta oszczednosciowe w ogole nie zostały wspomniane na stronie
            if i==0 and layout ==0 and word_count_with_locat == 0:
                print("Nie znalazłem lokat")
                isLokata = False
            
            #handling uzycia przypadkowego slowa klucz - alternatywa - stosunek ...?
            if len(dziecko.get_text().strip().split()) < 4000:
                #handling danych na lokate
                if isLokata and (layout_lokata==-1 or layout_lokata == layout) and word_count_with_locat !=0 and word_count_with_oszczed ==0:
                    layout_lokata = layout
                    lokata_data_end.append(dziecko.get_text().strip())

                #handlind danych oszczednosciowych
                if isOszczednosciowe and (layout_oszczed==-1 or layout_oszczed ==layout) and word_count_with_oszczed !=0 and word_count_with_locat ==0:
                    layout_oszczed = layout
                    oszczed_data_end.append(dziecko.get_text().strip())


                div_list.append({"i":i,
                    "layout":layout,
                    "dziecko":dziecko.get_text().strip(),
                    "len":len(dziecko.get_text().strip().split()),
                    "locat":word_count_with_locat,
                    "oszczed":word_count_with_oszczed,
                    "proc":word_count_with_proc,
                })
            find_last_divs(dziecko,layout,isLokata,isOszczednosciowe,layout_lokata,layout_oszczed)

        else:
            continue
            # print("else") 
            # div_list.append(dziecko)
        

# ----------------------------------------------     WYWOLANIE FUNKCJI ...

#POBRANIE LINKOW
linksLokata,linksOszczed = getLinks()

#ANALIZA DIVOW / MAIN ...
find_last_divs(start_divs,layout,True,True,-1,-1)

#----------------------------------------------- Wizualizacja procesu rekurencji
# for div in div_list:
#     print(div["i"] ," Layout: ", div["layout"]," Len: ",div["len"], " Sum_locat: ",div["locat"]," Sum_oszczęd: ",div["oszczed"], " Procent: ",div["proc"])

#DECYZYCJNOSC ODNOSNIE DANYCH
tableLokata,tableOszczed = analyzisOfTables()
if (lokata_data_end == []):
    print("Nieodpowiedni format lokata...\n\n")
    if(tableLokata):
        lokata_data_end = tableLokata
    else:
        print("Nie znalazłem tabeli lokat ani div...\n\n" )

if (oszczed_data_end == []):
    print("Nieodpowiedni format oszczed...\n\n")
    if(tableOszczed):
        oszczed_data_end = tableOszczed
    else:
        print("Nie znalazłem tabeli oszczed ani div...\n\n" )


if(linksLokata or linksOszczed):
    print("LINKI LOKATA: ",linksLokata,"\n\n\n","LINKI OSZCZEDNOSCIOWE: ",linksOszczed)
if(tableLokata or tableOszczed):
    print("TABELA LOKATA: ",tableLokata,"\n\n\n","TABELA OSZCZEDNOSCIOWE: ",tableOszczed)
if (lokata_data_end or oszczed_data_end):
    print("KONIEC: \n\n","-------LOKATA-------\n\n",lokata_data_end,"\n\n","-------OSZCZĘDNOŚCIOWE-------\n\n",oszczed_data_end)
