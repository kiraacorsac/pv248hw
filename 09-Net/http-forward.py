import http.server
import http.client
import urllib.request as reqs
import urllib.error
import sys
import json

port = sys.argv[1]
#port = 80
target = sys.argv[2]
#target = "http://www.mocky.io/v2/5bfdae3931000063002cfaa7"

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError:
    return False
  return True
  

class ForwardingHandler(http.server.BaseHTTPRequestHandler):
        
    def do_common(self,time=1):
        try:
            response = reqs.urlopen(self.request, timeout)
            resp_data = response.read()
            resp_type, resp_data = ("json", json.loads(resp_data)) if is_json(resp_data) else ("content", resp_data.decode("utf-8"))
            
            self.ret_obj =  {
                "code": response.status,
                "headers": dict(response.getheaders()),
                resp_type: resp_data
            }
            response.close()

        except urllib.error.HTTPError as e:
            resp_data = e.read()
            resp_type, resp_data = ("json", json.loads(resp_data)) if is_json(resp_data) else ("content", resp_data.decode("utf-8"))
            self.ret_obj =  {
                "code": e.code,
                "headers": dict(e.headers._headers),
                resp_type: resp_data
            }

        

    def do_GET(self):
        heads = self.headers
        self.request = reqs.Request(target if target[7:] != "http://" else "http://" + target, #TODO: HTTP
            headers=self.headers,
            method="GET")

        try:
            self.do_common()
        except Exception as e:
            self.ret_obj = {"code": "timeout"}
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(json.dumps(self.ret_obj, ensure_ascii=False), "UTF-8"))
    
    def do_POST(self):
        in_json = self.rfile.read(int(self.headers['content-length']))
        if not is_json(in_json):
            self.ret_obj = {"code": "invalid json"}
        else:
            in_json = json.loads(in_json)
            if "url" not in in_json:
                self.ret_obj = {"code": "invalid json"}
            else:
                request = reqs.Request(in_json.url if "url" in in_json else target,
                    data=bytes(in_json.content if "content" in in_json else "", "UTF-8"),
                    headers=in_json.headers if "headers" in in_json else {},
                    method=in_json.type if "type" in in_json else "GET")
                try:
                    self.do_common(in_json.timeout if "timeout" in in_json else 1)
                except:
                    self.ret_obj = {"code": "timeout"}
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(json.dumps(self.ret_obj, ensure_ascii=False), "UTF-8"))
        

server = http.server.HTTPServer(("", port), ForwardingHandler)
server.serve_forever()

