from django.contrib import admin
from src.app.admin.problem_note import ProblemNoteAdmin

from src.app.admin.letter import LetterAdmin
from src.app.admin.person import PersonAdmin
from src.app.admin.prison import PrisonAdmin
from src.app.models.letter import Letter
from src.app.models.person import Person
from src.app.models.prison import Prison
from src.app.models.problem_note import ProblemNote

admin.site.register(Letter, LetterAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Prison, PrisonAdmin)
admin.site.register(ProblemNote, ProblemNoteAdmin)
