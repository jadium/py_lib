#!/usr/bin/python
import re


class db_table(object):
    def __init__(self):
        self.db_params = {}


class orm:
        space_regex = re.compile('\s')
        varchar_regex = re.compile('varchar\((\d*)\)')
        enum_regex = re.compile('enum(\(.*\))')

        def __varchar(size):
            pass

        def __get_loaded(self, tpl):
            query = "select "
            for i in range(0, len(self.fields) - 1):
                query += "%s, " %self.fields[i][0]
            query += "%s " %self.fields[i+1][0]
            query += "from %s where " % self.table_name

            def load(**kwargs):
                params = []
                for arg in kwargs.keys():
                    params.append("%s='%s'" % (arg, kwargs[arg]))
                real_query = query +params.pop()+" and ".join(params)
                print real_query
                self.cursor.execute(real_query)
                results = self.cursor.fetchone()
                for i in range(0, len(self.fields)):
                    tpl.set(self.fields[i][0], results[i])
            return load
        def __get_all(self, tpl):
            
        def __get_saved(self, tpl):
            def update():
                query = "update %s set " %self.table_name
                db_fields = []
                params = []
                for field in self.fields:
                    params.append("%s='%s'" % (field[0], tpl.db_params[field[0]]))
                param_list = ", ".join(params)
                query += param_list
                self.cursor.execute(query)
                self.db.commit()

            def insert():
                params = []
                values = []
                for field in self.fields:
                    print "%s: %s" % (field[0], tpl.db_params[field[0]])
                    params.append(field[0])
                    values.append("'%s'" % tpl.db_params[field[0]])
                query = "insert into  %s (%s) values (%s)" %(self.table_name, ", ".join(params), ", ".join(values))
                print query
                print self.cursor.execute(query)
                self.db.commit()
            return (update, insert)

        def __get_fields(self):
            self.fields = []
            self.cursor.execute('desc %s' % self.table_name)
            res = self.cursor.fetchall()
            for result in res:
                self.fields.append((result[0], result[1]))


        def __init__(self, *args, **kwargs):
            req_args = ['db', 'user','passwd','host']
            for arg in req_args:
                if arg not in kwargs.keys():
                    raise Exception(
                        "Required Arguments: 'db','user','passwd','host'")
            try:
                import MySQLdb
            except ImportError:
                raise Exception("MySQLdb is not installed on this system, or is not in PYTHONPATH")
            setattr(self, 'db', MySQLdb.connect(**kwargs))
            setattr(self, 'cursor', self.db.cursor())
        

        def get_tables(self):
            self.cursor.execute('show tables')
            tables = []
            for table in self.cursor.fetchall():
                tables.append(table[0])
            return tables

        def __dump(self):
            for key in db_table.db_params.keys():
                print key, db_table.db_params[key]

        def __factory(self, tpl, field, field_type):

            def getter():
                return getattr(tpl, field, None)

            def getval(var):
                try:
                    return tpl.db_params[var]
                except KeyError:
                    return False

            def get_fields():
                try:
                    fields = []
                    for field in self.fields:
                        fields.append(field[0])
                    return fields
                except:
                    return []

            def setval(var, val):
                fields = []
                for field in self.fields:
                    fields.append(field[0])
                if var not in fields:
                    raise Exception("setting invalid variable name, %s not listed in field list" % var)
                try:
                    tpl.db_params[var] = val
                    setattr(tpl, var, val)
                except:
                    return False

            def dump():
                try:
                    return tpl.db_params
                except:
                    return False

            def setter(value):
                tpl.db_params[field] = value
                setattr(tpl, field, value)

            if re.search(self.__class__.varchar_regex, field_type):
                size = int(re.search(self.__class__.varchar_regex, field_type).group(1))

                def setter(value):
                    if len(value) <= size:
                        tpl.db_params[field] = value
                        setattr(tpl, field, value)
                        return
                    raise Exception("String Length Greater than Field Length")

            if re.search(self.__class__.enum_regex, field_type):
                allowed_values = eval(
                    re.search(self.__class__.enum_regex, field_type).group(1))

                def setter(value):
                    if value in allowed_values:
                        tpl.db_params[field] = value
                        setattr(tpl, field, value)
                        return
                    raise Exception("Value not allowed, possible values: %s" %
                                    ",".join(allowed_values))

            (update, insert) = self.__get_saved(tpl)
            load = self.__get_loaded(tpl)
            return (getter, setter, getval, setval,dump,update,insert,load,get_fields)

        def create(self, table_name):
            import re
            tpl = db_table()

            self.table_name = table_name
            if re.search(self.__class__.space_regex, table_name):
                raise Exception("table name invalid, spaces are not allowed!")
            self.__get_fields()
            for field, field_type in self.fields:
                (getter, setter,getval,setval,dump,update,insert,load,get_fields) = self.__factory(tpl,field,field_type)
                #(update, insert)=self.__get_saved(tpl)
                setattr(tpl, 'get_%s' % field,getter)
                setattr(tpl, 'set_%s' % field,setter)
                del getter
                del setter
            setattr(tpl, 'fields', self.fields)
            setattr(tpl, 'get_fields', get_fields)
            setattr(tpl, 'get', getval)
            setattr(tpl, 'set', setval)
            setattr(tpl, 'load', self.__get_loaded(tpl))
            setattr(tpl, 'update', update)
            setattr(tpl, 'insert', insert)
            setattr(tpl, 'dump', dump)
            return tpl
