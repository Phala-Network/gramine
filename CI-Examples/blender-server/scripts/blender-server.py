#!/usr/bin/env python3

import os
import sys
import subprocess
from http.server import SimpleHTTPRequestHandler, HTTPServer

BLENDER = '/blender/blender'


class RenderingRequestHandler(SimpleHTTPRequestHandler):
    def respond(self, code, message, body):
        self.send_response(code, message)
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def do_PUT(self):
        input_dir = os.path.join('/data', 'scenes')
        output_dir = os.path.join('/data', 'images')
        if not os.path.exists(input_dir):
            os.mkdir(input_dir)

        filename = os.path.basename(self.path)
        extension = os.path.splitext(filename)[-1]
        fileapth = os.path.join(input_dir, filename)
        if extension != '.blend':
            self.respond(415, 'Unsupported Media Type', 'Only .blend is supported\n')
            return

        file_length = int(self.headers['Content-Length'])
        with open(fileapth, 'wb') as output_file:
            output_file.write(self.rfile.read(file_length))

        print("file uploaded", flush=True)

        blender = subprocess.Popen([BLENDER, '-b', fileapth,
                          '-t', '4',
                          '-F', 'PNG',
                          '-o', os.path.join(output_dir, filename),
                          '-f', '1'])
        blender.wait()
        print("render finished", flush=True)

        self.respond(201, 'Created', 'Saved "%s"\n' % filename)


def main(argv):
    if len(argv) != 2:
        print(f'Usage: {argv[0]} <PORT>', file=sys.stderr)
        return 1

    if not os.path.exists(BLENDER):
        print('Blender not found', file=sys.stderr)
        return 1

    port = int(argv[1])
    srv = HTTPServer(('localhost', port), RenderingRequestHandler)
    srv.serve_forever()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
