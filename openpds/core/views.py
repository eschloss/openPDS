from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from openpds.core.models import Profile
from pymongo import Connection
from openpds import settings
import json
import random


def dump(request): 
    profiles = Profile.objects.all()
    data = {}
    
    connection = Connection(
        host=random.choice(getattr(settings, "MONGODB_HOST", None)),
        port=getattr(settings, "MONGODB_PORT", None),
        readPreference='nearest'
    )

    for profile in profiles:
        db = connection["User_" + str(profile.id)]
        funf = db["funf"]
        data[profile.uuid] = funf.find()
        
    connection.close()

    return render_to_response("dataDump.csv", data)
