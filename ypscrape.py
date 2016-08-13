import os, requests, bs4, re, csv, datetime

fqdn = "http://www.yellowpages.com"
category = ""
zipcode = ""


def get_company_info(results):
    companies = {}
    index = 0
    for element in results:
        index += 1
        result = element.find('div', class_='info')

        name = result.find('a', class_='business-name').get_text().encode('utf-8')
        phone = result.find('div', class_='phones').get_text()

        companies[name] = {}
        companies[name]['phone'] = phone.encode('utf-8')

        street = ""
        city = ""
        state = ""
        zip = ""
        addr = result.find_all('p', class_='adr')
        for tag in addr:
            if (tag.span is None):
                street = tag.get_text().encode('utf-8')
            else:
                span1 = tag.find('span', {'class' : 'street-address'})
                if(span1 is not None):
                    street = span1.get_text().encode('utf-8')

            span2 = tag.find('span', {'class' : 'locality'})
            span3 = tag.find('span', {'itemprop' : 'addressRegion'})
            span4 = tag.find('span', {'itemprop' : 'postalCode'})
        
            if(span2 is not None):
                city = span2.get_text()
            if(span3 is not None):
                state = span3.get_text()
            if(span4 is not None):
                zip = span4.get_text()

            companies[name]['street'] = street.encode('utf-8')
            companies[name]['city'] = city.encode('utf-8')
            companies[name]['state'] = state.encode('utf-8')
            companies[name]['zip'] = zip.encode('utf-8')

    return companies

def get_input():
    global category     
    global zipcode

    category = raw_input("Search Term: ").strip()
    zipcode = raw_input("Zip Code: ").strip()
    urlquery = "/search?search_terms=" + category + "&geo_location_terms=" + zipcode 

    print("Scraping data for '{}' in zip code '{}'...").format(category, zipcode)

    return urlquery

def save_csv(companies):
    with open(category + "_" + zipcode + " " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M%s"), "w") as toWrite:
        writer = csv.writer(toWrite, delimiter=",")
        writer.writerow(["name", "phone", "street", "city", "state", "zip"])
        for key in companies.keys():
            writer.writerow([key, companies[key]["phone"], companies[key]["street"], companies[key]["city"], companies[key]["state"], companies[key]["zip"]])


query = get_input()
response = requests.get(fqdn+query)
soup = bs4.BeautifulSoup(response.text, 'html.parser')
search_results = soup.find_all('div', id=re.compile('lid-*'))

companies = get_company_info(search_results)
save_csv(companies)
