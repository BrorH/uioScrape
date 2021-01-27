from html.parser import HTMLParser
import urllib.request
import re,sys

global url, visited
visited = []

pdfs = {}
pdfnames = []
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
                    if link.endswith(".pdf"):
                        
                        if regex_res := re.search(r"\/(?:\W+\/)*([^\/]+\.pdf)", link):
                            pdfname = regex_res.group(0)[1:]

                            try:
                                if (pdfname not in list(pdfs.keys()) ) or (len(link) > len(pdfs[pdfname])):
                                    pdfs[pdfname] = link
                                    
                                    print(pdfname, link)
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



def start_index_scraper(subject):
    global url, subject_code, parent_url, visited
    subject_code = subject.upper()
    url = "https://www.uio.no/studier/emner/matnat/fys/" + subject.upper() +"/"
    parent_url = url
    visited.append(url)
    request_object = urllib.request.Request(url)
    page_object = urllib.request.urlopen(request_object)
    link_parser = LinkScrapeIndex()
    link_parser.urls = []
    link_parser.feed(page_object.read().decode("latin-1"))

    return link_parser.urls 

def child_scraping(url_, depth = 0):
    global url,visited
    url = url_
    visited.append(url) 

    request_object = urllib.request.Request(url)
    page_object = urllib.request.urlopen(request_object)
    link_parser = LinkScrapeChild()
    link_parser.urls = []
    link_parser.feed(page_object.read().decode("latin-1"))
   
    if depth <= 1:
        for url__ in link_parser.urls:
            child_scraping(url__, depth + 1)
    return link_parser.urls


deep = 3



if __name__ == '__main__':
    index_urls = start_index_scraper(sys.argv[1])
    
    for index_url in index_urls:
        print(f"\nchecking {index_url} ... \n")
        try:
            child_urls = child_scraping(index_url)
        except urllib.error.HTTPError:
            pass

