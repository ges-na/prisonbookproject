from django.contrib import admin

from app.admin.letter import LetterAdmin
from app.admin.person import PersonAdmin
from app.admin.prison import PrisonAdmin
from app.models.letter import Letter
from app.models.person import Person
from app.models.prison import Prison

admin.site.register(Letter, LetterAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Prison, PrisonAdmin)
