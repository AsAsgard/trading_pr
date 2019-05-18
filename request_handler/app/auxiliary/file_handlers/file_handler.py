#!/usr/bin/env python
# coding: utf-8

from app.auxiliary.transaction import transactional
from app.auxiliary.file_handlers.keys_normalizer import normalize_keys
from app.auxiliary.file_handlers.uploader import uploadToDB
from werkzeug.datastructures import FileStorage
from pandas import read_csv, errors
from io import StringIO


@transactional
def handleFile(fileid: int, filepath):
    with open(filepath, 'rb') as fp:
        file = FileStorage(fp)

        try:
            str = StringIO(file.stream.readline().decode("utf-8"))
        except UnicodeError:
            raise RuntimeError("Bad data encoding or type.")

        try:
            df = read_csv(str, sep='[;,|]', engine="python", header=None)
        except errors.ParserError:
            raise RuntimeError("Bad file format.")
        except errors.EmptyDataError:
            raise RuntimeError("No data to read.")

        if df.empty:
            raise RuntimeError("No data to read.")

        index, titles = next(df.iterrows())
        titles = titles.tolist()
        titles = normalize_keys(titles)

        # Считываем данные
        filedata = file.stream.read().decode('utf-8').replace(';', ',')\
                                                     .replace('|', ',')\
                                                     .replace('\t', ',')
        try:
            df = read_csv(StringIO(filedata), sep=',', names=titles)
        except errors.ParserError:
            raise RuntimeError("Error during parsing. Check the correctness of the data in file.")
        except errors.EmptyDataError:
            raise RuntimeError("No data to read.")

    if df.empty:
        raise RuntimeError("No data to read.")

    df['fileid'] = fileid
    uploadToDB(df)
