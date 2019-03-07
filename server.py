import SocketServer, SimpleHTTPServer, requests, sqlite3, sys

class Reply(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        database = "reg.db"
        conn = sqlite3.connect(database)
        c = conn.cursor()
        if self.path == '/':
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        else:
        # with conn:
        #     c.execute('''CREATE TABLE IF NOT EXISTS counts (
        #                     dept VARCHAR(10) PRIMARY KEY,
        #                     counter INT
        #                 );''')

        # The query arrives in self.path.  The following line just echoes the query;
        # replace it with code that generates the desired response.
        # self.wfile.write("query was %s\n" % self.path) # replace this line
            split_query = self.path.split("/")
            dep_code = self.path[1:]
            course_code = ""
            if len(dep_code) != 3:
                dep_code = dep_code[:3]
                course_code = self.path[5:]
            subj_list = all['term'][0]['subjects']
            success = 0
            i = 0
            while (i < len(subj_list)):
            # dictionary = subj_list[i]
            # self.wfile.write(subj_list[i]['code'].lower() + "\n")
                if subj_list[i]['code'].lower() == dep_code.lower():
                    dictionary = subj_list[i]['courses']
                    j = 0
                    while j < len(dictionary):
                        if len(course_code) == 0:
                            self.wfile.write(dep_code.upper() + "\t")
                            self.wfile.write(dictionary[j]['catalog_number'] + "\t")
                            self.wfile.write(dictionary[j]['title'] + "\n")
                            success = 1
                        elif dictionary[j]['catalog_number'] == course_code:
                            self.wfile.write(dep_code.upper() + "\t")
                            self.wfile.write(dictionary[j]['catalog_number'] + "\t")
                            self.wfile.write(dictionary[j]['title'] + "\n")
                            success = 1
                        j += 1
                i += 1
            if success == 1:
                with conn:
                    c.execute("SELECT * FROM counts WHERE dept = :dept", {'dept': dep_code.upper()})
                    ret_list = c.fetchall()
                    if len(ret_list) == 0:
                        c.execute('INSERT INTO counts VALUES (?, ?)', (dep_code.upper(), 1))
                        conn.commit()
                    else:
                        update_val = ret_list[0][1]
                        update_val += 1
                        c.execute('''UPDATE counts SET counter = :counter
                                WHERE dept = :dept''', {'dept': dep_code.upper(),
                                'counter': update_val})
                        conn.commit()
            if split_query[1].lower() == "clear" and len(split_query) == 2:
                with conn:
                    c.execute('DELETE FROM counts')
            if split_query[1].lower() == "clear" and len(split_query) == 3:
                with conn:
                    c.execute('DELETE FROM counts WHERE dept = :dept',
                          {'dept': split_query[2].upper()})
            if split_query[1].lower() == "count" and len(split_query) == 2:
                with conn:
                    c.execute('SELECT * FROM counts')
                    all_counts = c.fetchall()
                    # self.wfile.write(all_counts)
                    for row in all_counts:
                        self.wfile.write(row[0])
                        self.wfile.write(" ")
                        self.wfile.write(row[1])
                        self.wfile.write("\n")
            if split_query[1].lower() == "count" and len(split_query) == 3:
                with conn:
                    c.execute("SELECT * FROM counts WHERE dept = :dept",
                          {'dept': split_query[2].upper()})
                    ret_list = c.fetchall()
                    if len(ret_list) != 0:
                        self.wfile.write(ret_list[0][0])
                        self.wfile.write(" ")
                        self.wfile.write(ret_list[0][1])
                        self.wfile.write("\n")
                    else:
                        self.wfile.write(split_query[2].upper())
                        self.wfile.write(" ")
                        self.wfile.write("0")
            if success == 0:
                self.wfile.write("\n")
                    # self.wfile.write(ret_list)



        # c.execute('INSERT INTO counts VALUES (?, ?)', (dep_code.upper(), 1))
        # conn.commit()
        # c.execute("SELECT * FROM counts WHERE dept = :dept", {'dept': dep_code.upper()})
        # conn.commit()
        # self.wfile.write(c.fetchall())


        # self.wfile.write(all['term'][0]['subjects'][0]['courses'][0]['catalog_number'] + '\n')
        # self.wfile.write(all['term'][0]['reg_name'])
        # self.wfile.write(all['term'][0]['subjects'])
        # self.wfile.write(all['term'][0]['subjects'][0]['code'])

all = []

def get_OIT(url):
    r = requests.get(url)
    if r.status_code != 200:
        return ["bad json"]
    return r.json()

def main():
    global all
    # Read OIT feed before starting the server.
    oit = 'http://etcweb.princeton.edu/webfeeds/courseofferings/?fmt=json&term=current&subject=all'
    all = get_OIT(oit)
    print("server is listening on port " + sys.argv[1])
    SocketServer.ForkingTCPServer(('', int(sys.argv[1])), Reply).serve_forever()

main()