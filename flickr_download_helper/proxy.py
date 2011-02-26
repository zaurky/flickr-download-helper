import urllib2
from flickr_download_helper.logger import Logger

class FDHProxySettings():
    def setValues(self, opt):
        self.user = opt.proxy_user
        self.password = opt.proxy_pass
        self.host = opt.proxy
        self.port = opt.proxy_port
        self.need_activation = opt.proxy

    def activate(self):
        if self.need_activation:
            Logger().info("\n== Initialising the proxy")
            Logger().debug("%s:%s@%s:%i"%(self.user, self.password, self.host,self.port))

            proxy_info = {
                    'user':self.user,
                    'pass':self.password,
                    'host':self.host,
                    'port':self.port
            }
            if self.user:
                if self.password:
                    proxy_support = urllib2.ProxyHandler({"http" : "http://%(user)s:%(pass)s@%(host)s:%(port)d" % proxy_info})
                else:
                    proxy_support = urllib2.ProxyHandler({"http" : "http://%(user)s@%(host)s:%(port)d" % proxy_info})
            else:
                proxy_support = urllib2.ProxyHandler({"http" : "http://%(host)s:%(port)d" % proxy_info})

            opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)

            # install it
            urllib2.install_opener(opener)
