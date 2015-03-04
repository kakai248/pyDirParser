import os
import urllib.request
from urllib.parse import urlparse, unquote
from datetime import datetime
from bs4 import BeautifulSoup

class DirParser:

    """ Creates a new instance of DirParser
        It uses the BeautifulSoup4 library to parse the HTML
        
        Arguments:
        document -- can be either the HTML document or a URL to fetch the document
        parser -- the parser to be used by BeautifulSoup4 to parse the file
                  by default it uses the default python HTML parser
                  
        Class variables:
        dirs -- list of directories of type Dir
        files -- list of files of type File
    """
    def __init__(self, document, parser="html.parser"):
        # List of directories of type Dir
        self.dirs = []
        
        # List of files of type File
        self.files = []
    
        parsedUrl = urlparse(document)
        # It's a url, obtain the document
        if parsedUrl.scheme and parsedUrl.netloc:
            self._url = document
            document = urllib.request.urlopen(self._url).read()
        
        # Parse the document
        soup = BeautifulSoup(document, parser)
        self._parseDocument(soup)
        
    """ Private method to parse document
    
        Arguments:
        soup -- BeautifulSoup object instanced with the document
    """
    def _parseDocument(self, soup):
        entries = soup.find_all("tr")
        for entry in entries[3:-1]:
            # get entry attributes
            name = unquote(entry.find("a")["href"])
            lastModified = datetime.strptime(entry.find_all("td")[2].string.strip(), "%d-%b-%Y %H:%M")
            size = self._parseSize(entry.find_all("td")[3].string.strip())
            description = entry.find_all("td")[4].string.strip()
            
            # if entry name ends in / its a directory
            isDir = True if name[-1:] == "/" else False
            
            if isDir:
                self.dirs.append(_Dir(name[:-1], lastModified, description))
            else:
                self.files.append(_File(name, lastModified, size, description))

    """ Private method to parse size
        
        Arguments:
        size -- string size to be parsed
                can take the follow example forms:
                    569   -- 569 bytes
                    3M    -- 3000000 bytes
                    1.9G  -- 1900000000 bytes
                    0.4T  -- 400000000000 bytes
                    
        Returns: number of bytes
    """
    def _parseSize(self, size):
        # No size
        if not size:
            return None
        
        # lack of symbol means first symbol (Bytes)
        if size.isdigit():
            return int(size)
        
        symbols = ("B", "K", "M", "G", "T")
        number = size[:-1]
        symbol = size[-1:].upper()

        # invalid size
        if symbol not in symbols:
            return None
        
        return int(float(number) * pow(10, symbols.index(symbol) * 3))
            
class _Dir:

    """ Creates a new instance of type Dir
        
        Arguments:
        name -- name of the dir
        lastModified -- datetime of modification of the dir
        description -- description of the dir
        
        Class variables:
        name -- name of the dir
        lastModified -- datetime of modification of the dir
        description -- description of the dir
    """
    def __init__(self, name, lastModified, description):
        self.name = name
        self.lastModified = lastModified
        self.description = description
        
class _File:

    """ Creates a new instance of type File
        
        Arguments:
        name -- name of the file
        lastModified -- datetime of modification of the file
        size -- size of the file in bytes
        description -- description of the file
        
        Class variables:
        name -- name of the file
        extension -- extension of the file, if it has one
        lastModified -- datetime of modification of the file
        size -- size of the file in bytes
        description -- description of the file
    """
    def __init__(self, name, lastModified, size, description):
        self.name = name
        self.extension = os.path.splitext(name)[-1].lower()[1:]
        self.lastModified = lastModified
        self.size = size
        self.description = description