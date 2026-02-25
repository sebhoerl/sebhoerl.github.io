import json

def format_name(author):
    given = author["given"].split(" ")
    given = ["{}.".format(item[0]) for item in given]
    result = "{}, {}".format(author["family"], "".join(given))

    if result.startswith("Hörl"):
        return "**{}**".format(result)
    else:
        return result
    
def format_source(entry):
    content = []
    content.append("*{}*".format(entry["container-title"]))

    if "volume" in entry:
        volume = str(entry["volume"])

        if "issue" in entry:
            volume = "{} ({})".format(volume, entry["issue"])
        
        content.append(volume)

    if "page" in entry:
        content.append(entry["page"])

    return ", ".join(content)

def format_month(month):
    if isinstance(month, int):
        return ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][month - 1]
    else:
        return month.capitalize()
    
def format_event(entry):
    if entry["event-title"] == entry["container-title"]:
        date = str(entry["issued"]["date-parts"][0][0])

        if len(entry["issued"]["date-parts"][0]) > 1:
            date = "{} {}".format(format_month(entry["issued"]["date-parts"][0][1]), date)
        
        return "{}, {}, {}".format(entry["event-title"], date, entry["publisher-place"])

    else:
        return "{}".format(entry["event-title"])

def format_sort_key(entry):
    return entry["title"]

def prepare(path, annual = False):
    with open(path) as f:
        data = json.load(f)

    years = sorted(set([str(entry["issued"]["date-parts"][0][0]) for entry in data]), reverse = True)

    entries = []
    for year in years:
        if annual:
            entries.append("### {}".format(year))

        year_entries = []

        for entry in (e for e in data if str(e["issued"]["date-parts"][0][0]) == year):
            content = [
                ", ".join(map(format_name, entry["author"])),
                " ({}).".format(entry["issued"]["date-parts"][0][0]),
                " {}.".format(entry["title"]),
            ]

            if "container-title" in entry:
                if not ("event-title" in entry and entry["event-title"] == entry["container-title"]):
                    content.append(" {}.".format(format_source(entry)))

            if "event-title" in entry:
                content.append(" {}.".format(format_event(entry)))

            if "DOI" in entry:
                doi = entry["DOI"].split("doi.org/")[-1]
                content.append(" [doi](https://doi.org/{})".format(doi))

            elif "URL" in entry:
                if "hal" in entry["URL"]:
                    content.append(" [hal]({})".format(entry["URL"]))
                else:
                    content.append(" [link]({})".format(entry["URL"]))

            content = "".join(content)
            year_entries.append((content, format_sort_key(entry)))

        year_entries = sorted(year_entries, key = lambda e: e[1], reverse = True)
        year_entries = [e[0] for e in year_entries]
        year_entries = ["- {}\n".format(entry) for entry in year_entries]
        entries += year_entries

    return entries

with open("publications.md", "w+") as f:
    content = []
    content.append("# Publications")
    content.append("\n<span class=\"publications\">\n")
    content.append("## Journal articles")
    content += prepare("_publications/International journals with peer review.json")
    content.append("## International conferences with peer review")
    content += prepare("_publications/International conferences with peer review.json", annual = True)
    content.append("## International conferences without peer review")
    content += prepare("_publications/International conferences without peer review.json")
    content.append("## National conferences with peer review")
    content += prepare("_publications/National conference with peer review.json")
    content.append("## Monographs and book contributions")
    content += prepare("_publications/Monographs and book contributions.json")
    content.append("## Reports, professional magazines, and data papers")
    content += prepare("_publications/Reports, professional magazines, and data papers.json")
    content.append("\n</span>\n")

    f.write("\n".join(content))