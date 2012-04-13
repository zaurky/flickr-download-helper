from flickr_download_helper.config import OPT, Singleton
import logging
import logging.config
import traceback
import random

class ConsoleLogger(Singleton):
    def debug(self, label):
        if OPT.debug: print "debug: %s"%label

    def info(self, label):
        print label

    def warn(self, label):
        print "warn: %s"%label

    def error(self, label):
        print "error: %s"%label

    def prompt(self, label):
        print label

    def print_tb(self, label):
        traceback.print_tb(label)

class NoneLogger(Singleton):
    def debug(self, label): pass
    def info(self, label): pass
    def warn(self, label): pass
    def error(self, label): pass
    def prompt(self, label): pass
    def print_tb(self, label): pass

def convertType(obj):
    if type(obj) == int:
        return str(obj)
    return obj

class FileLogger(Singleton):
    def treatLabel(self, label):
        if type(label) == list:
            return map(lambda l:" %s: \t%s"%(self.session_id, convertType(l).replace('\n', '')), label)
        return " %s: \t%s"%(self.session_id, label.replace('\n', ''))

    def setup(self):
        self.internal = logging.getLogger()
        self.session_id = "%06d"%(random.randint(0, 10000))
        print "logging as %s"%self.session_id

    def debug(self, label):
        self.internal.debug(self.treatLabel(label))

    def info(self, label):
        self.internal.info(self.treatLabel(label))

    def warn(self, label):
        self.internal.warn(self.treatLabel(label))

    def error(self, label):
        if type(label) == str:
            self.internal.error(self.treatLabel(label))
        elif hasattr(label, 'message'):
            self.internal.error(self.treatLabel(label.message))
        else:
            self.internal.error(self.treatLabel(str(label)))

    def prompt(self, label):
        self.internal.info("this is a prompt! there should not be any prompt here!")
        self.internal.info(self.treatLabel(label))

    def print_tb(self, label):
        try:
            self.internal.error(traceback.format_tb(label))
        except AttributeError:
            self.internal.error("Can't get traceback")


########################################################
class Logger(Singleton):
    def setup(self):
        if OPT.logger == 'console':
            self.internal = ConsoleLogger()
        elif OPT.logger == 'file':
            self.internal = FileLogger()
            try:
                logging.config.fileConfig(OPT.config_file)
            except Exception, e:
                self.internal = ConsoleLogger()
                raise e
            self.internal.setup()
        else:
            self.internal = NoneLogger()

    def __getattr__( self, attr ):
        if attr.startswith("__") and attr.endswith("__"):
            raise AttributeError, attr
        return getattr(self.internal, attr)

