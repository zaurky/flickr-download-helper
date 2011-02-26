import os
import sys
import getopt
import time

from ConfigParser import ConfigParser

class Singleton(object):
    """
    Duplicate from the Singleton() class from the MMC Project,
    to remove unwanted dependencies
    """

    def __new__(cls, *args):
        if not '_the_instance' in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance

class Options(Singleton):
    if 'HOME' in os.environ:
        configuration_dir = '%s/.flickr_download_helper/' % os.environ['HOME']
    else:
        configuration_dir = '/etc/fdh'
    token_file = os.path.join(configuration_dir, 'token')
    backup_dir = os.path.join(configuration_dir, 'backup')
    photo_dir = os.path.join(configuration_dir, 'photo')
    news_dir = os.path.join(configuration_dir, 'news') # should be configurable
    files_dir = os.path.join(configuration_dir, 'files') # should be configurable
    daily_news_dir = os.path.join(news_dir, 'daily')
    existing_ids_file = os.path.join(configuration_dir, 'existing_ids')
    favorites_file = os.path.join(configuration_dir, 'apache', 'favorites') # be configurable

    database_file = os.path.join(configuration_dir, 'db', 'fdh.db')
    database_logall_file = os.path.join(configuration_dir, 'db', 'logall.db')

    user_id = None
    url = None
    get_url = None
    nick = None
    photoset_id = None
    collection_id = None
    photo_id_in_file = None
    photo_ids = None
    tags = None
    username = None
    sort_by_user = True
    sort_by_photoset = False
    retrieve = False
    force = False
    interactive = True
    new_in_dir = False
    daily_in_dir = False
    fast_photo_url = False
    restore_photo_url = False
    only_backup_photo_url = False
    sleep_time = 1
    photo_id2destination = {}
    proxy = None
    proxy_port = 80
    proxy_user = None
    proxy_pass = None
    debug=False
    logger='console'
    config_file='/etc/fdh/fdh.ini'
    since = None
    loop = None
    smart = False
    not_smart = []
    group_id = None
    try_from_groups = False
    force_group_verbose = False

    user_hash = {}

    # used for getContacts
    getContactFields = ['nsid']
    advContactFields = False


class OptConfigReader(Singleton):
    def setup(self, config_file='/etc/fdh/fdh.ini'):
        self.cp = ConfigParser()
        self.cp.read(config_file)

        self.opt = Options()
        self.opt.config_file=config_file

        # get the main options
        if self.cp.has_section("main"):
            for option in ('sort_by_user', 'sort_by_photoset', 'retrieve',
                    'force', 'interactive', 'new_in_dir', 'fast_photo_url',
                    'daily_in_dir', 'debug'):
                if self.cp.has_option("main", option):
                    setattr(self.opt, option, self.cp.getboolean("main", option))

            if self.cp.has_option("main", "not_smart"):
                self.opt.not_smart = self.cp.get("main", "not_smart").split(',')
            if self.cp.has_option("main", "logger"):
                self.opt.logger = self.cp.get("main", "logger")
            if self.cp.has_option("main", "sleep_time"):
                self.opt.sleep_time = self.cp.get("main", "sleep_time")

        # get the directories to work in
        if self.cp.has_section("path"):
            if self.cp.has_option("path", "token_file"):
                self.opt.token_file = self.cp.get("path", "token_file")
            if self.cp.has_option("path", "backup_dir"):
                self.opt.backup_dir = self.cp.get("path", "backup_dir")
            if self.cp.has_option("path", "photo_dir"):
                self.opt.photo_dir = self.cp.get("path", "photo_dir")
            if self.cp.has_option("path", "news_dir"):
                self.opt.news_dir = self.cp.get("path", "news_dir")
            if self.cp.has_option("path", "daily_news_dir"):
                self.opt.daily_news_dir = self.cp.get("path", "daily_news_dir")
            if self.cp.has_option("path", "database_file"):
                self.opt.database_file = self.cp.get("path", "database_file")
            if self.cp.has_option("path", "database_logall_file"):
                self.opt.database_logall_file = self.cp.get("path", "database_logall_file")
            if self.cp.has_option("path", "existing_ids_file"):
                self.opt.existing_ids_file = self.cp.get("path", "existing_ids_file")
            if self.cp.has_option("path", "files_dir"):
                self.opt.files_dir = self.cp.get("path", "files_dir")

        # get proxy options
        if self.cp.has_section("proxy"):
            if self.cp.has_option("proxy", "host"):
                self.opt.proxy = self.cp.get("proxy", "host")
            if self.cp.has_option("proxy", "port") and self.cp.get("proxy", "port") != '':
                self.opt.proxy_port = self.cp.getint("proxy", "port")
            if self.cp.has_option("proxy", "user"):
                self.opt.proxy_user = self.cp.get("proxy", "user")
            if self.cp.has_option("proxy", "pass"):
                self.opt.proxy_pass = self.cp.get("proxy", "pass")

