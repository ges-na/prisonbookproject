from ajax_select import LookupChannel, register
from django.db.models import Q

from django.utils.html import format_html
from django.urls import reverse
from src.app.models.person import Person


@register("person")
class PersonLookup(LookupChannel):
    model = Person

    def get_query(self, query, request):
        return self.model.objects.filter(
            Q(inmate_number__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        ).order_by("inmate_number")[:10]

    def format_match(self, person):
        return format_html("<span class='person'>{} - {}, {}</span>", person.inmate_number, person.last_name, person.first_name)

    def format_item_display(self, person: Person):

        link = reverse('admin:app_person_change', kwargs={"object_id": person.id})
        # TODO: a refresh button would be cool here, since
        # the person data doesn't refresh after editing in popout
        body = format_html("""
                <div>
                <a
                    class='related-widget-wrapper-link change-related'
                    href='{}'
                    onclick="return showAddAnotherPopup(this);"
                >
                    <img src="/static/admin/img/icon-changelink.svg" alt="Change">
                </a>
                </div>
                <div>
                {} - {}, {}</div>
                <div>{}</div>
                    """, link, person.inmate_number, person.last_name, person.first_name, person.current_prison)
        eligibility = format_html("<div>{}</div>", person.get_eligibility_str())
        if person.current_prison and person.current_prison.restrictions:
            restrictions = format_html(
                "<div>RESTRICTIONS: {}</div>", person.current_prison.restrictions
            )
            return format_html("<div id='person_data'> {} {} {} </div>", body, restrictions, eligibility)
        return format_html("<div id='person_data'> {} {} </div>", body, eligibility)
