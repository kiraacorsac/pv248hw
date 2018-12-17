import http.server
import http.client
import urllib.request as reqs
import urllib.error
import socket
import sys
import json

port = int(sys.argv[1])
#port = 80
target = sys.argv[2]
#target = "http://www.mocky.io/v2/5bfdae3931000063002cfaa7"

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
    return "url" in json_object and not(json_object.type == "POST" and "content" not in json_object)

  except ValueError:
    return False  

class ForwardingHandler(http.server.BaseHTTPRequestHandler):

    def do_common(self,timeout):
        try:
            response = reqs.urlopen(self.request, timeout)
            resp_data = response.read().decode("utf-8")
            resp_type, resp_data = ("json", json.loads(resp_data)) if is_json(resp_data) else ("content", resp_data)
            
            self.ret_obj =  {
                "code": response.status,
                "headers": dict(response.getheaders()),
                resp_type: resp_data
            }
            response.close()

        except urllib.error.HTTPError as e:
            resp_data = e.read().decode("utf-8")
            resp_type, resp_data = ("json", json.loads(resp_data)) if is_json(resp_data) else ("content", resp_data)
            self.ret_obj =  {
                "code": e.code,
                "headers": dict(e.headers._headers),
                resp_type: resp_data
            }

        

    def do_GET(self):
        heads = dict(self.headers)
        heads['Accept-Encoding'] = 'identity'

        self.request = reqs.Request(
            target if target[7:] == "http://" else "http://" + target, #TODO: HTTP
            headers=heads,
            method="GET")

        try:
            self.do_common(1)
        except socket.timeout as e:
            self.ret_obj = {"code": "timeout"}
        
        response_data = json.dumps(self.ret_obj, ensure_ascii=False)

        self.send_response(200)
        self.send_header('Connection', 'close')
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_data)))
        self.end_headers()
        self.wfile.write(bytes(response_data, "utf-8"))
    
    def do_POST(self):
        if 'content-length' in self.headers:
            in_json = self.rfile.read(int(self.headers['content-length'])).decode("utf-8")
        else:
            in_json = ""

        if not is_json(in_json):
            self.ret_obj = {"code": "invalid json"}
        else:
            in_json = json.loads(in_json)
            self.request = reqs.Request(in_json.url,
                data=bytes(in_json.content if "content" in in_json else "", "utf-8"),
                headers=in_json.headers if "headers" in in_json else {},
                method=in_json.type if "type" in in_json else "GET")
            try:
                self.do_common(in_json.timeout if "timeout" in in_json else 1)
            except socket.timeout as e:
                self.ret_obj = {"code": "timeout"}
        response_data = json.dumps(self.ret_obj, ensure_ascii=False)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_data)))
        self.end_headers()
        self.wfile.write(bytes(response_data, "utf-8"))
        

server = http.server.HTTPServer(("", port), ForwardingHandler)
server.serve_forever()

