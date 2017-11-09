from django.conf import settings
from django.db import models
import datetime
import json

emoji_choices = (
    ('h', 'positive'),
    ('d','unhappy'),
    ('f', 'sick'),
    ('s', 'happy'),
    ('y', 'sleepy'),
    ('c', 'worried'),
    ('u', 'restless'),
    ('n', 'acutely ill'),
    ('l', 'confused'),
    ('b', 'in pain'),
    
    #the rest we aren't using
    ('r', 'runnynose'),
    ('a','calm'),
    ('e','energized'),
    ('m','motivated'),
    ('t','trouble concentrating'),
    
)

class Profile(models.Model):
    uuid = models.CharField(max_length=36, unique=True, blank = False, null = False, db_index = True)
    fbid = models.BigIntegerField(blank=True, null=True) #TODO. if a user changes his fbid, must delete all connected FB_Connections
    fbpic = models.URLField(blank=True, null=True)
    fbname = models.CharField(max_length=50, blank=True, null=True) 
    created = models.DateTimeField(auto_now_add=True)
    agg_latest_emoji = models.CharField(choices=emoji_choices, max_length=1, default="h")
    agg_latest_emoji_update = models.DateTimeField(default=datetime.datetime.now)
    lat = models.IntegerField(blank=True, null=True)
    lng = models.IntegerField(blank=True, null=True)
    location_last_set = models.DateTimeField(default=datetime.datetime.now) #repurposed. using it now for firebase
    referral = models.ForeignKey('Profile', blank=True, null=True)
    score = models.IntegerField(default=0)
    activity_this_week = models.IntegerField(default=50)
    social_this_week = models.IntegerField(default=50)

    def getDBName(self):
        return "User_" + str(self.uuid).replace("-", "_")
   
    def __unicode__(self):
        return self.uuid
    
class IPReferral(models.Model):
    profile = models.ForeignKey('Profile')
    ip = models.CharField(max_length=39)
    created = models.DateTimeField(auto_now_add=True)
    
class FirebaseToken(models.Model):
    profile = models.ForeignKey('Profile')
    token = models.CharField(max_length=255, default="")
    created = models.DateTimeField(auto_now_add=True)
    old = models.BooleanField(default=False)

    def __unicode__(self):
        return self.profile.uuid
    
class FB_Connection(models.Model):
    profile1 = models.ForeignKey('Profile', related_name="profile1") #this must have the fbid lower than profile2
    profile1_sharing = models.BooleanField(default=True) #is profile 1 sharing with profile 2
    profile2 = models.ForeignKey('Profile', related_name="profile2")
    profile2_sharing = models.BooleanField(default=True) # is profile 2 sharing with profile 1
    
class Emoji(models.Model):
    profile = models.ForeignKey('Profile')
    emoji = models.CharField(choices=emoji_choices, max_length=1)
    created = models.DateTimeField(auto_now_add=True)
    lat = models.IntegerField(blank=True, null=True)
    lng = models.IntegerField(blank=True, null=True)

class Emoji2(models.Model):
    profile = models.ForeignKey('Profile')
    emoji = models.CharField(choices=emoji_choices, max_length=1)
    created = models.DateTimeField()
    lat = models.IntegerField(blank=True, null=True)
    lng = models.IntegerField(blank=True, null=True)

class FluQuestions(models.Model):
    profile = models.ForeignKey('Profile')
    fluThisSeason = models.BooleanField()
    fluLastSeason = models.BooleanField()
    vaccineThisSeason = models.BooleanField()
    
class ProfileStartEnd(models.Model):
    profile = models.ForeignKey('Profile')
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    days = models.IntegerField(default=0)

class AuditEntry(models.Model):
    '''
    Represents an audit of a request against the PDS
    Given that there will be many entries (one for each request), 
    we are strictly limiting the size of data entered for each row
    The assumption is that script names and symbolic user ids
    will be under 64 characters 
    '''
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="auditentry_owner", db_index=True)
    requester = models.ForeignKey(Profile, blank = False, null = False, related_name="auditentry_requester", db_index=True)
    method = models.CharField(max_length=10)
    scopes = models.CharField(max_length=1024) # actually storing csv of valid scopes
    purpose = models.CharField(max_length=64, blank=True, null=True)
    script = models.CharField(max_length=64)
    token = models.CharField(max_length=64)
    system_entity_toggle = models.BooleanField()
    trustwrapper_result = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add = True, db_index=True)
    
    def __unicode__(self):
        self.pk

class Notification(models.Model):
    '''
    Represents a notification about a user's data. This can be filled in while constructing answers
    '''
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="notification_owner")
    title = models.CharField(max_length = 64, blank = False, null = False)
    content = models.CharField(max_length = 1024, blank = False, null = False)
    type = models.IntegerField(blank = False, null = False)
    timestamp = models.DateTimeField(auto_now_add = True)
    uri = models.URLField(blank = True, null = True)
    
    def __unicode__(self):
        self.pk

class Device(models.Model):

    datastore_owner = models.ForeignKey(Profile, blank=False, null=False, related_name="device_owner", db_index=True)
    gcm_reg_id = models.CharField(max_length=1024, blank=False, null=False)

