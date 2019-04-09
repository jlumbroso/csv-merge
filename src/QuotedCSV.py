"""
csv_reader.py

Author: Jeremie Lumbroso
Date Created: March 13th, 2016
Date Updated: July 28th, 2018

Description: Reads CSV data in quoted format
and returns it as a list of dictionaries.
"""

import csv
try:
    from io import StringIO  # Python 3
except ImportError:
    # import StringIO  # Python 2
    pass


def comment_stripper(line_iterator, comment_line_chars='#;'):
    for line in line_iterator:
        stripped_line = line.strip()
        if not stripped_line:
            # empty lines
            continue
        # look at first character
        if stripped_line[:1] in comment_line_chars:
            # lines that are commented out
            continue
        # yield line with quotes escaped
        yield line.replace('\\', '\\\\').replace('""', '\\"')


class QuotedCSV(csv.Dialect):
    def __init__(self):
        self.delimiter = ','
        self.doublequote = False
        self.escapechar = '\\'
        self.lineterminator = '\n'
        self.quotechar = '"'
        self.quoting = csv.QUOTE_MINIMAL
        self.skipinitialspace = True
        self.strict = True


def read_csv(filename="", stream=None, as_dict=False):
    close_at_end = False
    if stream == None:
        close_at_end = True
        stream = open(filename, 'r')
    if as_dict:
        reader = csv.DictReader(comment_stripper(stream),
                                dialect=QuotedCSV())
    else:
        reader = csv.reader(comment_stripper(stream),
                            dialect=QuotedCSV())
    rows = [row for row in reader]
    if close_at_end:
        stream.close()
    return rows
