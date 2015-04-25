from django.contrib import admin
from apps.models import UserStory
import reversion

# Register your models here.
class UserStoryAdmin(reversion.VersionAdmin):
    pass
    
admin.site.register(UserStory, UserStoryAdmin)