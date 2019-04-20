from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# import database config from database_setup.py
from database_setup import Restaurant, Base, MenuItem

# create a session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<a href='/restaurants/new'>Add a new restaurant</a>"
                output += "<br/>"
                output += "<h1>Restaurants:</h1>"
                output += "<ul>"
                for restaurant in session.query(Restaurant).all():
                    output += "<li><strong>%s</strong></li>" % restaurant.name
                    output += '''
                        <span>
                            <a href='/restaurants/%s/edit'>edit</a>
                        </span>''' % restaurant.id
                    output += '''
                        <span>
                            <a href='restaurants/%s/delete'>delete</a>
                        </span>''' % restaurant.id
                    output += "<br/><br/>"

                output += "</ul>"
                output += "</html></body>"

                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Add a new restaurant</h1>"
                output += '''
                    <form method='POST'
                          enctype='multipart/form-data'
                          action='/restaurants/new'>
                        <input name='newRestaurantName'
                               type='text'
                               placeholder='New restaurant name'/>
                        <input type='submit' value='Add'/>
                    </form>'''
                output += "</html></body>"

                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split('/')[2]
                oldRestaurantName = session.query(Restaurant)\
                    .filter_by(id=restaurantIDPath).one()

                if oldRestaurantName != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = ""
                    output += "<html><body>"
                    output += "<h1>%s</h1>" % oldRestaurantName.name 
                    output += '''<form method='POST'
                        enctype='multipart/form-data'
                        action='/restaurants/%s/edit'>''' % restaurantIDPath
                    output += '''<input name='editRestaurantName'
                        type='text'
                        placeholder='New restaurant name'/>'''
                    output += "<input type='submit' value='Change'/>"
                    output += "</form>"
                    output += "</html></body>"

                    self.wfile.write(output)
                    print output
                    return


            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split('/')[2]
                delRestaurantName = session.query(Restaurant)\
                    .filter_by(id=restaurantIDPath).one()
                print restaurantIDPath
                print delRestaurantName.name

                if delRestaurantName != []:
                    print 'in the response'
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = ""
                    output += "<html><body>"
                    output += '''<form method='POST'
                                       enctype='multipart/form-data'
                                       action='restaurants/%s/delete'>
                                       ''' % restaurantIDPath
                    output += "<h2>"
                    output += 'Are you sure you want to delete "%s"'\
                        % delRestaurantName.name
                    output += "</h2>"
                    output += "<input type='submit' value='Delete'>"
                    output += "</form>"
                    output += "</html></body>"

                    self.wfile.write(output)
                    print output
                    return


            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "" 
                output += "<html><body>"
                output += "<h1>Hello!</h1>"
                output += '''
                    <form method='POST'
                          enctype='multipart/form-data'
                          action='/hello'>
                        <h2>What would you like me to say?</h2>
                        <input name='message' type='text'>
                        <input type='submit' value='Submit'>
                    </form>
                '''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>&#161Hola</h1>"
                output += "<a href='/hello'>Back to Hello</a>"
                output += '''
                    <form method='POST'
                          enctype='multipart/form-data'
                          action='/hello'>
                        <h2>What would you like me to say?</h2>
                        <input name='message' type='text'>
                        <input type='submit' value='Submit'>
                    </form>
                '''
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, 'File not found %s' % self.path)


    def do_POST(self):
        try:
            if self.path.endswith('/restaurants/new'): 
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type')
                )

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                    return

            if self.path.endswith('/edit'):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type')
                )

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('editRestaurantName')
                    restaurantIDPath = self.path.split('/')[2]

                    editRestaurant = session.query(Restaurant)\
                        .filter_by(id=restaurantIDPath).one() 
                    if editRestaurant != []:
                        editRestaurant.name = messagecontent[0]
                        session.add(editRestaurant)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
                        return

            if self.path.endswith('/delete'):
                restaurantIDPath = self.path.split('/')[2]
                delRestaurantName = session.query(Restaurant)\
                    .filter_by(id=restaurantIDPath).one()
                if delRestaurantName != []:
                    session.delete(delRestaurantName)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                    return


            # self.send_response(301)
            # self.send_header('Content-type', 'text/html')
            # self.end_headers()

            # ctype, pdict = cgi.parse_header(
            #     self.headers.getheader('content-type'))
            # if ctype == 'multipart/form-data':
            #     fields = cgi.parse_multipart(self.rfile, pdict)
            #     messagecontent = fields.get('message')

            # output = ""
            # output += "<html><body>"
            # output += "<h2>Okay, how about this: </h2>"
            # output += "<h1> %s </h1>" % messagecontent[0]

            # output += '''
            #     <form method='POST'
            #           enctype='multipart/form-data'
            #           action='/hello'>
            #         <h2>What would you like me to say?</h2>
            #         <input name='message' type='text'/>
            #         <input type='submit' value='Submit'/>
            #     </form>
            # '''
            # output += "</body></html>"

            # self.wfile.write(output)
            # print output

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webServerHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()


if __name__ == '__main__':
    main()
