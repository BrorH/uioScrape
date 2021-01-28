import eventlet
eventlet.monkey_patch()
from html.parser import HTMLParser
import urllib.request
import re,sys, requests



ignore_pdfs = ["lecture", "smittevern", "Lecture", "oblig", "week", "Week", "exercise", "Oblig", "ukesoppgave", "Ukesoppgave", "oppgave", "Oppgave"]


class LinkScrape:
    urls = []
    parent_urls = []
    visited = []
    pdfs = {}
    valid_pdfs = []
    potential_pdfs = []
    subject_subfaculty_dict = {"fys":"fys", "fys-mek":"fys", "in":"ifi", "mat":"math", "mek":"math", "ast":"astro"}
    def __init__(self, subject_code):
        

        self.base_url = "https://www.uio.no/studier/emner/matnat/"
        self.subject_code = subject_code.upper()
        subject_regex = re.search(r"([a-zA-Z\-]+)(\d+)", self.subject_code)
        if subject_regex:
            self.subject_type = subject_regex.group(1)
            self.subject_uuid = subject_regex.group(2)
        else:
            print(f"Error, subject code '{subject_code}' is note valid")
            sys.exit(1)
        try:
            self.subfaculty = self.subject_subfaculty_dict[self.subject_type.lower()]
        except KeyError:
            print(f"Subject '{subject_code}' of type '{self.subject_type}' not yet supported")
            sys.exit(1)
        
    
    def start(self, **kwargs):
        self.start_index_scraper()
        try:
            for i,parent_url in enumerate(self.parent_urls):
                
                #print(f"\nchecking {index_url} ... \n")
                try:
                    self.child_scraping(parent_url)
                except urllib.error.HTTPError:
                    pass
                print(f"{i+1}/{len(self.parent_urls)}")
        except KeyboardInterrupt:
            pass

        

    

    def start_index_scraper(self):

        url = f"https://www.uio.no/studier/emner/matnat/{self.subfaculty}/{self.subject_code}/"
        self.url = url
        self.parent_urls.append(url)
        self.visited.append(url)
        request_object = urllib.request.Request(url)
        page_object = urllib.request.urlopen(request_object)
        link_parser = LinkScrapeStartIndex()
        link_parser.parentScrape = self
        link_parser.feed(page_object.read().decode("latin-1"))
        
        self.parent_urls = link_parser.urls[:]
    
    def child_scraping(self, url, depth=0):
        
        self.visited.append(url) 

        request_object = urllib.request.Request(url)
        page_object = urllib.request.urlopen(request_object)
        link_parser = LinkScrapeChild()
        link_parser.parentScrape = self 
        link_parser.parent_url = url
        link_parser.pdfs = self.pdfs 
        link_parser.feed(page_object.read().decode("latin-1"))

        if depth <= 1: 
            for url__ in link_parser.urls:
                self.child_scraping(url__, depth + 1)
        return link_parser.urls

class LinkScrapeStartIndex(HTMLParser):
    urls = []
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    link = attr[1]
                    if "@" in link: continue
                    if link == self.parentScrape.url: continue
                    if not link.startswith(self.parentScrape.url): continue
                    if link.endswith("/index-eng.html"): continue
                    

                    if re.search(r".*\?[^/]+",link): continue
                    if link.endswith("/index.html"):
                        link = link[:-10]
                    if link.find('http') >= 0:
                        if link not in self.urls:
                            self.urls.append(link)
        


class LinkScrapeChild(HTMLParser):
    urls = []

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
                                if (pdfname not in list(self.pdfs.keys()) ) or (len(link) > len(self.pdfs[pdfname])):
                                    self.pdfs[pdfname] = fill_incomplete_url(link, self.parent_url)
                                    name = pdfname.lower()
                                    try:
                                        if "ex" in name or "exam" in name or "eksamen" in name or "eks" in name:
                                            timeout = 10
                                        else:
                                            timeout = 1
                                        with eventlet.Timeout(timeout):
                                            if requests.get(self.pdfs[pdfname]).status_code == 200:
                                                print(pdfname, self.pdfs[pdfname])
                                                self.parentScrape.valid_pdfs.append(self.pdfs[pdfname])
                                    except eventlet.timeout.Timeout:
                                        self.parentScrape.potential_pdfs.append(self.pdfs[pdfname])
                                        print("Timed out:", pdfname, self.pdfs[pdfname])

                            except KeyError:
                                continue
                        continue
                    
                    
                    
                    if link.find('http') >= 0:
                        if re.search(r".*\?[^/]+",link): continue
                        if not self.parent_url in link: continue
                        if link in self.parentScrape.visited: continue
                        if "@" in link: continue
                        if link in self.parentScrape.parent_urls: continue
                        if link == self.parentScrape.url: continue
                        if link not in self.urls:
                            self.urls.append(link)




def fill_incomplete_url(link, parent_url):
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
    

if __name__ == '__main__':
    scraper = LinkScrape(sys.argv[1])
    scraper.start()

    print()
    print("===RESULTS===")
    print("\n".join(scraper.valid_pdfs))

    print()
    print("===POTENTIAL PDFS (TIMED OUT)===")
    print("\n".join(scraper.potential_pdfs))
