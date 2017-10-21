import win32com
from win32com.client import Dispatch
from os import walk

def get_WordContent(FullFileName):
    msword = Dispatch('Word.Application')
    msword.Visible = 0
    msword.DisplayAlerts = 0
    doc = msword.Documents.Open(FileName=FullFileName, Encoding='gb18030')
    range = doc.Range(doc.Content.Start, doc.Content.End)
    text = range.__str__()
    doc.Close
    doc=None
    msword=None
    return text

def get_allFiles(dir_name):
    files=[]
    for root,dirs,files in walk(dir_name):
        print(files)
    return files