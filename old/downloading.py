import sys, os, datetime, requests
from pdfrw import PdfReader, PdfWriter   
import uuid
from PyPDF2 import PdfFileReader, PdfFileWriter
import builtins
bytes_type = type(bytes()) # Works the same in Python 2.X and 3.X
string_type = getattr(builtins, "unicode", str)


def download_pdf(url, name, subject):
    # assure folder(s) exists
    if not os.path.exists(os.path.relpath(f"downloads")):
        os.system(f"mkdir downloads")
    if not os.path.exists(os.path.relpath(f"downloads/{subject}")):
        os.system(f"mkdir downloads/{subject}")
    # generate uuid from url
    sys.stdout.write(f"Downloading {name}{' '*20} \r" )
    pdf_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, url)

    filepath = os.path.relpath(f"downloads/{subject}/{name}")
    if os.path.exists(filepath):
        # if file exists, check if uuid matches. If not, add a (#) suffix
        with open(filepath, 'rb') as f:
            reader = PdfFileReader(f)
            try:
                if str(pdf_uuid) == reader.getDocumentInfo()["/Keywords"]:
                    print(f"File '{name}' has already been downloaded with UiOScrape!")
                    return
            except:
                pass
            samenames = []
            for exists in os.listdir(os.path.relpath(f"downloads/{subject}")):
                if exists.startswith(name):
                    try:
                        samenames.append(int(exists.lstrip(name)[1:-1]))
                    except:
                        samenames.append(0)
            new_suffix = max(samenames)+1
            filepath = os.path.relpath(f"downloads/{subject}/{name.rstrip('.pdf')}({new_suffix}).pdf")
        


    #download pdf
    sys.stdout.flush()
    r = requests.get(url)
    open(filepath, 'wb').write(r.content)


    #change metadata of pdf to include uuid to be recognized
    fin = open(filepath, 'rb')
    reader = PdfFileReader(fin)
    writer = PdfFileWriter()
    writer.appendPagesFromReader(reader)

    # writing metadata
    writer.addMetadata({
        '/Subject': subject,
        '/Author': "UiOScrape",
        '/Keywords':str(pdf_uuid)
    })

    fout = open(filepath, 'wb')
    
    writer.write(fout)
    
    fin.close()
    fout.close()
 