from html.parser import HTMLParser
import http.client
import re, sys, requests, threading, itertools, time, argparse
from urllib import request
import urllib.error
from multiprocessing import Queue
import numpy as np
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo

semester_exam_index_remover_regex = re.compile(r"(?s)(?:.*?)/[vh]\d{2}/eksamen/", re.IGNORECASE)

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
num_requests = 0

class LinkScrape:
    urls = []
    parent_urls = []
    visited = []
    pdfs = {}
    valid_pdfs = []
    potential_pdfs = []

    subject_subfaculty_dict = {"fys":"fys", "fys-mek":"fys", "in":"ifi", "mat":"math", "mek":"math", "ast":"astro", "kjm":"kjemi", "bios":"ibv", "bios-in":"ibv", "farm":"farmasi", "fys-stk":"fys", "mat-inf":"math"}
    def __init__(self, subject, max_depth, max_requests):
        self.max_depth = max_depth
        self.max_requests = max_requests
        

        self.base_url = "https://www.uio.no/studier/emner/matnat/"
        self.subject_code = subject.upper()
        subject_regex = re.search(r"([a-zA-Z\-]+)(\d+)", self.subject_code)
        if subject_regex:
            self.subject_type = subject_regex.group(1)
            self.subject_uuid = subject_regex.group(2)
        else:
            print(f"Error, subject code '{subject}' is note valid")
            sys.exit(1)
        try:
            self.subfaculty = self.subject_subfaculty_dict[self.subject_type.lower()]
        except KeyError:
            print(f"Subject '{subject}' of type '{self.subject_type}' not yet supported")
            sys.exit(1)
        
    
    def start(self, depth=0,**kwargs):
        print(f"Starting scrape of {self.subject_code   } of max depth {self.max_depth} and max requests {self.max_requests}")
        self.start_index_scraper()

        self.urls_to_be_checked = self.parent_urls.copy()  
        #print(self.urls_to_be_checked)
        #sys.exit()
        try:
            for i in range(self.max_depth):
                
                child_urls_ = fetch_parallel(self.urls_to_be_checked)#, iteration=i)
                child_urls = [foo[0][1:] for foo in child_urls_] # the semester page itself is always the first found url. Remove this
                #child_urls = list(itertools.chain.from_iterable(child_urls_)) # join into one list
                #print(child_urls)
                
                if i == 0:
                    parent_urls = [foo[0][0] for foo in child_urls_.copy()]
                new_urls_to_be_checked = []
                for childs,parent_url in zip(child_urls, parent_urls):
                    for url in childs:
                        if scrape_result:=self.check_url_and_update_storage(url, parent_url, parent_urls):
                            new_urls_to_be_checked.append(scrape_result)
                        
                
                #print(new_urls_to_be_checked)
                #sys.exit()
                self.urls_to_be_checked = reorder_urls_by_priority(new_urls_to_be_checked.copy())
        except KeyboardInterrupt:
            pass

        

    

    def start_index_scraper(self):

        url = f"https://www.uio.no/studier/emner/matnat/{self.subfaculty}/{self.subject_code}/"
        self.url = url
        self.parent_urls.append(url)
        self.visited.append(url)
        data = request.urlopen(url).read().decode("latin-1")
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
    

        


    def check_url_and_update_storage(self, url, parent_url, parent_urls):
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
                    if (pdfname not in list(self.pdfs.keys()) ) or (len(url) > len(self.pdfs[pdfname])):
                        self.pdfs[pdfname] = relative_to_absolute_url(url, parent_url)
                        ## fill_complete_url should be called before this
                except KeyError: return
            return
        
        url = relative_to_absolute_url(url, parent_url) # make sure url is full path and not relative
        if url.endswith(".tex"): return # ignore .tex files for now
        if url.find('http') >= 0:
            # storing and categorizing urls
            if url in self.visited: return
            if url in ignore_urls: return
            if re.search(r".*\?[^/]+",url): return # any urls with arguments passed after a ? in the url has proven uninteresting so far, so they are ignored
            if not "uio" in url: return
            if "@" in url: return
            if url in parent_urls: return
            if semester_exam_index_remover_regex.match(url): return
            if ".." in url: return
            if self.subject_type not in url: return
            for disc in disqualifiers:
                if disc in url: return
            if url not in self.urls:
                self.urls.append(url)
                return url

def reorder_urls_by_priority(urls, tolerance=80):
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
    
    return res[:int(len(urls)*tolerance/100)]




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
global REACHED_MAX_ALERED
REACHED_MAX_ALERED = False
#@on_exception(expo, RateLimitException, max_tries=8)
#@limits(calls=10, period=2)
def read_url(parent_url, queue):
    global num_requests, REACHED_MAX_ALERED
    if num_requests < max_requests:
        num_requests += 1
        #print(num_requests)
        try:
            data = request.urlopen(parent_url).read()
            sys.stdout.write("Requests completed: %i/%i \r" %(num_requests, max_requests))
            sys.stdout.flush()
        except urllib.error.HTTPError:
            print(f"Timed out: {parent_url}")
            queue.put([])
            return
        except http.client.InvalidURL:
            print(f"ERROR: Invalid url: {parent_url}")
            queue.put([])
            return
    else:
        if not REACHED_MAX_ALERED:
            print("\nCompiling results, please wait... (alternatively press ctrl+C to get semi-compiled results)")
            REACHED_MAX_ALERED = not REACHED_MAX_ALERED
        queue.put([])
        return
    
   
    data = [parent_url]+extract(data, parent_url)
                

    time.sleep(1)
    queue.put(data)