class OptReader(Singleton):
    """
[Options]
    -h --help                       display this help message
    -d --debug                      put the debug on (show all the calls to the flickr API)
       --logger                     change the logger (default to 'console')

    # one of the next 6 parameters is mandatory if you work on a user
    -i --id                         the user's id
    -u --url                        the user home url
    -n --nick                       the user nick name (not the username)
    -l --username                   the user name

       --photoset_id                a photoset id to retrieve
    -c --collection_id              a collection id to retrieve (this is a set of photosets) it requires a user is set
       --photo_id_in_file           a file containing url or ids of photos (one per line)
    -t --tags                       a tag list (separated by commas) it requires a user is set
    -g --group_id                   a group id, can be used with a user
       --get_url                    download gessing what you want from the url schema

       --sbu --sort_by_user         only valid when --photo_id_in_file is set.
                                    create a directory per user and sort photos by user
       --sbp --sort_by_photoset     only valid when a user is asked
                                    create a directory per user's photoset

    -f --force                      force the download of the picture even if it already exists
       --not_interactive            disable the interactive mode (all the queries are replied 'no')
    -r --retrieve                   retrieve the photos (else the photo's URL are displayed and that's all)
    -w --new_in_dir                 create a directory fill by links to the new files (only active if retrieve is set)
    --dw --daily_in_dir             create a directory fill by links to the daily new files

    -p --photodir                   the directory where the photos are downloaded
    -s --sleep_time                 the time we wait between two photo download
       --since                      a unix timestamp to know since when should we look the photos
       --loop                       an integer specifying the time between two loops of fdhs
       --smart                      a flag to say if you want to pass by the get recently upload contact process (experimental)

       --database_file              the path to the sqlite3 database
       --database_logall_file       the path to the log all sqlite3 database

       --fast_photo_url             don't ask flickr API for the photo's URL (work only if you have access to all the users photos)
       --restore_photo_url          don't ask for flickr API to know the users photos (work only if you already know the user's photos)
       --only_backup_photo_url      just ask for the users photos, backup their URL and quit

       --proxy                      to use a proxy, give the hostname
       --proxy_port                 the proxy port (default 80)
       --proxy_user                 the proxy username if needed
       --proxy_pass                 the proxy password if needed

    --tfg --try_from_groups         try to get this users photos from its groups (require a user)
    --fgv --force_group_verbose     force the verbose retrieving of groups (ie : get all the group content and then filter on user)

    ###### options for getContacts
    --gcf --getContactFields        the contacts fields to display (a list of fields separated by ,)
    --acf --advContactFields        if the fields are not in the getList function but in the getInfo one

    """
    def read(self, script = ''):
        opt = Options()
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hdfrwi:u:n:p:s:l:c:t:g:",
                    [
                        "help", "id=", "url=", "nick=", "photodir=",
                        "retrieve", "sleep_time=", "force", "username=",
                        "fast_photo_url", "debug", "restore_photo_url",
                        "only_backup_photo_url", "photoset_id=", "tags=",
                        "photo_id_in_file=", "sort_by_user", "proxy=",
                        "proxy_port=", "proxy_user=", "proxy_pass=",
                        "new_in_dir", "sort_by_photoset", "collection_id=",
                        "not_interactive", "logger=", "database_file=",
                        "database_logall_file=", "since=", "loop=",
                        "daily_in_dir", "dw", "gcf=", "getContactFields=",
                        "sbu", "sbp", "smart", "acf", "advContactFields",
                        "group_id=", 'try_from_groups', 'tfg',
                        "fgv", "force_group_verbose", 'get_url='
                    ])
        except getopt.error, msg:
            print self.__doc__
            print "for help use --help"
            return 2

        # process options
        if script != 'getContacts.py':
            print "\n== process options"
            if len(opts) == 0:
                print self.__doc__
                return 1

        for o, a in opts:
            if o in ("-h", "--help"):
                print self.__doc__
                return 1
            elif o in ("--id", "-i"): opt.user_id = a
            elif o in ("--url", "-u"): opt.url = a
            elif o in ("--nick", "-n"): opt.nick = a
            elif o in ("--username", "-l"): opt.username = a

            elif o in ("--photoset_id"): opt.photoset_id = a
            elif o in ("--collection_id"): opt.collection_id = a
            elif o in ("--photo_id_in_file"): opt.photo_id_in_file = a
            elif o in ("--tags", "-t"): opt.tags = a
            elif o in ("-g", "--group_id"): opt.group_id = a
            elif o in ("--get_url"): opt.get_url = a
            elif o in ('--sort_by_user', '--sbu'): opt.sort_by_user = True
            elif o in ("--sort_by_photoset", '--sbp'): opt.sort_by_photoset = True

            elif o in ("--retrieve", "-r"): opt.retrieve = True
            elif o in ("--force", "-f"): opt.force = True
            elif o in ("--not_interactive"): opt.interactive = False
            elif o in ("--debug", "-d"): opt.debug = True
            elif o in ("--logger"): opt.logger = a
            elif o in ("--new_in_dir", "-w"): opt.new_in_dir = True
            elif o in ("--dw", "--daily_in_dir"): opt.daily_in_dir = True

            elif o == "--fast_photo_url": opt.fast_photo_url = True
            elif o == "--restore_photo_url": opt.restore_photo_url = True
            elif o == "--only_backup_photo_url": opt.only_backup_photo_url = True

            elif o in ("--sleep_time", "-s"): opt.sleep_time = int(a)
            elif o in ("--photodir", "-p"): opt.photo_dir = a
            elif o in ("--since"): opt.since = a
            elif o in ("--loop"):opt.loop = int(a)
            elif o in ("--smart"):opt.smart = True

            elif o in ("--database_file"): opt.database_file = a
            elif o in ("--database_logall_file"): opt.database_logall_file = a

            elif o in ("--proxy"): opt.proxy = a
            elif o in ("--proxy_port"): opt.proxy_port = int(a)
            elif o in ("--proxy_user"): opt.proxy_user = int(a)
            elif o in ("--proxy_pass"): opt.proxy_pass = int(a)

            elif o in ("--try_from_groups", "--tfg"): opt.try_from_groups = True
            elif o in ("--force_group_verbose", "--fgv"): opt.force_group_verbose = True

            elif o in ("--gcf", "--getContactFields"): opt.getContactFields = a.split(",")
            elif o in ("--acf", "--advContactFields"): opt.advContactFields = True
            else:
                print self.__doc__
                return 2

        if opt.debug: print "switch to debug mode"
        if not opt.photo_id_in_file and opt.sort_by_user: opt.sort_by_user = False
        if script != 'getContacts.py':
            if opt.collection_id and not opt.user_id and not opt.url and not opt.nick and not opt.username:
                print "collection_id requires a user!"
                return 2
            if opt.tags and not opt.user_id and not opt.url and not opt.nick and not opt.username:
                print "tags requires a user!"
                return 2
            if opt.try_from_groups and not opt.user_id and not opt.url and not opt.nick and not opt.username:
                print "try from group requires a user!"
                return 2
        if not opt.retrieve and opt.new_in_dir:
            print "--new_in_dir can only be set when --retrieve is also set : putting new_in_dir to False"
            opt.new_in_dir = False
        if not opt.retrieve and opt.daily_in_dir:
            print "--daily_in_dir can only be set when --retrieve is also set : putting daily_in_dir to False"
            opt.daily_in_dir = False

        if opt.since != None:
            if opt.since.find('last') == 0:
                since = opt.since.replace('last', '')
                if since.find('h') != -1:
                    opt.since = int(time.time()) - 3600 * int(since.replace('h', ''))
                elif since.find('d') != -1:
                    opt.since = int(time.time()) - 3600*24 * int(since.replace('d', ''))
        if opt.group_id and not opt.user_id and not opt.url and not opt.nick and not opt.username:
            print "for the moment you must put a user when asking for a group!"
            return 2


        # process arguments (no know argument at the moment)
        for arg in args: pass

        return 0

OPT=Options()
