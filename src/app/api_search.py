import json
import os

from django.utils.html import format_html
import requests


def cor_request(inmate_number: str) -> list[dict[str, str | None]]:
    response = requests.post(
        "https://captorapi.cor.pa.gov/InmateLocatorAPIV8/api/v1/InmateLocator/SearchResults",
        data=json.dumps({"id": inmate_number}),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    if response.status_code != 200:
        return [{"Error": response.reason}]
    inmates = response.json().get("inmates")
    if not inmates:
        return [
            {
                "No results": format_html(
                    "{} <a href={} target='_blank'>{}</a>",
                    "Full ID required for search.",
                    "https://inmatelocator.cor.pa.gov",
                    "Check COR directly.",
                )
            }
        ]
    results = []
    for inmate in inmates:
        results.append(
            {
                "Inmate number": inmate.get("inmate_number"),
                "First name": inmate.get("inm_firstname"),
                "Middle name": inmate.get("inm_middlename"),
                "Last name": inmate.get("inm_lastname"),
                "Name suffix": inmate.get("inm_njamesuffix"),
                "Facility": inmate.get("fac_name"),
            }
        )
    return results


def bop_request(inmate_number: str) -> list[dict[str, str | None]]:
    response = requests.post(
        "https://www.bop.gov/PublicInfo/execute/inmateloc",
        data=f"todo=query&output=json&inmateNumType=IRN&inmateNum={inmate_number}",
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
    )
    if response.status_code != 200:
        return [{"Error": response.reason}]
    inmates = response.json().get("InmateLocator")
    if not inmates:
        return [
            {
                "No results": format_html(
                    "{} <a href={} target='_blank'>{}</a>",
                    "Full ID (no dashes) required for search.",
                    "https://www.bop.gov/inmateloc/",
                    "Check BOP directly.",
                )
            }
        ]
    results = []
    for inmate in inmates:
        record = {
            "Inmate number": inmate.get("inmateNum"),
            "First name": inmate.get("nameFirst"),
            "Middle name": inmate.get("nameMiddle"),
            "Last name": inmate.get("nameLast"),
            "Facility": f"{inmate.get('faclType', '')} {inmate.get('faclName')}",
        }
        facilities_url = f"http://www.bop.gov/PublicInfo/execute/phyloc?todo=query&output=json&code={inmate.get('faclCode')}"
        facility_response = requests.get(facilities_url)
        facilities = facility_response.json().get("Visiting")
        if facilities:
            record["State"] = facilities[0].get("state")
        if inmate.get("releaseCode").lower() == "r":
            record["Status"] = "Released"
        results.append(record)
    return results


def vinelink_request(inmate_number: str) -> list[dict[str, str | None]]:
    login_url = "https://vinelink-mobile.vineapps.com/api/v1/accounts/login"
    login_headers = {
        "Auth": f"Basic {os.environ.get('VINETOKEN')}",
        "x-vine-application": "VINELINK",
    }
    login_response = requests.post(login_url, headers=login_headers)
    jwt = login_response.headers.get("x-vine-jwt")
    session_id = login_response.headers.get("x-vine-session-id")
    url = f"https://vinelink-mobile.vineapps.com/api/v1/persons?isPartialSearch=true&siteRefId=PASWVINE&personContextRefId={inmate_number}&stateServed=PA"
    headers = {
        "Accept": "application/json, text/plain",
        "x-vine-application": "VINELINK",
        "x-vine-session-id": session_id,
        "x-vine-jwt": jwt,
        "Connection": "keep-alive",
    }
    response = requests.get(url, headers=headers)
    results = []
    inmates = response.json().get("_embedded", {})["persons"]
    if not inmates:
        return [
            {
                "No results": format_html(
                    "<a href={} target='_blank'>{}</a>",
                    "https://www.vinelink.com/search/PA/Person",
                    "Check VINELink directly.",
                )
            }
        ]
    for inmate in inmates:
        location_name = None
        for location in inmate.get("locations"):
            if location["locationType"] == "HOLDING_FACILITY":
                location_name = location["locationName"]
        person_context_id = inmate.get("personContext", {}).get("contextId")
        results.append(
            {
                "Inmate number": inmate.get("personContext", {}).get("contextRefId"),
                "First name": inmate.get("personName", {}).get("firstName"),
                "Middle name": inmate.get("personName", {}).get("middleName"),
                "Last name": inmate.get("personName", {}).get("lastName"),
                "Facility": location_name,
                "Status": inmate.get("offenderInfo", {}).get("custodyStatus", {}).get("name"),
                "Details": format_html(
                    "<a href={} target='_blank'>VINELink</a>",
                    f"https://www.vinelink.com/person-detail/offender/{person_context_id}",
                ),
            }
        )
    return results