#HTML_MAIN_BODY_REGEX = r"(?s)<div id=\"main\" role=\"main\">(.*)<div id=\"bottomnav\" role=\"navigation\">"
#HTML_MAIN_LEFT_BODY_REGEX = re.compile(r"(?s)<a class=\"vrtx-marked\"[^>]*>(?:(?!</a>).)*</a>\s*<ul>\s*(.*?)\s*</ul>", re.IGNORECASE)
HTML_MAIN_LEFT_BODY_REGEX = re.compile(r"(?s)(<li class=\"vrtx-child\"><a class=\"vrtx-marked\"(?:.*?)</li>)", re.IGNORECASE)
course_index_left_menu_regex = re.compile(r"(?s)<a class=\"vrtx-marked\"(?:.*?)</a>(?:.*?)<ul>(.*?)</ul>", re.IGNORECASE)
course_left_menu_regex = re.compile(r"<a href=\"([^\"^#^@^\?]*)\"[^>]*>")
course_main_body_regex = re.compile(r"(?s)<!--startindex-->(.*)<!--stopindex-->", re.IGNORECASE)
course_messages_regex = re.compile(r"(?s)(<div class=\"vrtx-messages-header\">(?:.*?)</div>)(.*?)(<div class=\"vrtx-messages\">(?:.*?)</div>)", re.IGNORECASE)
course_index_semester_list_regex = re.compile(r"(?s)(<div class=\"vrtx-frontpage-box grey-box\" id=\"vrtx-course-semesters\">(?:.*?)</div>)", re.IGNORECASE)

extract_href_regex = re.compile(r'(?s)href=\"([^\"^#^@^\?\~]*)\"[^>]*>(?:.*?)</a>', re.IGNORECASE)

def extract_course_index(content):
    if isinstance(content, tuple):
        content = content[0]
    if isinstance(content, bytes):
        content = content.decode("latin-1")
    course_semesters_list = course_index_semester_list_regex.findall(content)[0]
    course_semesters_urls = extract_href_regex.findall(course_semesters_list)
    course_semesters_urls = [foo.rstrip("index.html") for foo in course_semesters_urls]

    #extract content from left menu. try/except because will fail if nothing is in left menu otherwise
    try:
        course_left_menu = course_index_left_menu_regex.findall(content)
        course_left_menu_urls = extract_href_regex.findall(course_left_menu[0])
        course_left_menu_urls = [foo.rstrip("index.html") for foo in course_left_menu_urls]
        #print(course_left_menu_urls)
        return course_semesters_urls + course_left_menu_urls
    except:
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
        content = content.decode("latin-1")
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
    res = "https://"+"/".join(master + rel )
    if " " in res:
        res = res[res.index(" "):]
    return res
   




def fetch_parallel(urls_to_load):
    result = Queue()
    res = []

   
    
    threads = [threading.Thread(target=read_url, args = (url, result)) for url in urls_to_load]
    for t in threads:
        t.start()
        time.sleep(0.2)
    for t in threads:
        res.append([result.get()])
    for t in threads:
        t.join()
    return res


parser = argparse.ArgumentParser(description='Scrape all semester pages of a UiO subject in order to get the urls of pdfs of old exams and their solutions.\n Made by Bror Hjemgaard, 2021')
parser.add_argument('SUBJECT', metavar='SUBJECT', nargs=1,
                    help='Subject code of a matnat subject. Case insensitive')
parser.add_argument('-d', dest='depth', metavar="depth", default=2,
                    help='How many layers deep the scraping should go. This caues the number of requests to grow exponentially. Default: 2')
parser.add_argument("-r", dest="requests",  metavar="requests", default=50, help="max. number of requests to make. Increase at own risk. Default: 50")




if __name__ == '__main__':
    args = parser.parse_args()
    max_requests = int(args.requests)
    max_depth = int(args.depth)
    subject = args.SUBJECT[0]
    start = time.time()
    #sys.exit()
    scraper = LinkScrape(subject = subject, max_depth=max_depth, max_requests = max_requests)
    scraper.start()
    end = time.time()
    print()
    print(f"Found {len(scraper.pdfs.keys())} items in {round(end-start,2)}s after {num_requests} requests")
    print("===RESULTS===")
    print("\n".join([f"{name}: {link}" for name,link in scraper.pdfs.items()]))
    #print("\n".join([f"{name}: ../\u001b]8;;{link}\u001b\\{link.lstrip('https://www.uio.no/studier/emner/matnat/fys/'+scraper.subject_code)}\u001b]8;;\u001b\\" for name,link in scraper.pdfs.items()]))

