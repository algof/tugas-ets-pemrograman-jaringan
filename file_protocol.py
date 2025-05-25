import json
import logging
import shlex
from file_interface import FileInterface

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()
    def proses_string(self,string_datamasuk=''):
        logging.warning(f"string diproses: {string_datamasuk}")
        c = string_datamasuk.split(" ", 2)
        try:
            if len(c) == 1:
                c_request = c[0]
                if c_request == "LIST":
                    cl = self.file.list()
                    return json.dumps(cl)
                else:
                    return dict(status="ERROR", data="UNKNOWN command")
            elif len(c) == 2:
                c_request = c[0]
                params = c[1]
                if c_request == "GET":
                    cl = self.file.get([params])
                elif c_request == "DELETE":
                    cl = self.file.delete([params])
                elif c_request == "DOWNLOAD":
                    cl = self.file.download([params])
                else:
                    return json.dumps(dict(status="ERROR", data="UNKNOWN command"))
                return json.dumps(cl)
            elif len(c) == 3:
                c_request = c[0].strip()
                if c_request == "UPLOAD":
                    filename = c[1]
                    params = ''.join(c[2:])
                    cl = self.file.upload([filename, params])
                else:
                    return json.dumps(dict(status="ERROR", data="UNKNOWN command"))
                return json.dumps(cl)
        except Exception:
            return json.dumps(dict(status='ERROR',data='request tidak dikenali'))


if __name__=='__main__':
    fp = FileProtocol()
    content = fp.proses_string("LIST")
    # content = fp.proses_string("GET pokijan.jpg")
    # content = fp.proses_string("DELETE donalbebek_1.jpg")
    print(content)
    # data = json.loads(content)
    # print(data)
    # print(data['data_file'])
    # content_2 = fp.proses_string(f"UPLOAD copypokijan_2.jpg {data['data_file']}")
    # print(content_2)