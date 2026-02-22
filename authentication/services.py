import json
from urllib import parse, request
from urllib.error import HTTPError, URLError


class ApiIntegrationError(Exception):
    pass


def _http_get(url, params=None):
    if params:
        url = f"{url}?{parse.urlencode(params)}"
    try:
        with request.urlopen(url, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise ApiIntegrationError(str(exc)) from exc


def fetch_meta_insights(connection):
    fields = "fan_count,followers_count,impressions,page_views_total"
    payload = _http_get(
        f"https://graph.facebook.com/v20.0/{connection.external_account_id}",
        {"fields": fields, "access_token": connection.access_token},
    )
    return {
        "followers": payload.get("fan_count") or payload.get("followers_count") or 0,
        "impressions": payload.get("impressions") or 0,
        "page_views": payload.get("page_views_total") or 0,
        "location": payload.get("location", ""),
    }


def fetch_instagram_insights(connection):
    metrics = ",".join([
        "reach",
        "impressions",
        "profile_views",
        "follower_count",
        "engagement",
    ])
    payload = _http_get(
        f"https://graph.facebook.com/v20.0/{connection.external_account_id}/insights",
        {"metric": metrics, "period": "day", "access_token": connection.access_token},
    )
    values = {item.get("name"): item.get("values", [{}])[0].get("value", 0) for item in payload.get("data", [])}

    audience = _http_get(
        f"https://graph.facebook.com/v20.0/{connection.external_account_id}/insights",
        {"metric": "audience_city,audience_gender_age", "period": "lifetime", "access_token": connection.access_token},
    )
    audience_values = {item.get("name"): item.get("values", [{}])[0].get("value", {}) for item in audience.get("data", [])}

    impressions = values.get("impressions", 0)
    engagement = values.get("engagement", 0)
    engagement_rate = (engagement / impressions * 100) if impressions else 0

    return {
        "followers": values.get("follower_count", 0),
        "profile_views": values.get("profile_views", 0),
        "reach": values.get("reach", 0),
        "impressions": impressions,
        "engagement": engagement,
        "engagement_rate": round(engagement_rate, 2),
        "gender_split": audience_values.get("audience_gender_age", {}),
        "city_split": audience_values.get("audience_city", {}),
    }


def fetch_google_analytics(connection):
    body = {
        "metrics": [
            {"name": "screenPageViews"},
            {"name": "activeUsers"},
            {"name": "engagementRate"},
        ],
        "dimensions": [{"name": "city"}, {"name": "country"}, {"name": "userGender"}],
        "dateRanges": [{"startDate": "30daysAgo", "endDate": "today"}],
    }

    req = request.Request(
        f"https://analyticsdata.googleapis.com/v1beta/properties/{connection.external_account_id}:runReport",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {connection.access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise ApiIntegrationError(str(exc)) from exc

    rows = payload.get("rows", [])
    page_views = 0
    users = 0
    engagement_rate = 0
    city_split = {}
    gender_split = {}
    location = ""

    for row in rows:
        dimensions = [d.get("value", "") for d in row.get("dimensionValues", [])]
        metrics = [m.get("value", "0") for m in row.get("metricValues", [])]
        city = dimensions[0] if len(dimensions) > 0 else ""
        country = dimensions[1] if len(dimensions) > 1 else ""
        gender = dimensions[2] if len(dimensions) > 2 else "unknown"

        views = int(float(metrics[0])) if len(metrics) > 0 else 0
        active_users = int(float(metrics[1])) if len(metrics) > 1 else 0
        this_engagement_rate = float(metrics[2]) if len(metrics) > 2 else 0

        page_views += views
        users += active_users
        engagement_rate = max(engagement_rate, this_engagement_rate)
        if city:
            city_split[city] = city_split.get(city, 0) + active_users
        gender_split[gender] = gender_split.get(gender, 0) + active_users
        if country and not location:
            location = country

    return {
        "page_views": page_views,
        "reach": users,
        "engagement_rate": round(engagement_rate * 100, 2),
        "city_split": city_split,
        "gender_split": gender_split,
        "location": location,
    }
