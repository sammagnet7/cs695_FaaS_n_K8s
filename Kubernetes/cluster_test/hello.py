from flask import Flask
app = Flask(__name__)


# Global variable to keep track of the count
route_count = 0

@app.route("/")
def hello():
    global route_count
    route_count += 1

    # Write the count to a file
    with open("route_count.txt", "w") as file:
        file.write("Access count: ")
        file.write(str(route_count))
        file.write("\n")

    return "Hello World!"