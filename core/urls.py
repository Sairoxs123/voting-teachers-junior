from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name = "home"),
    path("admin/login/", login, name="login"),
    path("admin/", admin, name="admin"),
    path("admin/add/contestant/", addContenstant, name = "add"),
    path("admin/delete/contestant/", delete, name = "delete"),
    path("voting/form/", votingForm, name="form"),
    path("voting/form/mobile", votingFormMobile, name="mobileForm"),
    path("voting/submit/", submitVote, name="submit"),
    path("reset/votes/", resetVotes, name="reset"),
    path("delete/all/", deleteAll, name="deleteall"),
    path("open/", openVoting, name="open"),
    path("close/", closeVoting, name="close"),
    path("vote/data/create-csv/", createCSV, name="create-csv"),
    path("email/sent/", emailSent, name="email-sent"),
    path("auth/", details, name="auth"),
    path("email/verify/", verifyEmail, name="verify-email"),
    path("logout/", logout, name="logout")
]
