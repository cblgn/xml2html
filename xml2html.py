#!/usr/bin/env python

import argparse
import os
import pystache
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from xml.dom.minidom import getDOMImplementation, parseString

class TestDefinition():

    def __init__(self, filepath):
        self.path = filepath
        self.title = None
        self.document = None
        self.tags = ['Priority', 'Category', 'Requirement', 'Configuration', 'Description']
        self.definition = { t : None for t in self.tags }
        self._load()

    def _load(self):
        try:
            self.document = minidom.parse(self.path)
        except (IOError, ExpatError):
            pass

    def _extract(self, tag_name):
        try:
            key = tag_name.lower()
            value = self.document.getElementsByTagName(tag_name)[0].firstChild.nodeValue.strip()
            self.definition[key] = value
        except (ValueError, KeyError, AttributeError):
            pass

    def get_title(self):
        try:
            test_node = self.document.getElementsByTagName('Test')[0]
            self.title = test_node.attributes['title'].value
            return True
        except (ValueError, KeyError, AttributeError):
            return False

    def get_definition(self):
        for t in self.tags:
            self._extract(t)
        return True

    def parse(self):
        if self.get_title():
            return self.get_definition()

    def serialize(self):
        data = self.definition
        data['title'] = self.title
        data['file'] = self.path
        return data

test_tpl = """
<tr>
<td class="small"><a href="{{file}}">{{ title }}</td>
<td class="small">{{ description }}</td>
</tr>
"""

main_tpl = """
<html>
  <head>
    <link rel="stylesheet" href="http://netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">
  </head>
  <body>
    <div class="well">
      <table class="table table-responsive table-striped table-hover table-bordered table-condensed">
	<thead>
          <tr>
            <th><span class="glyphicon glyphicon-file"></span> Test</th>
            <th><span class="glyphicon glyphicon-comment"></span> Description</th>
          </tr>
	</thead>
	<tbody>
          {{#tests}}
          {{ > test_tpl }}
          {{/tests}}
	</tbody>
      </table>
    </div>
  </body>
</html>
"""

def inspect(directory):
    tests = []
    for dirpath, dirnames, filenames in os.walk(args.directory):
        dirnames.sort()
        filenames.sort()
        for f in filenames:
            path = os.path.join(dirpath, f)
            test = TestDefinition(path)
            if test.parse():
               tests.append(test)

    return tests

def html_serialize(tests, output_filepath):
    with open(output_filepath, 'w') as o:
        renderer = pystache.Renderer(partials={'test_tpl': test_tpl})
        o.write(renderer.render(main_tpl, {'tests': [t.serialize() for t in tests]}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', default=os.getcwd())
    parser.add_argument('-o', '--output', default='output.html')
    args = parser.parse_args()

    tests = inspect(args.directory)
    html_serialize(tests, args.output)
