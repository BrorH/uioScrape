from html.parser import HTMLParser
import re, sys, requests, threading, itertools
from urllib import request
import urllib.error
from multiprocessing import Queue
import numpy as np

global ignore_urls, disqualifiers, num_requests, priorities
#todo: add more elegant way of importing these values, through np.loadtxt
with open("ignores.txt", "r") as file:
    ignore_urls = [foo.rstrip() for foo in file.readlines()[1:]]
with open("disqualifiers.txt", "r") as file:
    disqualifiers = [foo.rstrip() for foo in file.readlines()[1:]]
priorities = {}
with open("priorities.txt", "r") as file:
    for line in sorted(file.readlines(), key=len):
        words = line.rstrip().split()
        priorities[words[0]] = int(words[-1])
# list of strings which will automaticall disqualify a pdf from being stored
ignore_pdfs = ["devilry","lecture", "smittevern", "Lecture", "oblig", "week", "Week", "exercise", "Oblig", "ukesoppgave", "Ukesoppgave", "oppgave", "Oppgave"]
max_requests = 1000 # dont make more than 1000 requests to the uio servers
num_requests = 0
def check_url_and_update_storage(scraper,url, parent_url, parent_urls):
    """
    performs several checks on a given url and does one of three things:
     - discards the url if it is not of interest 
     - if url is of interest to dig deeper, it is stored
     - if path points to a pdf, it is stored as a pdf, but not as a potential url to dig deeper in
    in either case, the url is stored to it kan be skipped during future evaluation

    the passed url can be full or relative path
    """
    if url in scraper.visited: return 
    if url.endswith(".pdf"): 
        # storing and categorizing pdfs
        # to add: check if link yields a valid .pdf with 2xx response.
        
        if regex_res := re.search(r"\/(?:\W+\/)*([^\/]+\.pdf)", url):
            pdfname = regex_res.group(0)[1:]
            for ignore in ignore_pdfs:
                if ignore in pdfname: return
            try:
                if (pdfname not in list(scraper.pdfs.keys()) ) or (len(url) > len(scraper.pdfs[pdfname])):
                    scraper.pdfs[pdfname] = relative_to_absolute_url(url, parent_url)
                    ## fill_complete_url should be called before this
            except KeyError: return
        return
    
    url = relative_to_absolute_url(url, parent_url) # make sure url is full path and not relative
    
    if url.find('http') >= 0:
        # storing and categorizing urls
        if url in scraper.visited: return
        if url in ignore_urls: return
        if re.search(r".*\?[^/]+",url): return # any urls with arguments passed after a ? in the url has proven uninteresting so far, so they are ignored
        if not "uio" in url: return
        if "@" in url: return
        if url in parent_urls: return
        for disc in disqualifiers:
            if disc in url: return
        if url not in scraper.urls:
            scraper.urls.append(url)
            return url

def reorder_urls_by_priority(urls, tolerance=10):
    # tolerance is how many percent of the urls are to be returned
    global priorities

    pri_vals = np.zeros(len(urls))
    for i,url in enumerate(urls):
        for pri in priorities.keys():
            if pri in url.lower():
                pri_vals[i] = priorities[pri]
    pri_vals_args = np.argsort(pri_vals)[::-1]
    res = []
    for i,pri in enumerate(pri_vals_args):
        res.append(urls[pri])
    
    return res[:int(len(urls)/tolerance)]




def relative_to_absolute_url(link, parent_url):
    if link.startswith('http'):
        if not parent_url.startswith(link):
            return link
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

    
def read_url(parent_url, scraper, queue):
    global num_requests
    if num_requests <= max_requests:
        try:
            num_requests += 1
            print(num_requests)
            data = request.urlopen(parent_url).read()
        except Exception as e:#urllib.error.HTTPError:
            print("ERROR", parent_url)
            print(e)
            print("\n")
            return
    else:
        print("REACHED MAX NUMBER OF REQUESTS")
        sys.exit(1)
    
   
    data = [parent_url]+extract(data, parent_url)
                

    queue.put(data)



