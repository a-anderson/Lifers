import pytest
import requests
import pandas as pd
from lifers import ebird_api


class TestGetSubnationalCodes:
    mock_url = "https://api.ebird.org/v2/ref/region/list/subnational1/AU"

    def test_successful_request(self, requests_mock):
        requests_mock.get(
            self.mock_url,
            json=[{"name": "Region1", "code": "R1"}, {"name": "Region2", "code": "R2"}],
        )
        parent_code = "AU"
        subnational_level = 1
        headers = {"Authorization": "your_api_key_here"}
        result = ebird_api.get_subnational_codes(
            parent_code, subnational_level, headers
        )
        assert result == {"Region1": "R1", "Region2": "R2"}

    def test_when_api_error_then_raises_request_exception(self, requests_mock):
        requests_mock.get(
            self.mock_url,
            status_code=500,
        )
        parent_code = "AU"
        subnational_level = 1
        headers = {"Authorization": "your_api_key_here"}
        with pytest.raises(requests.RequestException):
            ebird_api.get_subnational_codes(parent_code, subnational_level, headers)

    def test_when_missing_authorization_then_raises_request_error(self):
        parent_code = "AU"
        subnational_level = 1
        headers = {}
        with pytest.raises(requests.RequestException):
            ebird_api.get_subnational_codes(parent_code, subnational_level, headers)

    def test_when_empty_response_then_returns_empty_dict(self, requests_mock):
        requests_mock.get(self.mock_url, json=[])
        parent_code = "AU"
        subnational_level = 1
        headers = {"Authorization": "your_api_key_here"}
        result = ebird_api.get_subnational_codes(
            parent_code, subnational_level, headers
        )
        assert result == {}

    def test_non_200_response_then_raises_request_error(self, requests_mock):
        requests_mock.get(self.mock_url, status_code=404)
        parent_code = "AU"
        subnational_level = 1
        headers = {"Authorization": "your_api_key_here"}
        with pytest.raises(requests.RequestException):
            ebird_api.get_subnational_codes(parent_code, subnational_level, headers)


class TestGetRecentObservations:
    mock_url = "https://api.ebird.org/v2/data/obs/AU-VIC-MEL/recent"

    def test_when_request_successful_then_result_correctly_formatted(
        self, requests_mock
    ):
        requests_mock.get(
            self.mock_url,
            json=[
                {"speciesCode": "SPECIES1"},
                {"speciesCode": "SPECIES2"},
            ],
        )
        region_code = "AU-VIC-MEL"
        days_back = 3
        headers = {"Authorization": "your_api_key_here"}
        result = ebird_api.get_recent_observations(region_code, days_back, headers)
        assert len(result) == 2
        assert result[0]["speciesCode"] == "SPECIES1"
        assert result[1]["speciesCode"] == "SPECIES2"

    def test_when_api_error_then_raises_request_exception(self, requests_mock):
        requests_mock.get(
            self.mock_url,
            status_code=500,
        )
        region_code = "AU-VIC-MEL"
        days_back = 3
        headers = {"Authorization": "your_api_key_here"}
        with pytest.raises(requests.RequestException):
            ebird_api.get_recent_observations(region_code, days_back, headers)

    def test_when_authorization_missing_then_raises_request_exception(self):
        region_code = "AU-VIC-MEL"
        days_back = 3
        headers = {}
        with pytest.raises(requests.RequestException):
            ebird_api.get_recent_observations(region_code, days_back, headers)

    def test_when_response_is_empty_then_returns_empty_list(self, requests_mock):
        requests_mock.get(self.mock_url, json=[])
        region_code = "AU-VIC-MEL"
        days_back = 3
        headers = {"Authorization": "your_api_key_here"}
        result = ebird_api.get_recent_observations(region_code, days_back, headers)
        assert result == []

    def test_when_non_200_response_then_raises_request_exception(self, requests_mock):
        requests_mock.get(self.mock_url, status_code=404)
        region_code = "AU-VIC-MEL"
        days_back = 3
        headers = {"Authorization": "your_api_key_here"}
        with pytest.raises(requests.RequestException):
            ebird_api.get_recent_observations(region_code, days_back, headers)


class TestGetRecentSpeciesObs:
    mock_url = "https://api.ebird.org/v2/data/obs/AU-VIC-MEL/recent/SPECIES1"

    def test_when_request_successful_then_formats_data_correctly(self, requests_mock):
        requests_mock.get(
            self.mock_url,
            json=[
                {"speciesCode": "SPECIES1", "obsDt": "2023-08-01", "howMany": 2},
                {"speciesCode": "SPECIES1", "obsDt": "2023-08-02", "howMany": 1},
            ],
        )
        region_code = "AU-VIC-MEL"
        species_code = "SPECIES1"
        days_back = 7
        headers = {"Authorization": "your_api_key_here"}
        result = ebird_api.get_recent_species_obs(
            region_code, species_code, days_back, headers
        )
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (2, 3)
        assert result["speciesCode"].tolist() == ["SPECIES1", "SPECIES1"]

    def test_when_api_error_then_raises_request_exception(self, requests_mock):
        requests_mock.get(
            self.mock_url,
            status_code=500,
        )
        region_code = "AU-VIC-MEL"
        species_code = "SPECIES1"
        days_back = 7
        headers = {"Authorization": "your_api_key_here"}
        with pytest.raises(requests.RequestException):
            ebird_api.get_recent_species_obs(
                region_code, species_code, days_back, headers
            )

    def test_when_authorization_missing_then_raises_request_exception(self):
        region_code = "AU-VIC-MEL"
        species_code = "SPECIES1"
        days_back = 7
        headers = {}
        with pytest.raises(requests.RequestException):
            ebird_api.get_recent_species_obs(
                region_code, species_code, days_back, headers
            )

    def test_when_response_is_empty_then_returns_empty_df(self, requests_mock):
        requests_mock.get(self.mock_url, json={})
        region_code = "AU-VIC-MEL"
        species_code = "SPECIES1"
        days_back = 7
        headers = {"Authorization": "your_api_key_here"}
        result = ebird_api.get_recent_species_obs(
            region_code, species_code, days_back, headers
        )
        assert result.empty

    def test_when_non_200_response_then_raises_request_exception(self, requests_mock):
        requests_mock.get(self.mock_url, status_code=404)
        region_code = "AU-VIC-MEL"
        species_code = "SPECIES1"
        days_back = 7
        headers = {"Authorization": "your_api_key_here"}
        with pytest.raises(requests.RequestException):
            ebird_api.get_recent_species_obs(
                region_code, species_code, days_back, headers
            )
