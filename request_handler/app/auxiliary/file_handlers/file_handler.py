#!/usr/bin/env python
# coding: utf-8

from multiprocessing import Process, Manager
from app.auxiliary.transaction import transactional
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from app.auxiliary.file_handlers.parser import parseRow
from app.auxiliary.file_handlers.uploader import uploadRow
from flask import abort
from werkzeug.datastructures import FileStorage
from pandas import read_csv, errors
from io import StringIO
from ctypes import c_bool
from appconfig import NUM_PROCESSES


def parseRowsSingleProcess(file_ended, data_parsed, df_list, to_upload, fileid):

    def proxyData():
        while df_list:
            df = df_list.pop(0)
            values = parseRow(df, data_keys)
            values['fileid'] = fileid
            to_upload.append(values)

    data_schema = DataSchema()
    data_keys = data_schema.dump(Data()).data.keys()
    while not file_ended.value:
        proxyData()
    proxyData()
    data_parsed.value = True


def uploadDataSingleProcess(data_parsed, to_upload, upload_lock, values_lock):

    def uploadFromList():
        while to_upload:
            with values_lock:
                if to_upload:
                    values = to_upload.pop(0)
                else:
                    break
            uploadRow(values, data_schema, upload_lock)

    data_schema = DataSchema()
    while not data_parsed.value:
        uploadFromList()
    uploadFromList()


@transactional
def handleFile(fileid: int, file: FileStorage):
    str = StringIO(file.stream.readline().decode("utf-8"))
    if not str:
        abort(400)

    df = None
    try:
        df = read_csv(str, sep='[;,|]', engine="python", header=None)
    except errors.ParserError:
        abort(400)

    if df.empty:
        abort(400)
    index, title = next(df.iterrows())
    title = title.tolist()

    # НЕОБХОДИМО ОТПРОФИЛИРОВАТЬ И ОПТИМИЗИРОВАТЬ!-------------
    # Считываем данные
    import time
    preparation = time.perf_counter()
    file_ended = Manager().Value(c_bool, False)
    data_parsed = Manager().Value(c_bool, False)
    df_list = Manager().list()
    to_upload = Manager().list()
    upload_lock = Manager().Lock()
    values_lock = Manager().Lock()
    row_parse_process = Process(target=parseRowsSingleProcess, args=(file_ended,
                                                                     data_parsed,
                                                                     df_list,
                                                                     to_upload,
                                                                     fileid))
    row_parse_process.start()
    uploaders = []
    for i in range(NUM_PROCESSES-2 if NUM_PROCESSES > 2 else 1):
        uploader = Process(target=uploadDataSingleProcess, args=(data_parsed,
                                                                 to_upload,
                                                                 upload_lock,
                                                                 values_lock))
        uploaders.append(uploader)
        uploader.start()
    preparation = (time.perf_counter() - preparation) * 1000
    print(f"preparation: {preparation}")

    reading = time.perf_counter()
    str = StringIO(file.stream.readline().decode("utf-8"))
    while str:
        try:
            df = read_csv(str, sep='[;,|]', engine="python", names=title)
        except errors.ParserError:
            abort(400)
        if df.empty:
            break
        df_list.append(df)
        str = StringIO(file.stream.readline().decode("utf-8"))
    reading = (time.perf_counter() - reading) * 1000
    print(reading)

    file_ended.value = True

    row_parse_process.join()
    for uploader in uploaders:
        uploader.join()
    #------------------------------------------------------------