class LinkScrape:
    urls = []
    parent_urls = []
    visited = []
    pdfs = {}
    valid_pdfs = []
    potential_pdfs = []

    max_depth = 1
    subject_subfaculty_dict = {"fys":"fys", "fys-mek":"fys", "in":"ifi", "mat":"math", "mek":"math", "ast":"astro"}
    def __init__(self, subject_code):
        global ignore_urls
        

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
        #ignore_urls = [f'https://www.uio.no/studier/', f'https://www.uio.no/studier/emner/', f'https://www.uio.no/studier/emner/matnat/', 'https://www.uio.no/studier/emner/matnat/','https://www.uio.no/studier/emner/matnat/fys/',f'https://www.uio.no/studier/emner/matnat/fys/{self.subject_code}']
        
    
    def start(self, depth=0,**kwargs):
        self.start_index_scraper()
        self.urls_to_be_checked = self.parent_urls.copy()  # urls_to_be_checked gets dynamically updated
        try:
            for i in range(self.max_depth):
                
                child_urls_ = fetch_parallel(self, self.urls_to_be_checked)#, iteration=i)
                child_urls = [foo[0][1:] for foo in child_urls_]
                #child_urls = list(itertools.chain.from_iterable(child_urls))
                
                if i == 0:
                    parent_urls = [foo[0][0] for foo in child_urls_]
                new_urls_to_be_checked = []
                for childs in child_urls:
                    for url in childs[1:]:
                        if scrape_result:=check_url_and_update_storage(self, url, childs[0], parent_urls):
                            new_urls_to_be_checked.append(scrape_result)
                        
                
                #print("\n\n\n")
                
                #print("\n".join([f"{name}: {link}" for name,link in self.pdfs.items()]))
                self.urls_to_be_checked = reorder_urls_by_priority(new_urls_to_be_checked.copy())
                print("\n".join(self.urls_to_be_checked))
                
                #child_urls = [relative_to_absolute_url(foo) for foo in child_urls]
                #print(child_urls)
                #self.urls_to_be_checked = child_urls.copy()
            # for parent_url in self.parent_urls:
                
            #     #print(f"\nchecking {index_url} ... \n")
            #     try:
            #         self.child_scraping(parent_url)
            #     except error.HTTPError:
            #         pass
            #     #print(f"{j+1}/{len(self.parent_urls)}")
        except KeyboardInterrupt:
            pass

        

    

    def start_index_scraper(self):

        url = f"https://www.uio.no/studier/emner/matnat/{self.subfaculty}/{self.subject_code}/"
        self.url = url
        self.parent_urls.append(url)
        self.visited.append(url)
        #print(url)
        data = request.urlopen(url).read().decode("utf-8")
        raw_parent_urls = extract_course_index(data)
        self.parent_urls = []
        for link in raw_parent_urls:
            if "@" in link: continue
            if link == self.url: continue
            if not link.startswith(self.url): continue
            if link.endswith("/index-eng.html"): continue
            

            if re.search(r".*\?[^/]+",link): continue
            if link.endswith("/index.html"):
                link = link[:-10]
            if link.find('http') >= 0:
                if link not in self.urls:
                    self.parent_urls.append(link)
        

        #print("\n".join(self.parent_urls))
    
    def child_scraping(self, child_urls):
        self.visited += child_urls #append(url)
        result = Queue()
        res = []

        threads = [threading.Thread(target=check_url_and_update_storage, args = (self, url, result)) for url in child_urls]
        for t in threads:
            t.start()
        for t in threads:
            res.append(extract(result.get().decode("latin-1")))
        for t in threads:
            t.join()
        return res



