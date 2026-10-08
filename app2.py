from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import psycopg


DB_HOST = "db"
DB_NAME = "appdb"
DB_USER = "appuser"
DB_PASSWORD = "password123"


def get_connection():
    return psycopg.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def initialize_database():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    message TEXT NOT NULL
                )
            """)


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/":
            self.show_home()

        elif self.path == "/data":
            self.show_data()

        else:
            self.send_error(404)

    def do_POST(self):

        length = int(self.headers["Content-Length"])
        body = self.rfile.read(length).decode()
        data = parse_qs(body)

        if self.path == "/add":

            message = data.get("message", [""])[0]

            if message.strip():
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO messages (message) VALUES (%s)",
                            (message,)
                        )

        elif self.path == "/update":

            message_id = data.get("id", [""])[0]
            message = data.get("message", [""])[0]

            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE messages SET message = %s WHERE id = %s",
                        (message, message_id)
                    )

        elif self.path == "/delete":

            message_id = data.get("id", [""])[0]

            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM messages WHERE id = %s",
                        (message_id,)
                    )

        self.send_response(303)
        self.send_header("Location", "/data")
        self.end_headers()

    def show_home(self):

        html = """
        <html>
        <body>

        <h1>Python + Docker + PostgreSQL</h1>

        <h2>Add Message</h2>

        <form method="POST" action="/add">

            <input
                type="text"
                name="message"
                placeholder="Type your message"
                size="50"
                required
            >

            <button type="submit">
                Save
            </button>

        </form>

        <br>

        <a href="/data">View Database</a>

        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def show_data(self):

        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    "SELECT id, message FROM messages ORDER BY id"
                )

                rows = cursor.fetchall()

        html = """
        <html>
        <body>

        <h1>PostgreSQL Database Contents</h1>

        <table border="1" cellpadding="10">

        <tr>
            <th>ID</th>
            <th>Message</th>
            <th>Update</th>
            <th>Delete</th>
        </tr>
        """

        for row in rows:

            html += f"""
            <tr>

                <td>{row[0]}</td>

                <td>{row[1]}</td>

                <td>
                    <form method="POST" action="/update">

                        <input type="hidden"
                               name="id"
                               value="{row[0]}">

                        <input type="text"
                               name="message"
                               value="{row[1]}"
                               required>

                        <button type="submit">
                            Update
                        </button>

                    </form>
                </td>

                <td>
                    <form method="POST" action="/delete">

                        <input type="hidden"
                               name="id"
                               value="{row[0]}">

                        <button type="submit">
                            Delete
                        </button>

                    </form>
                </td>

            </tr>
            """

        html += """
        </table>

        <br>

        <a href="/">Add another message</a>

        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())


initialize_database()

server = HTTPServer(("0.0.0.0", 9000), MyHandler)

print("Python server running on port 9000...")

server.serve_forever()
