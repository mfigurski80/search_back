from flask import Flask, redirect
from flask_cors import CORS
import json
from difflib import get_close_matches



tags_dict = json.load(open("static/tags.json"))
urls_dict = json.load(open("static/urls.json"))

def getNameFromURL(url):
    url = url.split(".surge.sh")[0]
    url = url.replace("http://","").replace("https://","")
    return url

def getURLSFor(terms):
    matchSites = {}
    for term in terms:
        matches = get_close_matches(term, tags_dict.keys(), cutoff=.9)
        # print("\tMatches: " + str(matches))
        for match in matches:
            for site in tags_dict[match]:
                if site in matchSites.keys():
                    matchSites[site] += tags_dict[match][site]
                else:
                    matchSites[site] = tags_dict[match][site]
    returnSites = []
    for site in matchSites:
        returnSites.append((site, matchSites[site]))
    return returnSites

def getResultsFor(urls_list):
    results = []
    for url_tuple in urls_list:
        url = url_tuple[0]
        result_info = urls_dict[url]
        result_info["url"] = url
        result_info["term_density"] = url_tuple[1]
        results.append(result_info)
    return results

def cleanResults(results):
    cleanResults = []
    namesList = [getNameFromURL(result["url"]) for result in results]

    for name in namesList:
        if namesList.count(name) == 1:
            cleanResults.append(results.pop(namesList.index(name)))
            namesList.pop(namesList.index(name))
        else:
            # get all the duplicates into one list
            duplicates = []
            for i in range(namesList.count(name)):
                duplicates.append(results.pop(namesList.index(name)))
                namesList.pop(namesList.index(name))

            # Generate composite site from all duplicates
            try: # some sites havent had their actual base site indexed. Thats a problem
                base_site = urls_dict["http://" + name + ".surge.sh"]
                url = "http://" + name + ".surge.sh"
            except:
                url_length_list = [len(site["url"]) for site in duplicates]
                base_site = duplicates[url_length_list.index(min(url_length_list))]
                url = base_site["url"]
            density_list = [site["term_density"] for site in duplicates]
            best_site = duplicates[density_list.index(max(density_list))]

            best_site = duplicates[0]
            new_site = {
                "url": url,
                "term_density": best_site["term_density"],
                "title": base_site["title"],
                "linked_by": base_site["linked_by"],
                "links_to": best_site["links_to"],
                "size": best_site["size"],
                "blurb": best_site["blurb"]
            }
            cleanResults.append(new_site)

    return cleanResults

def orderResults(searches_dicts):
    rated_searches = []
    for result in searches_dicts:
        # clean the result first (just in case)
        if result["title"] == None:
            result["title"] = result["url"]

        #give result a rating
        rating = .1
        if result["term_density"] < 10: # primary rating factor -- function with term density
            rating = (1-(1/(1+pow(result["term_density"],.5))))*1.31625
        if len(result["links_to"]) > 20: # if its just a page of links
            rating *= .4
        if result["size"] < 150: # if its really small
            rating *= .8
        if result["title"] in [result["url"], "React App", "Document", "None", ""]: # if doesn't have real title
            rating *= .6
        # linked_by_names = [getNameFromURL(url) for url in result["linked_by"]]
        # if linked_by_names.count(getNameFromURL(result["url"])) == len(linked_by_names): # if all the linked_by sites are under same domain
        #     rating *= .9

        rated_searches.append({
            "title": result["title"].replace("'"," ").replace("{","").replace("}","").replace("\"","").replace(">","").replace("<","").replace(";",""),
            "url": result["url"],
            "blurb": result["blurb"].replace("'"," ").replace("{","").replace("}","").replace("\"","").replace(">","").replace("<","").replace(";",""),
            "rating": rating
        })

    #actually order the searches
    ordered_searches = []
    ratings = [search["rating"] for search in rated_searches]
    for _ in range(len(ratings)):
        max_pos = ratings.index(max(ratings))
        ordered_searches.append(rated_searches.pop(max_pos))
        ratings.pop(max_pos)
    return ordered_searches

def boundNum(num):
    return (1 - 1/(1+num))

def fullSearch(term):
    terms = term.lower().split()
    search_urls = getURLSFor(terms)
    search_results = orderResults(cleanResults(getResultsFor(search_urls)))
    # print(search_results)
    return search_results










app = Flask(__name__)
CORS(app)

@app.route("/about")
def output():
    return "<p>This is an app by Mikolaj Figurski</p>"

@app.route("/")
def red():
    return redirect("http://srch.surge.sh")


@app.route("/search/<tag>")
def result(tag):
    results = str(fullSearch(tag.replace(","," "))).replace("\"","").replace(">","").replace("<","").replace(";","")
    return results


if __name__ == "__main__":
    app.run()
