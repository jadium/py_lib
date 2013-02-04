'''
Created on Aug 26, 2012

@author: darnold
'''
import hashlib
import re
class ParserFieldError(Exception): pass
class ParseField(object):
    '''
    classdocs
    '''


    def __init__(self,regex, name):
        '''
        Constructor
        '''
        self.regex = re.compile(regex)
        self.name = name
        self.data = {}
        self.records = []
        self.md5 = hashlib.md5
        self.size = 0
        self.pop_count = 0
        self.trash_list = []
        
    def __set__(self, parser_input):
        try:
            record_hash = self.md5(parser_input).hexdigest()
            # we add the group to the dictionary prior to appending 
            # to the records list, if error is raised due to invalid 
            # input, exception will be raised before appending to list
            # this prevents additions to the list that aren't in the dict
            if record_hash not in self.records:
                self.data[record_hash] = re.search(self.regex, parser_input).group(1)
                self.records.append(record_hash)
                self.size += 1
                return
            else:
                raise ParserFieldError("duplicate entry: %s"%self.name)
        except:
            self.trash_list.append(record_hash)
    
    def __get__(self):
        try:
            key = self.records.pop()
            return (key, self.data[key])
        except:
            raise ParserFieldError("no such key found in %s"%self.name)
    
    def get_record(self, key):
        if key in self.trash_list:
            return None
        try:
            return self.data[key]
        except:
            raise ParserFieldError("invalid key for %s"%self.name)
    
    def __iter__(self):
        return self 
    
    def next(self):
        if self.pop_count < self.size:
            try:
                iter_data = self.records.pop()
                return iter_data
            except:
                raise StopIteration 
        raise StopIteration
     
    def keys(self):
        return self.data.keys()
