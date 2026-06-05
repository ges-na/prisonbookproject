from ajax_select import LookupChannel, register
from django.db.models import Q

from django.utils.html import format_html
from django.urls import reverse
from src.app.models.person import Person


@register("person_channel")
class PersonLookup(LookupChannel):
    model = Person

    def check_auth(self, request):
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_contributor)

    def get_query(self, q, request):
        del request
        return self.model.objects.filter(
            Q(inmate_number__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        ).order_by("inmate_number")[:10]

    def format_match(self, obj):
        return format_html("<span class='person'>{} - {}, {}</span>", obj.inmate_number, obj.last_name, obj.first_name)

    def format_item_display(self, obj: Person):

        link = reverse('admin:app_person_change', kwargs={"object_id": obj.id})
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
                    """, link, obj.inmate_number, obj.last_name, obj.first_name, obj.current_prison)
        eligibility = format_html("<div>{}</div>", obj.get_eligibility_str())
        if obj.current_prison and obj.current_prison.restrictions:
            restrictions = format_html(
                "<div>RESTRICTIONS: {}</div>", obj.current_prison.restrictions
            )
            return format_html("<div id='person_data'> {} {} {} </div>", body, restrictions, eligibility)
        return format_html("<div id='person_data'> {} {} </div>", body, eligibility)

@register("person_contrib_channel")
class PersonLookupContrib(LookupChannel):
    model = Person

    def check_auth(self, request):
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_contributor)

    def get_query(self, q, request):
        del request
        return self.model.objects.filter(
            Q(inmate_number__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        ).order_by("inmate_number")[:10]

    def format_match(self, obj: Person):
        return format_html("<span class='person'>{} - {}, {}</span>", obj.inmate_number, obj.last_name, obj.first_name)

    def format_item_display(self, obj: Person):
        body = format_html("""
                <div>
                {} - {}, {}</div>
                <div>{}</div>
                    """, obj.inmate_number, obj.last_name, obj.first_name, obj.current_prison)
        eligibility = format_html("<div>{}</div>", obj.get_eligibility_str(links=False))
        if obj.current_prison and obj.current_prison.restrictions:
            restrictions = format_html(
                "<div>RESTRICTIONS: {}</div>", obj.current_prison.restrictions
            )
            return format_html("<div id='person_data'> {} {} {} </div>", body, restrictions, eligibility)
        return format_html("<div id='person_data'> {} {} </div>", body, eligibility)
