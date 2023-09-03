import requests
import pandas as pd


def get_subnational_codes(parent_code, subnational_level, headers):
    response = requests.get(
        f"https://api.ebird.org/v2/ref/region/list/subnational{subnational_level}/{parent_code}",
        headers=headers,
    )

    if response.status_code != 200:
        raise requests.RequestException(
            f"API request failed with status code: {response.status_code}"
        )

    return {region["name"]: region["code"] for region in response.json()}


def get_recent_observations(region_code, days_back, headers):
    response = requests.get(
        f"https://api.ebird.org/v2/data/obs/{region_code}/recent",
        params={
            "back": days_back,
        },
        headers=headers,
    )

    if response.status_code != 200:
        raise requests.RequestException(
            f"API request failed with status code: {response.status_code}"
        )

    return response.json()


def get_recent_species_obs(region_code, species_code, days_back, headers):
    params = {"back": days_back}
    response = requests.get(
        f"https://api.ebird.org/v2/data/obs/{region_code}/recent/{species_code}",
        headers=headers,
        params=params,
    )

    if response.status_code != 200:
        raise requests.RequestException(
            f"API request failed with status code: {response.status_code}"
        )
    return pd.DataFrame(response.json())
