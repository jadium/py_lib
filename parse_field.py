'''
Created on Aug 26, 2012

@author: darnold
'''
import hashlib
import re
class ParserFieldError(Exception): pass
class ParseField(object):
    def __init__(self,regex, name):
        self.regex = re.compile(regex)
        self.name = name
        self.data = {}
        self.records = []
        self.md5 = hashlib.md5
        self.size = 0
        self.pop_count = 0
        self.trash_list = []
        self.entry = ""
        
    def __setattr__(self, name, value):
        record_hash = self.md5(value).hexdigest()
        try:
            # we add the group to the dictionary prior to appending 
            # to the records list, if error is raised due to invalid 
            # input, exception will be raised before appending to list
            # this prevents additions to the list that aren't in the dict
            if record_hash not in self.records:
                self.data[record_hash] = re.search(self.regex, value).group(1)
                self.records.append(record_hash)
                self.size += 1
                return
            else:
                raise ParserFieldError("duplicate entry: %s"%self.name)
        except:
            self.trash_list.append(record_hash)
    
    def __getattribute__(self, name):
        if name == 'item':
            record = self.records.pop()
            self.size -= 1
            entry = self.data[record]
            del self.data[record]
            return entry
            
    def __getattr__(self, name):
        raise AttributeError("%s does not exist"%name)
    
    def pop(self):
        try:
            key = self.records.pop()
            value = self.data[key]
            del self.data[key]
            return (key, value)
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
