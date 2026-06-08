from django.contrib import admin

from src.app.admin.issue import LetterIssueAdmin, PersonIssueAdmin
from src.app.admin.letter import LetterAdmin
from src.app.admin.person import PersonAdmin
from src.app.admin.prison import PrisonAdmin
from src.app.models.issue import LetterIssue, PersonIssue
from src.app.models.letter import Letter
from src.app.models.person import Person
from src.app.models.prison import Prison

admin.site.register(Letter, LetterAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Prison, PrisonAdmin)
admin.site.register(LetterIssue, LetterIssueAdmin)
admin.site.register(PersonIssue, PersonIssueAdmin)
