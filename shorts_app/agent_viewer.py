"""Read-only output viewer; all creative edits happen in the agent conversation."""
import json
import mimetypes
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,unquote
from .model import ROOT


def start_viewer(workspace,port=4319):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            if self.headers.get('Host') not in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'):
                self.send_error(403);return
            path=unquote(urlsplit(self.path).path)
            if path=='/api/projects':
                raw=json.dumps(workspace.list(),ensure_ascii=False).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
            if path=='/':target=ROOT/'agent_viewer/index.html'
            elif path.startswith('/media/'):
                target=(workspace.root/path[7:]).resolve()
                if not target.is_relative_to(workspace.root.resolve()) or target.suffix not in ('.mp4','.png','.srt') or '/renders/' not in str(target):self.send_error(403);return
            else:self.send_error(404);return
            if not target.is_file():self.send_error(404);return
            size=target.stat().st_size;start=0;end=size-1
            request=self.headers.get('Range')
            if request:
                import re
                match=re.fullmatch(r'bytes=(\d+)-(\d*)',request)
                if not match:self.send_error(416);return
                start=int(match[1]);end=min(int(match[2]) if match[2] else end,end)
                if start>end:self.send_error(416);return
            self.send_response(206 if request else 200);self.send_header('Content-Type',mimetypes.guess_type(target.name)[0] or 'application/octet-stream');self.send_header('Accept-Ranges','bytes');self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(end-start+1))
            if request:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.end_headers()
            with target.open('rb') as f:
                f.seek(start);left=end-start+1
                while left:
                    chunk=f.read(min(65536,left))
                    if not chunk:break
                    try:self.wfile.write(chunk)
                    except (BrokenPipeError,ConnectionResetError):break
                    left-=len(chunk)
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    import threading
    threading.Thread(target=server.serve_forever,daemon=True).start()
    return server
