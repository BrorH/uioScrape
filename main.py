import eventlet
eventlet.monkey_patch()
from html.parser import HTMLParser
import urllib.request
import re,sys, requests

global url, visited, parent_url, rec, subject_type, subject_uuid
visited = []
pdfs = {}
pdfnames = []
valid_pdfs = []
potential_pdfs = []
rec = 0

ignore_pdfs = ["lecture", "smittevern", "Lecture", "oblig", "week", "Week", "exercise", "Oblig", "ukesoppgave", "Ukesoppgave", "oppgave", "Oppgave"]

class LinkScrapeIndex(HTMLParser):

    def handle_starttag(self, tag, attrs):
        #print(tag, attrs)
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    link = attr[1]
                    if "@" in link: continue
                    if link == url: continue
                    if not link.startswith(url): continue
                    if link.endswith("/index-eng.html"): continue
                    

                    if re.search(r".*\?[^/]+",link): continue
                    if link.endswith("/index.html"):
                        link = link[:-10]
                    if link.find('http') >= 0:
                        if link not in self.urls:
                            self.urls.append(link)

class LinkScrapeChild(HTMLParser):

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    link = attr[1]
                    ignored = False
                    if link.endswith(".pdf"):

                        
                        if regex_res := re.search(r"\/(?:\W+\/)*([^\/]+\.pdf)", link):
                            pdfname = regex_res.group(0)[1:]
                            for ignore in ignore_pdfs:
                                if ignore in pdfname: 
                                    ignored = True
                                    break 
                            if ignored: continue
                            try:
                                if (pdfname not in list(pdfs.keys()) ) or (len(link) > len(pdfs[pdfname])):
                                    pdfs[pdfname] = fill_incomplete_url(link)
                                    name = pdfname.lower()
                                    #print(fill_incomplete_url(link), "aaa")
                                    try:
                                        if "ex" in name or "exam" in name or "eksamen" in name or "eks" in name:
                                            timeout = 10
                                        else:
                                            timeout = 1
                                        with eventlet.Timeout(timeout):
                                            if requests.get(pdfs[pdfname]).status_code == 200:
                                                print(pdfname, pdfs[pdfname])
                                                valid_pdfs.append(pdfs[pdfname])
                                    except eventlet.timeout.Timeout:
                                        potential_pdfs.append(pdfs[pdfname])
                                        print("Timed out:", pdfname, pdfs[pdfname])

                            except KeyError:
                                continue
                        continue
                    
                    
                    
                    if link.find('http') >= 0:
                        if re.search(r".*\?[^/]+",link): continue
                        if not parent_url in link: continue
                        if link in visited: continue
                        if "@" in link: continue
                        if link == parent_url: continue
                        if link == url: continue
                        if link not in self.urls:
                            self.urls.append(link)


def fill_incomplete_url(link):
    if link.startswith('http'):
        return link
    # add check for correct top level domain
    
    if link.startswith("/"):
        link = link[1:]
    
    if link.startswith("studier/"):
        return "https://www.uio.no/" + link
    else:
        if parent_url.endswith("/"):
            return parent_url+link
        else:
            return parent_url +"/" + link
    


def start_index_scraper():
    global url, subject_code, parent_url, visited, subfaculty, subject_type
    #subject_code = subject.upper()

    url = f"https://www.uio.no/studier/emner/matnat/{subfaculty}/{subject_code}/"
    parent_url = url
    visited.append(url)
    request_object = urllib.request.Request(url)
    page_object = urllib.request.urlopen(request_object)
    link_parser = LinkScrapeIndex()
    link_parser.urls = []
    link_parser.feed(page_object.read().decode("latin-1"))

    return link_parser.urls 

def child_scraping(url_, depth = 0):
    global url,visited, rec
    url = url_
    visited.append(url) 

    request_object = urllib.request.Request(url)
    page_object = urllib.request.urlopen(request_object)
    link_parser = LinkScrapeChild()
    link_parser.urls = []
    link_parser.feed(page_object.read().decode("latin-1"))
   
    if depth <= 1:
        for url__ in link_parser.urls:
            rec += 1
            child_scraping(url__, depth + 1)
    return link_parser.urls


deep = 3

def initializer(subject):
    global subject_type, subject_uuid, subject_code, subfaculty
    # extracts subject code, subject type (mat, fys etc) and does other initializing

    subject_subfaculty_dict = {"fys":"fys", "fys-mek":"fys", "in":"ifi", "mat":"math", "mek":"math", "ast":"astro"}

    subject_code = subject.upper()
    subject_regex = re.search(r"([a-zA-Z\-]+)(\d+)", subject)
    if subject_regex:
        subject_type = subject_regex.group(1)
        subject_uuid = subject_regex.group(2)
    else:
        print(f"Error, subject code '{subject}' is note valid")
        sys.exit(1)
    try:
        subfaculty = subject_subfaculty_dict[subject_type]
    except KeyError:
        print(f"Subject '{subject_code}' of type '{subject_type}' not yet supported")
        sys.exit(1)
    
        


if __name__ == '__main__':
    try:
        initializer(sys.argv[1])
        index_urls = start_index_scraper()
        print(f"Found {len(index_urls)} links of interest on main semester page")

        for i,index_url in enumerate(index_urls):
            
            #print(f"\nchecking {index_url} ... \n")
            parent_url = index_url
            try:
                child_urls = child_scraping(index_url)
            except urllib.error.HTTPError:
                pass
            print(f"{round(((i+1)*100)//len(index_urls))}%")
    except KeyboardInterrupt:
        pass
    print()
    print("===RESULTS===")
    print("\n".join(valid_pdfs))

    print()
    print("===POTENTIAL PDFS (TIMED OUT)===")
    print("\n".join(potential_pdfs))
