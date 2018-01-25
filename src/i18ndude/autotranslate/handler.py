# encoding: utf-8
from bs4.dammit import EntitySubstitution
from copy import copy
from i18ndude import untranslated, common, script
from utils import replace

import HTMLParser
import bs4 as BeautifulSoup
import sys
import xml.sax


class Handler(untranslated.NoSummaryVerboseHandler):

    def log(self, msg, severity):
        untranslated.Handler.log(self, msg, severity)
        print '%s:%s:%s:\n-%s- - %s' % (self._filename,
                                        self._parser.getLineNumber(),
                                        self._parser.getColumnNumber(),
                                        severity,
                                        msg)

    def startElement(self, tag, attrs):
        self._history.append([tag, attrs, ''])

        untranslated.attr_validator(tag, attrs, self.log)

        if 'i18n:translate' in attrs.keys():
            self._i18nlevel += 1
        elif self._i18nlevel != 0:
            self._i18nlevel += 1

    def endElement(self, tag):
        tag, attrs, data = self._history.pop()
        data = data.strip()

        if untranslated._translatable(data) and not untranslated._tal_replaced_content(tag, attrs):
            # not enclosed
            if (self._i18nlevel == 0) and tag not in [
                    'script', 'style', 'html']:
                severity = untranslated._severity(tag, attrs) or ''
                if severity:
                    if untranslated.IGNORE_UNTRANSLATED in attrs.keys():
                        # Ignore untranslated data. This is necessary for
                        # including literal content, that does not need to be
                        # translated.
                        pass
                    elif not untranslated.CHAMELEON_SUBST.match(data):
                        h = HTMLParser.HTMLParser()
                        with open(self._filename, 'r') as source_file:
                            bs = BeautifulSoup.BeautifulSoup(source_file, 'lxml')
                            source_file.close()
                        attr = {}
                        for key in attrs.keys():
                            if key not in ['selected']:
                                attr[key] = attrs.getValue(key)
                        values = bs.findAll(tag.lower(), attrs=attr)
                        if not values:
                            self.log(
                                'i18n:translate missing for this:\n'
                                '"""\n%s\n"""\nTag:<%s> Attrs:%s' % (data.encode('utf8'), tag, attr), severity)
                        for v in values:
                            if not v.has_attr('i18n:translate'):
                                v.name = tag
                                escaper = EntitySubstitution()
                                substitute = copy(v)
                                if v.string:
                                    substitute.string = escaper.substitute_html(v.string)
                                for i in [v, substitute]:
                                    pattern = h.unescape(str(i))
                                    i['i18n:translate'] = ""
                                    substring = h.unescape(str(i))
                                    match = replace(self._filename, str(pattern), str(substring), self._parser.getLineNumber())
                                    if match:
                                        break
                                if not match:
                                    self.log(
                                        'i18n:translate missing for this:\n'
                                        '"""\n%s\n"""\nPattern: %s' % (data.encode('utf8'), str(pattern)), severity)
        if self._i18nlevel != 0:
            self._i18nlevel -= 1


def find_untranslated(files):
    parser = xml.sax.make_parser(['expat'])
    # disable external validation to make it work without network access
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    parser.setFeature(xml.sax.handler.feature_external_pes, False)
    handler = Handler(parser)  # default
    parser.setContentHandler(handler)

    errors = 0
    for filename in script.filter_isfile(files):  # parse file by file
        with open(filename) as myfile:
            if not myfile.read().strip():
                continue
        # Reinitialize the handler, resetting errors.
        handler.set_filename(filename)
        file_errors = []
        success = False
        for content in common.present_file_contents(filename):
            if content is None:
                continue
            if isinstance(content, list):
                # These are errors.
                file_errors.extend(content)
                continue
            # Reinitialize the handler, resetting errors.
            handler.set_filename(filename)
            try:
                parser.parse(content)
            except KeyboardInterrupt:
                print >> sys.stderr, 'Interrupted by user.'
                sys.exit(1)
            except xml.sax.SAXException as error:
                file_errors.append(error)
                continue
            except Exception as error:
                file_errors.append(error)
                continue
            else:
                # We have successfully parsed the file.
                success = True
                # We can safely print the output.
                handler.show_output()
                # No need for a run with another parser.
                break
            finally:
                handler.clear_output()
        # Note that the error stats of the handler get reset to zero
        # when starting on a new document, so we ask about errors
        # after each document.
        if handler.has_errors():
            # So some untranslated strings were found.
            errors += 1
        if success:
            # next file
            continue
        if file_errors:
            errors += 1
            report = 'ERRORs found trying to parse document in various ways:\n'
            for error in file_errors:
                report += '%s\n' % error
            handler.log(report, 'FATAL')
    return errors
