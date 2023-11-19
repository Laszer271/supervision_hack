import requests
from bs4 import BeautifulSoup


def proces_links(links, base_url, only_pdfs=False):
    new_links = []
    for link in links:
        link = dict(link) # to copy by value

        if only_pdfs and not link['href'].endswith('.pdf'):
            continue

        if not link['href'].startswith('http'):
            if not link['href'].startswith('/'):
                link['href'] = '/' + link['href']
            link['href'] = base_url + link['href']

        new_links.append(link)
    return new_links


class HTMLBankParser():

    def __init__(self, url):
        self.url = url
        self.initialize_soup()
        self.start_divs = self.soup.find("body")
        self.div_list = []
        self.lokata_data_end = []
        self.oszczed_data_end = []
        # self.links_lokata=[]
        # self.links_oszczed=[]
        # self.layout = -1

    def initialize_soup(self):
        response = requests.get(self.url, )
        response.encoding = 'utf-8'
        self.soup = BeautifulSoup(response.text, 'lxml')


    def analyzisOfTables(self):
        table_words_lokata = []
        table_words_oszczed = []
        tbody_elements = self.soup.find_all('table')
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

        return table_words_lokata, table_words_oszczed
    # ----------------------------------------------        



    # ----------------------------------------------HANDLOWANIE LINKOW
    def getLinks(self):
        links = self.soup.find_all("a", href=True)
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
        return links_lokata, links_oszczed

    # ----------------------------------------------        


    # ----------------------------------------------HANDLOWANIE DIVOW / MAIN / SECTION
    def find_last_divs(self, divs, layout, isLokata, isOszczednosciowe, layout_lokata, layout_oszczed):
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
                        self.lokata_data_end.append(dziecko.get_text().strip())

                    #handlind danych oszczednosciowych
                    if isOszczednosciowe and (layout_oszczed==-1 or layout_oszczed ==layout) and word_count_with_oszczed !=0 and word_count_with_locat ==0:
                        layout_oszczed = layout
                        self.oszczed_data_end.append(dziecko.get_text().strip())


                    self.div_list.append({"i":i,
                        "layout":layout,
                        "dziecko":dziecko.get_text().strip(),
                        "len":len(dziecko.get_text().strip().split()),
                        "locat":word_count_with_locat,
                        "oszczed":word_count_with_oszczed,
                        "proc":word_count_with_proc,
                    })
                self.find_last_divs(dziecko,layout,isLokata,isOszczednosciowe,layout_lokata,layout_oszczed)

            else:
                continue
                # print("else") 
                # div_list.append(dziecko)
            
    def get_outputs(self):
        #POBRANIE LINKOW
        linksLokata, linksOszczed = self.getLinks()

        #ANALIZA DIVOW / MAIN ...
        layout = -1
        self.find_last_divs(self.start_divs, layout, True,True,-1,-1)


        #DECYZYCJNOSC ODNOSNIE DANYCH
        tableLokata, tableOszczed = self.analyzisOfTables()
        if (self.lokata_data_end == []):
            print("Nieodpowiedni format lokata...\n\n")
            if(tableLokata):
                self.lokata_data_end = tableLokata
            else:
                print("Nie znalazłem tabeli lokat ani div...\n\n" )

        if (self.oszczed_data_end == []):
            print("Nieodpowiedni format oszczed...\n\n")
            if(tableOszczed):
                self.oszczed_data_end = tableOszczed
            else:
                print("Nie znalazłem tabeli oszczed ani div...\n\n" )


        # if(linksLokata or linksOszczed):
            # print("LINKI LOKATA: ", linksLokata,"\n\n\n","LINKI OSZCZEDNOSCIOWE: ",linksOszczed)
        # if(tableLokata or tableOszczed):
        #     print("TABELA LOKATA: ",tableLokata,"\n\n\n","TABELA OSZCZEDNOSCIOWE: ",tableOszczed)
        # if (self.lokata_data_end or self.oszczed_data_end):
        #     print("KONIEC: \n\n","-------LOKATA-------\n\n", self.lokata_data_end,"\n\n","-------OSZCZĘDNOŚCIOWE-------\n\n", self.oszczed_data_end)

        return self.lokata_data_end, self.oszczed_data_end, tableLokata, tableOszczed, linksLokata, linksOszczed

# ----------------------------------------------     WYWOLANIE FUNKCJI ...
if __name__ == '__main__':
    url = "https://www.credit-agricole.pl/oprocentowanie"
    parser = HTMLBankParser(url)
    output = parser.get_outputs()
    # print(output)