import libxml2
import libxslt
import os
import urllib2

from convenient_python.os_utils import has_permissions

class XMLError(Exception): pass

class XML(object):
    def __init__(self, xml_file=None, xml_string=None, xml_uri=None, 
                 xsl_file=None, xsl_string=None):
        if xml_file:
            self._doc = self.parse_file(xml_file)
        elif xml_string:
            self._doc = self.parse_string(xml_string)
        elif xml_uri:
            self._doc = self.parse_from_url(xml_uri)
        else:
            self._doc = None

        if xsl_file:
            self._style = self.parse_xsl_file(xsl_file)
        elif xsl_string:
            self._style = self.parse_xsl_string(xsl_string)
        else:
            self._style = None

    def parse_file(self, xml_file):
        if os.path.isfile(xml_file):
            raise XMLError("XML file path does not resolve to an actual " \
                           "file: %s" % xml_file)
        if has_permissions(xml_file, "USR", "R"):
            raise XMLError("Cannot read XML file.  Permission denied. " \
                           "XML file: %s" % xml_file)
        try:
            self._doc = libxml2.parseFile(xml_file)
        except Exception, ex:
            raise XMLError("Error parsing xml: %s" % str(ex))

        return self._doc

    def parse_string(self, xml_string):
        try:
            self._doc = libxml2.parseDoc(xml_string)
        except Exception, ex:
            raise XMLError("Error parsing xml: %s" % str(ex))

        return self._doc

    def parse_from_url(self, xml_url):
        try:
            response = urllib2.urlopen(xml_url)
            xml_string = response.read()
            self._doc = self.parse_string(xml_string)
        except Exception, ex:
            raise XMLError("Error parsing xml: %s" % str(ex))

        return self._doc

    def parse_xsl_file(self, xsl_file):
        try:
            self._style = libxslt.parseStylesheetFile(xsl_file)
        except Exception, ex:
            raise XMLError("Error parsing xsl: %s" % str(ex))

        return self._style

    def parse_xsl_string(self, xsl_string):
        try:
            # parse the stylesheet xml file into doc object
            styledoc = libxml2.parseDoc(xsl_string)
            # process the doc object as xslt
            self._style = libxslt.parseStylesheetDoc(styledoc)
        except Exception, ex:
            raise XMLError("Error parsing xsl: %s" % str(ex))

        return self._style

    def transform(self):
        try:
            result = self._style.applyStylesheet(self._doc, None)
            output = self._style.saveResultToString(result)
            result.freeDoc()
        except Exception, ex:
            raise XMLError("Error occurred during transform: %s" % str(ex))

        return output

    def free(self):
        self._doc.freeDoc()
        self._style.freeStylesheet()

    @property
    def getdoc(self):
        return self._doc

    @property
    def getstyle(self):
        return self._style
