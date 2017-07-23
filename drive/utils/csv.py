import collections
import csv

class CSVWriter(object):
    def __init__(self,
                 fp,
                 fieldnames=None,
                 headers=None,
                 missing='',
                 **kwargs):
        self.fp = fp
        if headers is None:
            headers = fieldnames
        self.fieldnames = fieldnames
        self.headers = headers
        if headers is not None and len(self.fieldnames) != len(self.headers):
            raise ValueError(
                'must have the same number of fieldnames as headers')
        self.missing = missing

        kwargs.setdefault('dialect', csv.excel)
        self.writer = csv.writer(fp, **kwargs)

    def writecomment(self, comment):
        lines = ['# ' + c.rstrip() for c in comment.strip().split('\n')]
        for line in lines:
            line = str(line)
            self.fp.write(line + '\r\n')

    def writeheader(self):
        if self.headers is not None:
            self.writerow(self.headers)

    def _dict_to_list(self, rowdict):
        return [
            rowdict.get(key, self.missing)
            for key in self.fieldnames
        ]

    def writerow(self, row):
        if isinstance(row, collections.Mapping):
            row = self._dict_to_list(row)
        elif self.fieldnames and len(self.fieldnames) != len(row):
            raise ValueError(
                'row does not contain the exact number of fields')
        row = [
            str(item if item is not None else self.missing)
            for item in row
        ]
        self.writer.writerow(row)
