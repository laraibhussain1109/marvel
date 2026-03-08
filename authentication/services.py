import json
from urllib import parse, request
from urllib.error import HTTPError, URLError


class ApiIntegrationError(Exception):
    pass


def _http_get(url, params=None, headers=None):
    if params:
        url = f"{url}?{parse.urlencode(params)}"
    req = request.Request(url, headers=headers or {}, method="GET")
    try:
        with request.urlopen(req, timeout=25) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise ApiIntegrationError(str(exc)) from exc


def _http_post_json(url, payload, headers=None):
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=25) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise ApiIntegrationError(str(exc)) from exc


def fetch_facebook_insights(connection):
    page = _http_get(
        f"https://graph.facebook.com/v20.0/{connection.external_account_id}",
        {
            "fields": "name,fan_count,followers_count,location",
            "access_token": connection.access_token,
        },
    )
    metrics = _http_get(
        f"https://graph.facebook.com/v20.0/{connection.external_account_id}/insights",
        {
            "metric": "page_impressions,page_engaged_users,page_views_total",
            "period": "day",
            "access_token": connection.access_token,
        },
    )
    metric_map = {item.get("name"): item.get("values", [{}])[0].get("value", 0) for item in metrics.get("data", [])}
    impressions = metric_map.get("page_impressions", 0)
    engagement = metric_map.get("page_engaged_users", 0)
    return {
        "followers": page.get("followers_count") or page.get("fan_count") or 0,
        "impressions": impressions,
        "page_views": metric_map.get("page_views_total", 0),
        "engagement": engagement,
        "engagement_rate": round((engagement / impressions * 100), 2) if impressions else 0,
        "location": (page.get("location") or {}).get("country", ""),
        "raw_payload": {"page": page, "insights": metrics},
    }


def fetch_instagram_insights(connection):
    insights = _http_get(
        f"https://graph.facebook.com/v20.0/{connection.external_account_id}/insights",
        {
            "metric": "reach,impressions,profile_views,follower_count,engagement",
            "period": "day",
            "access_token": connection.access_token,
        },
    )
    audience = _http_get(
        f"https://graph.facebook.com/v20.0/{connection.external_account_id}/insights",
        {
            "metric": "audience_city,audience_gender_age",
            "period": "lifetime",
            "access_token": connection.access_token,
        },
    )
    values = {item.get("name"): item.get("values", [{}])[0].get("value", 0) for item in insights.get("data", [])}
    audience_values = {item.get("name"): item.get("values", [{}])[0].get("value", {}) for item in audience.get("data", [])}
    impressions = values.get("impressions", 0)
    engagement = values.get("engagement", 0)

    return {
        "followers": values.get("follower_count", 0),
        "profile_views": values.get("profile_views", 0),
        "reach": values.get("reach", 0),
        "impressions": impressions,
        "engagement": engagement,
        "engagement_rate": round((engagement / impressions * 100), 2) if impressions else 0,
        "gender_split": audience_values.get("audience_gender_age", {}),
        "city_split": audience_values.get("audience_city", {}),
        "raw_payload": {"insights": insights, "audience": audience},
    }


def fetch_youtube_insights(connection):
    channel_stats = _http_get(
        "https://www.googleapis.com/youtube/v3/channels",
        {
            "part": "statistics,snippet",
            "id": connection.external_account_id,
            "access_token": connection.access_token,
        },
    )
    items = channel_stats.get("items", [])
    if not items:
        raise ApiIntegrationError("YouTube channel not found or access denied")

    stats = items[0].get("statistics", {})
    snippet = items[0].get("snippet", {})
    followers = int(stats.get("subscriberCount", 0))
    views = int(stats.get("viewCount", 0))

    return {
        "followers": followers,
        "profile_views": views,
        "page_views": views,
        "engagement": int(stats.get("videoCount", 0)),
        "location": snippet.get("country", ""),
        "raw_payload": channel_stats,
    }


def fetch_google_analytics(connection):
    report = _http_post_json(
        f"https://analyticsdata.googleapis.com/v1beta/properties/{connection.external_account_id}:runReport",
        {
            "dateRanges": [{"startDate": "30daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "city"}, {"name": "country"}, {"name": "userGender"}],
            "metrics": [{"name": "activeUsers"}, {"name": "screenPageViews"}, {"name": "engagedSessions"}, {"name": "engagementRate"}],
        },
        headers={"Authorization": f"Bearer {connection.access_token}"},
    )

    city_split = {}
    gender_split = {}
    users = page_views = engaged = 0
    engagement_rate = 0
    location = ""

    for row in report.get("rows", []):
        dimensions = [entry.get("value", "") for entry in row.get("dimensionValues", [])]
        metrics = [entry.get("value", "0") for entry in row.get("metricValues", [])]
        city = dimensions[0] if len(dimensions) > 0 else ""
        country = dimensions[1] if len(dimensions) > 1 else ""
        gender = dimensions[2] if len(dimensions) > 2 else "unknown"

        active_users = int(float(metrics[0])) if len(metrics) > 0 else 0
        row_page_views = int(float(metrics[1])) if len(metrics) > 1 else 0
        row_engaged = int(float(metrics[2])) if len(metrics) > 2 else 0
        row_engagement_rate = float(metrics[3]) if len(metrics) > 3 else 0

        users += active_users
        page_views += row_page_views
        engaged += row_engaged
        engagement_rate = max(engagement_rate, row_engagement_rate)
        if city:
            city_split[city] = city_split.get(city, 0) + active_users
        gender_split[gender] = gender_split.get(gender, 0) + active_users
        if country and not location:
            location = country

    return {
        "reach": users,
        "page_views": page_views,
        "engagement": engaged,
        "engagement_rate": round(engagement_rate * 100, 2),
        "city_split": city_split,
        "gender_split": gender_split,
        "location": location,
        "raw_payload": report,
    }
