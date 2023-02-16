

def process_invoice(data):
    results={}
    for k, v in data['results']['analyzeResult']['documents'][0]['fields'].items():
        if v['type'] != 'array': # TO DO - Implement Array Processing and better type handling
            results['value'][k] = v['content']
    return(results)
 

def process_tables(data):

    tables=[]
    results={}
    if 'tables' in data['results']['analyzeResult'].keys():
            res=data['results']['analyzeResult']['tables']
            for table in res:
                raw_text=[]
                cells = []
                headers=[]
                regions=table['boundingRegions']
                for r in regions: pageNumber = r['pageNumber']
                for cell in table['cells']:
                    cells.append(
                    {
                        "text": cell['content'],
                        "rowIndex": cell['rowIndex'],
                        "colIndex": cell['columnIndex'],
                        #"confidence": '',
                        "is_header": False
                    })
                    isheader=False
                    if ('kind' in cell.keys() ): 
                        isheader = (cell['kind']=='columnHeader')
                        cells.append({'is_header': isheader})
                        if isheader: 
                            headers.append(cell['content'])
                    if not isheader: 
                        raw_text.append(cell['content'])


                tables.append({
                    "page_number": pageNumber,
                    "raw_count" : table['rowCount'],
                    "column_count": table['columnCount'],
                    "headers": headers,
                    "cells": cells,
                    "raw_text":raw_text
                }
                )
                h=len(headers)
    #results['value']['data']=tables
    results['value']=tables
    return(results)
                