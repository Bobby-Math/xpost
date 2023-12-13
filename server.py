from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import post 

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())

    def do_POST(self):
        if self.path == '/post-to-twitter':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            tweet_text = parse_qs(post_data)['tweetText'][0]

            with open("uni.txt",'w') as file:
                file.write(tweet_text)

            # Run your Python code to post on Twitter here
            
            # Replace the following print statement with your actual Twitter API integration code
            


            
            print('Tweet posted:', tweet_text)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response_message = '{"status": "success", "message": "Tweet posted successfully"}'
            self.wfile.write(response_message.encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Server running on http://localhost:8000')
    httpd.serve_forever()
