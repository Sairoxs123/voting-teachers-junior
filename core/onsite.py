from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from .models import *
import os

# Create your views here.

adminpassword = "hello"

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

    return render(request, "admin.html", {"contestants":contestants, "open":request.session.get("open")})



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

def submitVote(request):
    if request.method == 'POST':
        headboy = request.POST.get("headboy")
        headgirl = request.POST.get("headgirl")
        sportsboy = request.POST.get("sportsboy")
        sportsgirl = request.POST.get("sportsgirl")
        jssid = request.POST.get("jssid").upper()
        date = request.POST.get("date")

        letters = 0
        numbers = 0

        for i in jssid:
            if i.isdigit():
                numbers += 1

            if i.isalpha():
                letters += 1

        jssid = "JSSPS" + jssid

        if letters != 1 or numbers != 4:
            return render(request, "message.html", {"error":"jssid"})

        try:
            student = Students.objects.get(jssid=jssid)

        except:
            return render(request, "message.html", {"error":"jssid"})

        if not headboy or not headgirl or not sportsboy or not sportsgirl or not jssid:
            return render(request, "message.html")

        if not request.session.get("open"):
            return render(request, "message.html", {"error":"closed"})

        x = Votes.objects.all().filter(student=student)

        if len(x) > 0:
            return render(request, "message.html", {"error":"done"})

        positions = [headboy, headgirl, sportsboy, sportsgirl]

        for i in positions:
            inst = Contestants.objects.get(name=i)
            Votes(student=student, contestant=inst).save()
            inst.votes += 1
            inst.save()

            from datetime import date

            History(jssid=student.jssid, student_name=student.name, contestant_name=inst.name, position=inst.position, date=date.today()).save()

        return render(request, "thank you.html")

    return HttpResponse("Invalid request")


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
    data = "S.No, Name of student, JSSID, Grade, Name of contestant, Position\n"
    #fh.write("S.No, Name of student, JSSID, Grade, Name of contestant, Position\n")

    count = 0

    for i in votes:
        count += 1
        data += f"{count}, {i.student.name}, {i.student.jssid}, {i.student.grade_sec.strip()}, {i.contestant.name}, {i.contestant.position}\n"
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


def saveStudentsData(request):

    Students.objects.all().delete()

    fh = open("STUDENT DATA.csv", 'r')

    data = fh.readlines()

    grades = {
        "junior": [],
        #"middle": [],
        #"high": []
    }

    junior = ["I", "II", "III", "IV", "V"]
    #middle = ["VI", "VII", "VIII"]
    #high = ["IX", "X", "XI", "XII"]

    for i in data:
        tokens = i.split(",")

        if tokens[3] in junior:
            grades["junior"].append(
                {"name":tokens[1], "jssid":tokens[0], "class":tokens[3] + tokens[4]}
            )
    #
        #if tokens[3] in middle:
        #    grades["middle"].append(
        #        {"name":tokens[1], "jssid":tokens[0], "class":tokens[3] + tokens[4]}
        #    )

        #if tokens[3] in high:
        #    grades["high"].append(
        #        {"name":tokens[1], "jssid":tokens[0], "class":tokens[3] + tokens[4]}
        #    )

    for i in grades["junior"]:
        Students(name=i["name"], jssid=i["jssid"], grade_sec=i["class"]).save()

    fh.close()

    return JsonResponse({"created":True})


def openVoting(request):
    request.session["open"] = True

    return redirect("/admin")

def closeVoting(request):
    request.session["open"] = False

    return redirect("/admin")


def logout(request):
    del request.session["logged-in"]

    return redirect("/admin/login")

