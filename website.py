import requests
import random
from flask import *
from groups import *
from message import *
from user import *
app = Flask(__name__)
app.secret_key = "b'\xd13\x05s\x9d\xb6\r\x85\xa6q\xf1\xfc\xbd#\x19\xaeL\xb2\xb5\xbe`\xae\xa1\xb1'"


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/loginrequest", methods=["POST"])
def loginRequest():
    response = requests.post("http://127.0.0.1:5000/login", json=request.form)
    if response.json()["result"] < 0:
        return "login failed smh"
    session["user_id"] = response.json()["result"]
    return "yay"

@app.route("/home")
def home():
    data = requests.get("http://127.0.0.1:5000/groups")
    groups = []
    for d in data.json():
        groups.append(Groups(d["id"], d["name"], d["description"], d["image"], d["created_time"]))
    data = requests.get("http://127.0.0.1:5000/users")
    users = []
    other = request.args.get("other")
    isGroup = request.args.get("isGroup")
    if isGroup == None or isGroup == "False":
        isGroup = False
    else:
        isGroup = True
    user_id = session["user_id"]
    for u in data.json():
        if user_id != u["id"]:
            if other == None:
                other = u["id"]
            users.append(User(u["id"], u["username"], u["password"], u["image"], u["createdTime"]))
    messages = []
    if not isGroup:
        data = requests.post("http://127.0.0.1:5000/messages", json={"user1": user_id, "user2": other})
        for d in data.json():
            messages.append(Message(d["id"], d["username"], d["userImage"], d["message"], d["time"]))
    else:
        data = requests.post("http://127.0.0.1:5000/groupmessage", json={"groupId": other})
        for d in data.json():
            messages.append(Message(d["id"], d["username"], d["userImage"], d["message"], d["time"]))
    a = 0
    if isGroup:
        a = 1
    return render_template("home.html", users=users, messages=messages, other=int(other), groups=groups, isGroup=a)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/registerrequest", methods=["POST"])
def registerRequest():
    session["username"] = request.form["username"]
    session["password"] = request.form["password"]
    code = ""
    for i in range(6):
        code += str(random.randint(0, 9))
    session["passcode"] = code
    d = request.form.to_dict()
    d["passcode"] = code
    response = requests.post("http://127.0.0.1:5000/verify", json=d)
    if response.json()["result"] == -1:
        return "User Already Taken :("
    elif response.json()["result"] == -2:
        return "Passwords don't Match SMH"
    return "yay"

@app.route("/verifyrequest", methods=["POST"])
def verifyRequest():
    code = request.form["passcode"]
    if code == session["passcode"]:
        response = requests.post("http://127.0.0.1:5000/register", json={"username": session["username"], "password": session["password"]})
        if response.json()["result"] > 0:
            return "yay"
    return "Incorrect Passcode"

@app.route("/verify")
def verify():
    return render_template("verify.html")


@app.route("/message", methods=["POST"])
def message():
    isGroup = request.form["isGroup"]
    print(isGroup)
    print(isGroup + "woof")
    if isGroup == "0":
        d = request.form.to_dict()
        d["user1"] = session["user_id"]
        response = requests.post("http://127.0.0.1:5000/send", json=d)
    else:
        response = requests.post("http://127.0.0.1:5000/sendgroupmessage", json={"groupId": request.form["user2"], "userId": session["user_id"], "message": request.form["message"]})
    return "yay"

@app.route("/creategrouppage")
def createGroupPage():
    return render_template("createGroup.html")

@app.route("/creategroup", methods=["POST"])
def createGroup():
    d = request.form.to_dict()
    data = requests.post("http://127.0.0.1:5000/creategroup", json=d)
    return "yay"

@app.route("/settings")
def settings():
    id = session["user_id"]
    data = requests.get("http://127.0.0.1:5000/user/" + str(id))
    data = data.json()
    print(data)
    user = User(data["id"], data["username"], data["password"], data["image"], data["createdTime"])
    return render_template("settings.html", user=user)

@app.route("/updateUser", methods=["POST"])
def updateUser():
    id = session["user_id"]
    data = requests.get("http://127.0.0.1:5000/user/" + str(id))
    data = data.json()
    username = ""
    image = ""
    oldPassword = ""
    newPassword = ""
    if "username" in request.form:
        username = request.form["username"]
    if "image" in request.form:
        image = request.form["image"]
    if "oldPassword" in request.form:
        oldPassword = request.form["oldPassword"]
    if "newPassword" in request.form:
        newPassword = request.form["newPassword"]
    print("meow!!!", oldPassword)


    if username == "" and newPassword == "" and image == "":
        return "Wow There is Nothing to Update"
    if oldPassword != data["password"]:
        return "Old Password Doesn't Match"
    requests.post("http://127.0.0.1:5000/updateuserdata", json={"newPassword": newPassword, "username": username, "image": image, "userId": id})
    return "yay"

app.run(port=5001)