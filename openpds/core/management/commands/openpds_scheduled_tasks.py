from django.core.management.base import BaseCommand
import logging
from openpds.questions.tasks import ensureFunfIndexes, recentProbeCounts, dumpFunfData, dumpSurveyData, flumojiNotifications, emojiLocations, deleteUnusedProfiles, profileLocations, setInfluenceScores, cleanExpiredReferrals

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        #flumojiNotifications.delay()
        recentProbeCounts.apply_async(countdown=10)

        ensureFunfIndexes.apply_async(countdown=300)
        dumpFunfData.apply_async(countdown=0)
        #dumpFunfData.apply_async(countdown=60)
        dumpFunfData.apply_async(countdown=2*60)
        #dumpFunfData.apply_async(countdown=3*60)
        dumpFunfData.apply_async(countdown=4*60)
        #dumpFunfData.apply_async(countdown=5*60)
        dumpFunfData.apply_async(countdown=6*60)
        #dumpFunfData.apply_async(countdown=7*60)
        dumpFunfData.apply_async(countdown=8*60)
        #dumpFunfData.apply_async(countdown=9*60)
        #dumpSurveyData.apply_async()
        #emojiLocations.apply_async(countdown=900)
        #profileLocations.apply_async(countdown=1200)
        #deleteUnusedProfiles.apply_async()
        #setInfluenceScores.apply_async(countdown=1500)
        #cleanExpiredReferrals.apply_async(countdown=1800)