HTML_MAIN_BODY_REGEX = r"(?s)<div id=\"main\" role=\"main\">(.*)<div id=\"bottomnav\" role=\"navigation\">"
HTML_MAIN_LEFT_BODY_REGEX = re.compile(r"(?s)<a class=\"vrtx-marked\"[^>]*>(?:(?!</a>).)*</a>\s*<ul>\s*(.*?)\s*</ul>", re.IGNORECASE)
HTML_MAIN_LEFT_BODY_REGEX = re.compile(r"(?s)(<li class=\"vrtx-child\"><a class=\"vrtx-marked\"(?:.*?)</li>)", re.IGNORECASE)
course_left_menu_regex = re.compile(r"<a href=\"([^\"^#^@^\?]*)\"[^>]*>")
course_main_body_regex = re.compile(r"(?s)<!--startindex-->(.*)<!--stopindex-->", re.IGNORECASE)
course_messages_regex = re.compile(r"(?s)(<div class=\"vrtx-messages-header\">(?:.*?)</div>)(.*?)(<div class=\"vrtx-messages\">(?:.*?)</div>)", re.IGNORECASE)
course_index_semester_list_regex = re.compile(r"(?s)(<div class=\"vrtx-frontpage-box grey-box\" id=\"vrtx-course-semesters\">(?:.*?)</div>)", re.IGNORECASE)

#HTML_TAG_REGEX = re.compile(r'<ahref=\"([^\"^#^@^\?]*)\"[^>]*>([^<]*)<\/a>', re.IGNORECASE)
extract_href_regex = re.compile(r'(?s)href=\"([^\"^#^@^\?\~]*)\"[^>]*>(?:.*?)</a>', re.IGNORECASE)

def extract_course_index(content):
    if isinstance(content, tuple):
        content = content[0]
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    course_semesters_list = course_index_semester_list_regex.findall(content)[0]
    course_semesters_urls = extract_href_regex.findall(course_semesters_list)
    course_semesters_urls = [foo.rstrip("index.html") for foo in course_semesters_urls]
    return course_semesters_urls
    


def purge_unwanted_urls(urls):
    accepted = []
    for url in urls:
        #print(url.lstrip("https://www.").rstrip("/") in ignore_urls, url.lstrip("https://www.").rstrip("/"))
        
        #url = url.replace("http:", "https:")
        if not url.lstrip("https://www.").rstrip("/") in ignore_urls:
            
            accepted.append(url)
        
    return accepted


def extract(content, parent_url):
    if isinstance(content, tuple):
        content = content[0]
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    urls = extract_href_regex.findall(content)
    urls = purge_unwanted_urls(urls)
    for i,url in enumerate(urls):
        if not url.lstrip().startswith("http"):
            urls[i] = merge(parent_url, url)
    urls_ = []
    for url in urls:
        if "uio" in url and url not in urls_:
            urls_.append(url)
 
    return urls_

    


def merge(master, rel):
    # merges a relative url with the parent, creating an absolute path
    rel= rel.lstrip("/")
    if master == "":
        return rel
    if master.startswith("http"):
        master = master.lstrip("https://").rstrip("/")


    if rel.startswith("http"):
        rel = rel.lstrip("https://")
    master = master.split("/")
    rel = rel.split("/")
    for idx,sub in enumerate(master):
        if sub == rel[0]:
            return "https://"+"/".join(master[:idx] + rel )
    return "https://"+"/".join(master + rel )
   




def fetch_parallel(scraper, urls_to_load):
    result = Queue()
    res = []


    threads = [threading.Thread(target=read_url, args = (url, scraper, result)) for url in urls_to_load]
    for t in threads:
        t.start()
    for t in threads:
        res.append([result.get()])
    for t in threads:
        t.join()
    return res

if __name__ == '__main__':
    scraper = LinkScrape(sys.argv[1])
    scraper.start()

    print()
    print("===RESULTS===")
    print("\n".join([f"{name}: {link}" for name,link in scraper.pdfs.items()]))

