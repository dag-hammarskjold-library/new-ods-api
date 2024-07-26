from dlx import DB
from config_dlx import Config
import time
import re
from datetime import datetime
from dlx.file import S3, File, Identifier, FileExists, FileExistsConflict

DB.connect(Config.connect_string, database="undlFiles")
#S3.connect(bucket='undl-files')
from dlx.marc import Bib, BibSet, AuthSet, Query, Condition

def escape_characters(input_string, chars_to_escape):
    for char in chars_to_escape:
        input_string = input_string.replace(char, f'\\{char}')
    return input_string

def get_tcodes(subject):
    query = Query(
        Condition(
            tag='150',
            subfields={'a': re.compile(str(subject).upper())}
            )
    )

    authset = AuthSet.from_query(query, projection={'035':1,'150':1})

    for auth in authset:
        val_035a=auth.get_values('035','a')
        val_035a=''.join([str for str in val_035a if str[0] in {'T', 'P'}] )
    return val_035a

start_time_chunk=time.time()
symbols=["A/CONF.94/L.3"]
for symbol in symbols:
    symbol=escape_characters(symbol,"()")
    query = Query.from_string("symbol:/^"+symbol+"$/") 

    lst=[]
    document_symbol=""
    distribution=""
    area="UNDOC"
    publication_date=""
    release_date=datetime.now().strftime('%d/%m/%y')
    sessions=""
    title_en=""
    agendas=""
    subjects=""
    tcodes=""
    #datamodel=(document_symbol, distribution, area, publication_date, release_date, sessions, title_en, agendas, subjects)# defining the order of the fields

    for bib in BibSet.from_query(query):
        document_symbol=bib.get_values('191', 'a')
        distribution=bib.get_value('091', 'a')
        #area is a constant UNDOC
        publication_date=bib.get_value('269','a')
        #release_date=datetime.now().strftime('%d %B')
        release_date=datetime.now().strftime('%d/%m/%y')
        sessions=' '.join(bib.get_values('191','c'))
        if publication_date !='':
            publication_date=datetime.strptime(publication_date, '%Y-%m-%d').strftime('%d/%m/%y') 
        title_en=bib.get_value('245', 'a')+" "+bib.get_value('245', 'b')
        agendas=' '.join(bib.get_values('991','b'))
        #subjects=','.join(bib.get_values('650','a'))
        tcodes=','.join([get_tcodes(subject) for subject in bib.get_values('650','a')])
                                       
        datamodel={"symbol":document_symbol[0],"distribution":distribution,"area": area, "publication_date":publication_date, 
                   "release_date":release_date, "sessions":sessions, "title":title_en, "agendas":agendas, "subjects":subjects, "tcodes":tcodes}
        lst.append(datamodel)
        print('- - -')
        print(f'The files for {document_symbol[0]} are:')
        for lang in ["AR","ZH","EN", "FR", "RU", "ES", "DE"]:
            try:
                f = File.latest_by_identifier_language(Identifier('symbol', document_symbol[0]), lang)
                print(''.join(f.languages), f.uri)
            except:
                pass
    
    #for t in sorted(lst,key=lambda st: st[0],reverse=True):#sorting
    for d in lst:
        for k in d:
            print (k+":"+d[k])
print(f"--- {time.time() - start_time_chunk} seconds for full speeches list ---")
       