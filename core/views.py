from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from .models import *
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Create your views here.

adminpassword = "hello"

session_open = False


def index(request):
    return render(request, "index.html")


def login(request):

    if request.method == "POST":
        password = request.POST.get("password")

        if password == adminpassword:
            request.session["logged-in"] = True
            return redirect("/admin")

        else:
            return render(request, "admin.html", {"wrong":True})

    if request.session.get("logged-in"):
        return redirect("/admin")

    return render(request, "admin-login.html")


def admin(request):

    if not request.session.get("logged-in"):
        return redirect("/admin/login")

    contestants = Contestants.objects.all()

    return render(request, "admin.html", {"contestants":contestants, "open":session_open})



def addContenstant(request):

    if request.method == "POST":
        name = request.POST.get("name").title().strip()
        position = request.POST.get("position").title()
        photo = request.FILES.get("image")

        try:
            res = Contestants.objects.get(name=name)
            return render(request, "add.html", {"exists":True})

        except:
            pass

        last = None

        try:
            last = Contestants.objects.all().last().id + 1
        except:
            last = 1

        contestant = Contestants.objects.create(id=last, name=name, position=position, votes=0)

        contestant.save()

        contestantinst = Contestants.objects.get(id=last)

        contestantinst.photo = photo

        contestantinst.save()

        return render(request, "add.html", {"added":True})


    if not request.session.get("logged-in"):
        return redirect("/admin")

    return render(request, "add.html")

def delete(request):
    if request.method == "POST":
        id = int(request.POST.get('id'))

        res = Contestants.objects.get(id=id)

        current = os.getcwd()

        print(current)

        os.remove(current + res.photo.url)

        res.delete()

        return redirect("/admin")


def votingForm(request):
    headboys = Contestants.objects.all().filter(position="Headboy")
    headgirls = Contestants.objects.all().filter(position="Headgirl")
    sportsboys = Contestants.objects.all().filter(position="Sports Captain Boy")
    sportsgirls = Contestants.objects.all().filter(position="Sports Captain Girl")

    return render(request, "vote.html", {"headboys" : headboys, "headgirls" : headgirls, "sportsboys" : sportsboys, "sportsgirls" : sportsgirls})

def votingFormMobile(request):
    headboys = Contestants.objects.all().filter(position="Headboy")
    headgirls = Contestants.objects.all().filter(position="Headgirl")
    sportsboys = Contestants.objects.all().filter(position="Sports Captain Boy")
    sportsgirls = Contestants.objects.all().filter(position="Sports Captain Girl")

    return render(request, "vote-mobile.html", {"headboys" : headboys, "headgirls" : headgirls, "sportsboys" : sportsboys, "sportsgirls" : sportsgirls})


def generateToken():
    import random
    chars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "_", ]

    special = ""

    for i in range(128):
        special += random.choice(chars)

    return special


def details(request):
    if request.method == "POST":
        email = request.POST.get("email") + "@jsspsdubai.com"

        x = Votes.objects.all().filter(email=email)

        if len(x) > 0:
            return render(request, "message.html", {"error":"done"})

        from datetime import date

        token = generateToken()

        email_sender = "jsspsvoting@gmail.com"
        email_password = "kivilaopxbwdkish"
        email_reciever = email

        subject = "Verify your Email to Register Your Vote"

        html  = f"""
            <a href="http://127.0.0.1:8000/email/verify/?token={token}">Click here</a> to verify email.
            PLEASE DO NOT OPEN IF YOU DID NOT GIVE THE DETAILS FOR RECEIVING THIS EMAIL.
        """

        body = MIMEMultipart()

        body.attach(MIMEText(html, "html"))

        body["From"] = email_sender
        body["To"] = email_reciever
        body["Subject"] = subject
        #em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_reciever, body.as_string())

        request.session["email"] = email
        request.session["date"] = str(date.today())
        request.session["verify"] = token

        return redirect("/email/sent/")

    return render(request, "details.html")

def submitVote(request):
    if request.method == 'POST':

        if not request.session.get("verified"):
            return render(request, "message.html", {"error":"na"})

        headboy = request.POST.get("headboy")
        headgirl = request.POST.get("headgirl")
        sportsboy = request.POST.get("sportsboy")
        sportsgirl = request.POST.get("sportsgirl")
        date = request.session["date"]
        email = request.session["email"]

        if not headboy or not headgirl or not sportsboy or not sportsgirl:
            return render(request, "message.html")

        if not session_open:
            return render(request, "message.html", {"error":"closed"})

        #x = Votes.objects.all().filter(student=student)
#
        #if len(x) > 0:
        #    return render(request, "message.html", {"error":"done"})

        x = Votes.objects.all().filter(email=email)

        if len(x) > 0:
            return render(request, "message.html", {"error":"done"})

        positions = [headboy, headgirl, sportsboy, sportsgirl]

        for i in positions:
            inst = Contestants.objects.get(name=i)
            Votes(contestant=inst, email=email).save()
            inst.votes += 1
            inst.save()

            from datetime import date

            History(email=email, contestant_name=inst.name, position=inst.position, date=date.today()).save()

        request.session["verified"] = None

        return render(request, "thank you.html")

    return HttpResponse("Invalid request")

def emailSent(request):

    email = request.session["email"]

    if not email:
        return render(request, "sent.html", {"email":"na"})

    return render(request, "sent.html", {"email":email})

def verifyEmail(request):

    if not session_open:
        return render(request, "message.html", {"error":"closed"})

    token = request.GET.get("token")

    #votes = request.session["votes"]
    #email = request.session["email"]
    #jssid = request.session["jssid"]
    #date_obj = request.session["date"]
    verification_token = request.session["verify"]

    if token != verification_token:
        request.session["email"] = None
        request.session["jssid"] = None
        request.session["date"] = None
        request.session["verify"] = None
        return render(request, "message.html", {"error":"token"})

    else:
        request.session["verified"] = True

    return redirect("/voting/form/")


def resetVotes(request):
    if request.method == "POST":
        res = Contestants.objects.all()

        for i in res:
            i.votes = 0
            i.save()

        Votes.objects.all().delete()

        return redirect("/admin")

    return redirect("/admin")


def deleteAll(request):
    if request.method == "POST":
        res = Contestants.objects.all()

        current = os.getcwd()

        for i in res:
            os.remove(current + i.photo.url)
            i.delete()

        return redirect("/admin")


def createCSV(request):
    votes = Votes.objects.all()
    import os

    root_dir = os.path.join(os.getcwd(), "assets")

    fh = open(os.path.join(root_dir, "votes.csv"), "w")
    data = "S.No, Email, Name of contestant, Position\n"
    #fh.write("S.No, Name of student, JSSID, Grade, Name of contestant, Position\n")

    count = 0

    for i in votes:
        count += 1
        data += f"{count}, {i.email}, {i.contestant.name}, {i.contestant.position}\n"
        #fh.write(line)

    fh.write(data)
    fh.close()


    fh = open(os.path.join(root_dir, "results.csv"), "w")
    data = "S.No, Name of contestant, Position, No. of votes\n"
    #fh.write("S.No, Name of contestant, Position, No. of votes\n")

    count = 0

    contestants = Contestants.objects.all()

    for i in contestants:

        count += 1

        data += f"{count}, {i.name}, {i.position}, {i.votes}\n"

    fh.write(data)

    fh.close()

    return JsonResponse({"created":True})


def openVoting(request):
    global session_open
    session_open = True

    return redirect("/admin")

def closeVoting(request):
    global session_open
    session_open = False

    return redirect("/admin")


def logout(request):
    del request.session["logged-in"]

    return redirect("/admin/login")

