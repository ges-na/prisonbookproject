from ajax_select import LookupChannel, register
from django.db.models import Q

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
        return f"<span class='person'>{person.inmate_number} - {person.last_name}, {person.first_name}</span>"

    def format_item_display(self, person: Person):
        body = f"""
                <div>
                <a
                    id='{person.id}'
                    class='related-widget-wrapper-link change-related'
                    data-href-template='/admin/app/person/{person.id}/change/?_to_field=id&_popup=1'
                    href='/admin/app/person/{person.id}/change/?_to_field=id&_popup=1'
                >
                    <img src="/static/admin/img/icon-changelink.svg" alt="Change">
                </a>
                </div>
                <div>
                {person.inmate_number} - {person.last_name}, {person.first_name}</div>
                <div>{person.current_prison}</div>
                """
        eligibility = f"<div>{person.get_eligibility_str()}</div>"
        if person.current_prison and person.current_prison.restrictions:
            restrictions = (
                f"<div>RESTRICTIONS: {person.current_prison.restrictions}</div>"
            )
            return body + restrictions + eligibility
        return body + eligibility
