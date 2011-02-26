import sqlite3
import os
import os.path
from flickr_download_helper.config import Singleton, OPT

class SaveAll(Singleton):
    version = 1
    __init = False
    def init(self, db_file = None):
        if db_file == None:
            db_file = OPT.database_logall_file
        self.db_file = db_file
        if not os.path.exists(db_file):
            self.__init = True
        self.conn = sqlite3.connect(self.db_file)
        self.c = self.conn.cursor()
        if self.__init or self.version < self.getVersion():
            self.initialize_db()

    def close(self):
        self.conn.commit()
        self.c.close()

    def commit(self):
        self.conn.commit()

    def getVersion(self):
        if self.__init: return 0
        self.c.execute('select v from Version')
        version = self.c.fetchone()
        return version[0]

    def initialize_db(self):
        version = self.getVersion()
        if version < 1:
#            self.c.execute('''create table Log (uuid INTEGER PRIMARY KEY AUTOINCREMENT, )''')
            self.c.execute('''create table User (
                    uuid INTEGER PRIMARY KEY AUTOINCREMENT,
                    id str,
                    ispro int,
                    iconserver int,
                    iconfarm int,
                    username str,
                    realname str,
                    mbox_sha1sum str,
                    location str,
                    photosurl int,
                    profileurl int,
                    photos_firstdate int,
                    photos_firstdatetaken str,
                    photos_count int
                )''')
            self.c.execute('''create table Photo (
                    uuid INTEGER PRIMARY KEY AUTOINCREMENT,
                    fk_owner INTEGER,
                    id int,
                    secret int,
                    server int,
                    isfavorite int,
                    license int,
                    rotation int,
                    originalsecret str,
                    originalformat str,
                    owner_id str,
                    owner_username str,
                    title str,
                    descriptio str,
                    visibility_ispublic int,
                    visibility_isfriend int,
                    visibility_isfamily int,
                    date_posted date,
                    date_taken date,
                    lasupdate int,
                    permcomment int,
                    permaddmeta int,
                    cancomment int,
                    canaddmeta int
                )''')
            self.c.execute('''create table Version (v int)''')
            self.c.execute('insert into Version values (1)')

        if version < 2:
            # next version of the database
            # self.c.execute('update Version set v = 2')
            pass

        self.commit()
        self.__init = False

    def getUser(self, user_id=None, user_name=None, user_uuid=None):
        sql_query = 'SELECT uuid, id, ispro, iconserver, iconfarm, username, realname, mbox_sha1sum, location, photosurl, profileurl, photos_firstdate, photos_firstdatetaken, photos_count FROM User'
        sql_from = []
        if user_id: sql_from.append("id == '%s'"%user_id)
        if user_uuid: sql_from.append("uuid == '%s'"%user_uuid)
        if user_name: sql_from.append("username == '%s'"%user_name)
        if len(sql_from) > 0:
            sql_query += ' WHERE ' + ' AND '.join(sql_from)

        result = self.c.execute(sql_query)
        result = map(lambda r: {'uuid':r[0], 'id':r[1], 'ispro':r[2], 'iconserver':r[3], 'iconfarm':r[4], 'username':r[5], 'realname':r[6], 'mbox_sha1sum':r[7], 'location':r[8], 'photosurl':r[9], 'profileurl':r[10], 'photos_firstdate':r[11], 'photos_firstdatetaken':r[12], 'photos_count':[13]}, result)
        return (len(result), result)

    def addUser(self, user):
        return None
        print user
        user_id = user['id']
        user_name = user['username']
        if type(user_name) == dict and '_content' in user_name: user_name = user_name['_content']
        already_in_db = self.getUser(user_id=user_id, user_name=user_name)
        if already_in_db[0] == 0:
            self.c.execute('''insert into User (
                    id,
                    ispro,
                    iconserver,
                    iconfarm,
                    username,
                    realname,
                    mbox_sha1sum,
                    location,
                    photosurl,
                    profileurl,
                    photos_firstdate,
                    photos_firstdatetaken,
                    photos_count
                ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                user['id'],
                user['ispro'],
                user['iconserver'],
                user['iconfarm'],
                user['username'],
                user['realname'],
                user['mbox_sha1sum'],
                user['location'],
                user['photosurl'],
                user['profileurl'],
                user['photos_firstdate'],
                user['photos_firstdatetaken'],
                user['photos_count']
            )
            already_in_db = self.getUser(user_id=user_id, user_name=user_name)
        return already_in_db[1][0]['uuid']

    def log():
        pass

class MyDatabase(Singleton):
    version = 1
    __init = False
    def init(self, db_file = None):
        if db_file == None:
            db_file = OPT.database_file
        self.db_file = db_file
        if not os.path.exists(db_file):
            self.__init = True
        self.conn = sqlite3.connect(self.db_file)
        self.c = self.conn.cursor()
        if self.__init or self.version < self.getVersion():
            self.initialize_db()

    def close(self):
        self.conn.commit()
        self.c.close()

    def getVersion(self):
        if self.__init: return 0
        self.c.execute('select v from Version')
        version = self.c.fetchone()
        return version[0]

    def initialize_db(self):
        version = self.getVersion()
        if version < 1:
            self.c.execute('''create table User (uuid INTEGER PRIMARY KEY AUTOINCREMENT, flickr_id text, username text)''')
            self.c.execute('''create table Photo (uuid INTEGER PRIMARY KEY AUTOINCREMENT, flickr_id text, fk_user int)''')
            self.c.execute('''create table PhotoUrl (uuid INTEGER PRIMARY KEY AUTOINCREMENT, fk_photo int, fk_size int, url text)''')
            self.c.execute('''create table Size (uuid INTEGER PRIMARY KEY AUTOINCREMENT, label text, value text)''')
            for s in (('Original', 'o'), ('Large', 'l'), ('Medium', 'm'), ('Square', 's'), ('Thumbnail', 't')):
                self.c.execute('insert into Size (label, value) values (?, ?)', s)

            self.c.execute('''create table Favorite (uuid INTEGER PRIMARY KEY AUTOINCREMENT, fk_user int, profile_url text, label text, last_update date default now)''')

#            self.c.execute('''create table  (uuid INTEGER PRIMARY KEY AUTOINCREMENT, flickr_id text, ''')
#            self.c.execute('''create table  (uuid INTEGER PRIMARY KEY AUTOINCREMENT, flickr_id text, ''')
#            self.c.execute('''create table  (uuid INTEGER PRIMARY KEY AUTOINCREMENT, flickr_id text, ''')
#            self.c.execute('''create table  (uuid INTEGER PRIMARY KEY AUTOINCREMENT, flickr_id text, ''')
            self.c.execute('''create table Version (v int)''')
            self.c.execute('insert into Version values (1)')

        if version < 2:
            # next version of the database
            # self.c.execute('update Version set v = 2')
            pass

        self.__init = False

    # Users
    def addUser(self, username, flickr_id):
        self.c.execute('insert into User (flickr_id, username) values (?, ?)', (flickr_id, username))

    def getUser(self, username = '', flickr_id = ''):
        request = 'select * from User'
        clauses = []
        if username != '':
            clauses.append('username = "%s"'%(username))
        if flickr_id != '':
            clauses.append("flickr_id = '%s'"%(flickr_id))
        if len(clauses) > 0:
            request += " where " + ' and '.join(clauses)
        self.c.execute(request)
        ret = []
        for u in self.c:
            ret.append(u)
        return ret

    # Favorite
    def addFavorite(self, userid, profile_url, label):
        user = self.getUser(flickr_id = userid)
        self.c.execute('insert into Favorite (fk_user, profile_url, label) values (?, ?, ?)', (user[0][0], profile_url, label))

    def getFavorite(self, userid = '', profile_url = '', label = ''):
        request = 'select * from Favorite'
        clauses = []
        if userid != '':
            user = self.getUser(flickr_id = userid)
            clauses.append('fk_user = %s'%user[0][0])
        if profile_url != '':
            clauses.append('profile_url = %s'%profile_url)
        if label != '':
            clauses.append('label = %s'%label)
        if len(clauses) > 0:
            request += " where " + ' and '.join(clauses)
        self.c.execute(request)
        ret = []
        for u in self.c:
            ret.append(u)
        return ret

