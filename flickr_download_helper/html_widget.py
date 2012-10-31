import markup

class FDH_page(markup.page):
    def __str__(self, *attr):
        self.br()
        self.br()
        self.hr()
        str = "Content-type: text/html\n\n"
        str += super(FDH_page, self).__str__(*attr)
        return str

    def init(self, css=None, header=None, script=None):
        return super(FDH_page, self).init(
                title = "Flickr Download Helper",
                charset = "utf-8",
                script=script,
                header=header,
                footer='(c) 2010 - flickr download helper',
                css=css)

class Redirect_Page:
    def __str__(self, *attr):
        str = """Content-type: text/html


            <html><head>
            <meta http-equiv="Refresh" content="0;URL=%s">
            </head></html>""" % (self.url)
        return str

    def __init__(self, url):
        self.url = url