class QuestionType(models.Model):
    UI_CHOICES = (
        ('s', 'Slider'),
        ('b', 'Binary (Yes/No)'),
        ('m', 'Multiple Choice'),
    )
    
    text = models.TextField() #What was your morning Glucose level?
    ui_type = models.CharField(max_length=1, choices=UI_CHOICES)
    params = models.TextField(default="[]", help_text="this column must be coded in JSON and is specific to the uitype - for YES/NO params=[], for slider params='[ [min, \"label\"], [max, \"label\"] ]' ie '[[ 0, \"worst\"], [10, \"best\"]]', Multiple Choice '[ [0, \"Never\"], [1, \"Some\"], [2, \"All\" ]]'")
    frequency_interval = models.IntegerField(default=1440, blank=True, null=True, help_text="minutes between the next time the question is asked. set as null if the question isn't set on a schedule directly.")
    resend_quantity = models.IntegerField(default=0, help_text="Number of times to resend this question until it's answered.")
    followup_key = models.IntegerField(blank=True, null=True, help_text="If this question result in a followup question, select the answer that results in a follow up. If not, or if any answer creates a follow up, leave blank")
    followup_question = models.ForeignKey('QuestionType', related_name="parent_question", blank=True, null=True, help_text="If this question should result in a followup question, select the follow-up question. If not, leave blank") 
    expiry = models.IntegerField(default=1440, help_text="minutes until the question expires")
    sleep_offset = models.IntegerField(default=0, help_text="minutes after a user wakes up to send notification. if negative, it's minutes before a user goes to sleep to send a notification.")
    
    
    def __unicode__(self):
        return unicode( str(self.pk) + ": " + self.text )
        
    def optionList(self):
        return json.loads(self.params)
        
    def followup_question_parent(self):
        parents = self.parent_question.all()
        if len(parents) > 0:
            return parents[0]
        return None
    
class Baseline(models.Model):
    profile = models.OneToOneField('Profile', blank=True, null=True)
    ip = models.GenericIPAddressField()
    q1 = models.BooleanField(default=False)
    q2 = models.BooleanField(default=False)
    q3 = models.BooleanField(default=False)

class IphoneDummy(models.Model):
    email = models.EmailField()
    visits = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)
    hospital = models.IntegerField(blank=True, null=True)

class QuestionInstance(models.Model):
    question_type = models.ForeignKey('QuestionType')
    profile = models.ForeignKey('Profile')
    datetime = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    answer = models.IntegerField(blank=True, null=True)
    expired = models.BooleanField(default=False, help_text="Once an answer either expires past a certain time or is completed, this is checked off. This is for the efficiency of only querying the database on expired and profile.")
    notification_counter = models.IntegerField(default=0, help_text="How many times was a notification sent out for this Question Instance?")
#    followup_instance = models.ForeignKey('QuestionInstance', blank=True, null=True, help_text="If this question has a followup question associated, then reference it from here")
    def __unicode__(self):
        return str(self.datetime) + ": " +self.profile.__unicode__() + " (" +str(self.question_type.pk)+ ")"

GENDER_CHOICE = (
    ('m', 'Male'),
    ('f', 'Female'),
)
CENTER_CHOICE = (
    ('b', 'BWH'),
    ('m', 'MGH'),
    ('o', 'other'),
)
ETIOLOGY_CHOICE = (
    ('1', 'EtOH'),
    ('2', 'HCV'),
    ('3', 'NASH'),
    ('4', 'PBC'),
    ('5', 'PSC'),
    ('6', 'AIH'),
    ('7', 'A1AT'),
    ('8', 'Wilson'),
    ('9', 'Hemochromatosis'),
    ('10', 'HBV'),
    ('11', 'other'),
)
YN_CHOICE = (
    ('0', 'No'),
    ('1', 'Yes'),
    ('u', 'Unknown'),
)
CARE_LOCATION_CHOICE = (
    ('h', 'hospital'),
    ('c', 'clinic'),
    ('e', 'emergency room'),
)
        
class Chart1(models.Model):
    study_id = models.CharField(max_length=15)
    last_name = models.CharField(max_length=20)
    mrn = models.CharField(max_length=9)
    created = models.DateTimeField(auto_now_add=True)
    dob = models.DateField()
    doe = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    center = models.CharField(max_length=1, choices=CENTER_CHOICE)
    etiology = models.CharField(max_length=2, choices=ETIOLOGY_CHOICE)
    baseline_meld = models.IntegerField(blank=True, null=True)
    baseline_meld_insufficient = models.BooleanField(default=False) 
    baseline_child = models.IntegerField(blank=True, null=True)
    baseline_child_insufficient = models.BooleanField(default=False)
    transplant_candidate = models.CharField(max_length=1, choices=YN_CHOICE)
    hcc = models.CharField(max_length=1, choices=YN_CHOICE)
    aspirin81 = models.CharField(max_length=1, choices=YN_CHOICE)
    aspirin325 = models.CharField(max_length=1, choices=YN_CHOICE)
    other_antiplatelet = models.CharField(max_length=1, choices=YN_CHOICE)
    anticoagulant = models.CharField(max_length=1, choices=YN_CHOICE)
    d_first_liver_care = models.DateField(blank=True, null=True)
    d_first_liver_care2 = models.CharField(max_length=100, blank=True, null=True)
    d_last_liver_care_prior_to_study = models.DateField(blank=True, null=True)
    d_last_liver_care_prior_to_study2 = models.CharField(max_length=100, blank=True, null=True)
    location_last_liver_care_prior_to_study = models.CharField(max_length=1, choices=CARE_LOCATION_CHOICE)
    
class Chart2(models.Model):
    pass