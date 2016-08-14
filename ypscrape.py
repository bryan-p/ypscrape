import os, requests, bs4, re, csv, datetime

fqdn = "http://www.yellowpages.com"
filename = ""
category = ""
zipcode = ""
companies = {}

def get_company_info(results):
    global companies
    for element in results:
        name = ""
        phone = ""
        street = ""
        city = ""
        state = ""
        zip = ""

        result = element.find('div', class_='info')

        name = result.find('a', class_='business-name').get_text().encode('utf-8')
        phoneDiv = result.find('div', class_='phones')
        if (phoneDiv is not None):
            phone = phoneDiv.get_text()

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
                city = city[:-2]
            if(span3 is not None):
                state = span3.get_text()
            if(span4 is not None):
                zip = span4.get_text()

        if (zip == zipcode):
            companies[name] = {}
            companies[name]['phone'] = phone.encode('utf-8')
            companies[name]['street'] = street.encode('utf-8')
            companies[name]['city'] = city.encode('utf-8')
            companies[name]['state'] = state.encode('utf-8')
            companies[name]['zip'] = zip.encode('utf-8')

def get_input():
    global category     
    global zipcode

    category = raw_input("Search Term: ").strip()
    zipcode = raw_input("Zip Code: ").strip()
    urlquery = "/search?search_terms=" + category + "&geo_location_terms=" + zipcode 

    print("Scraping data for '{}' in zip code '{}'...").format(category, zipcode)

    return urlquery

def save():
    global filename 
    filename = category + "_" + zipcode + " " + datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S" + ".csv")
    with open(filename, "w") as toWrite:
        writer = csv.writer(toWrite, delimiter=",")
        writer.writerow(["name", "phone", "street", "city", "state", "zip"])
        for key in companies.keys():
            writer.writerow([key, companies[key].get("phone", ""), companies[key].get("street"), companies[key].get("city", ""), companies[key].get("state", ""), companies[key].get("zip", "")])

query = get_input()

while True:
    response = requests.get(fqdn+query)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    
    nextPage = soup.find('a', class_='next')
    search_results = soup.find_all('div', id=re.compile('lid-*'))
    get_company_info(search_results)

    if(nextPage is None):
       print("No more pages")
       break
    else:
       print("searching next page: " + nextPage.get('href'))
       query = nextPage.get("href") 
         
print("Saving data to file: {} in folder: {}").format(filename, os.getcwd())
save()
