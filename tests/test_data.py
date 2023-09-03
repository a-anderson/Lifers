import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from lifers import data


class TestScinameSpeciesCodes:
    def test_when_called_then_returns_dict(self):
        result = data.sciname_speciescodes()
        assert isinstance(result, dict)

    def test_when_called_then_returns_non_empty_dict(self):
        result = data.sciname_speciescodes()
        assert len(result) > 0


class TestCountryCodes:
    def test_when_called_then_returns_dict(self):
        result = data.country_codes()
        assert isinstance(result, dict)

    def test_when_called_then_returns_not_empty_dict(self):
        result = data.country_codes()
        assert len(result) > 0


class TestLoadLifelistCSV:
    @pytest.fixture
    def sample_csv(self, tmp_path):
        csv_content = """Row #,Taxon Order,Category,Common Name,Scientific Name,Count,Location,S/P,Date,LocID,SubID,Exotic,Countable
        1,3764,species,Australian Owlet-nightjar,Aegotheles cristatus,1,"Finland Road, Paradise Waters",AU-QLD,12 Aug 2023,L3862700,S147015015,,1
        2,5817,species,Double-banded Plover,Charadrius bicinctus,1,Maroochy River Mouth north side,AU-QLD,11 Aug 2023,L3801739,S146953601,,1
        """
        csv_path = tmp_path / "test.csv"
        csv_path.write_text(csv_content)
        return csv_path

    def test_when_called_with_valid_csv_then_returns_dataframe_with_correct_number_of_rows(
        self, sample_csv
    ):
        df = data.load_lifelist_csv(sample_csv)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_when_called_with_invalid_csv_format_then_raises_value_error(
        self, tmp_path
    ):
        invalid_csv = tmp_path / "invalid.csv"
        invalid_csv.write_text("Invalid content")
        with pytest.raises(
            ValueError,
        ):
            data.load_lifelist_csv(invalid_csv)

    def test_when_called_with_missing_required_columns_then_raises_value_error(
        self, tmp_path
    ):
        invalid_csv = tmp_path / "invalid.csv"
        invalid_content = "Row #,Taxon Order\n1,3764\n2,5817\n"
        invalid_csv.write_text(invalid_content)
        with pytest.raises(ValueError, match="Missing required columns"):
            data.load_lifelist_csv(invalid_csv)

    def test_when_called_with_valid_csv_then_filters_category_species(self, sample_csv):
        df = data.load_lifelist_csv(sample_csv)
        assert all(df["Category"] == "species")

    def test_when_called_with_valid_csv_then_adds_species_code_column(self, sample_csv):
        df = data.load_lifelist_csv(sample_csv)
        assert "Species Code" in df.columns

    def test_when_called_with_valid_csv_then_species_number_matches_dataframe_shape(
        self, sample_csv
    ):
        df = data.load_lifelist_csv(sample_csv)
        assert all(df["Species Number"] == df.shape[0] - df.index.values)


class TestFormatNeedsData:
    @pytest.fixture
    def sample_data(self):
        data = {
            "speciesCode": ["sparrow", "pigeon"],
            "comName": ["House Sparrow", "Rock Pigeon"],
            "sciName": ["Passer domesticus", "Columba livia"],
        }
        return pd.DataFrame(data)

    def test_when_called_with_valid_data_then_returned_df_includes_species_information_column(
        self, sample_data
    ):
        formatted_data = data.format_needs_data(sample_data)

        assert "Species Information" in formatted_data.columns
        assert "Common Name" in formatted_data.columns
        assert "Scientific Name" in formatted_data.columns

        expected_urls = [
            "https://ebird.org/australia/species/sparrow",
            "https://ebird.org/australia/species/pigeon",
        ]
        assert formatted_data["Species Information"].tolist() == expected_urls

    def test_when_called_with_data_subset_then_returned_df_has_only_subset_columns(
        self, sample_data
    ):
        formatted_data = data.format_needs_data(sample_data)

        expected_columns = ["Common Name", "Scientific Name", "Species Information"]
        assert list(formatted_data.columns) == expected_columns


class TestFormatRegionNeedsDataForMap:
    @pytest.fixture
    def sample_data(self):
        # Create sample data for testing
        data = {
            "locName": ["Location1", "Location2", "Location1"],
            "lat": [42.0, 43.0, 42.0],
            "lng": [-71.0, -72.0, -71.0],
            "comName": ["Sparrow", "Pigeon", "Pigeon"],
        }
        return pd.DataFrame(data)

    def test_when_called_with_valid_data_then_formats_data_correctly(self, sample_data):
        formatted_data = data.format_region_needs_data_for_map(sample_data)

        expected_columns = ["locName", "lng", "lat", "tooltip_species", "num_species"]
        assert list(formatted_data.columns) == expected_columns

        expected_data = pd.DataFrame(
            {
                "locName": ["Location1", "Location2"],
                "lng": [-71.0, -72.0],
                "lat": [42.0, 43.0],
                "tooltip_species": ["1. Pigeon\n2. Sparrow", "1. Pigeon"],
                "num_species": [2, 1],
            }
        )
        pd.testing.assert_frame_equal(formatted_data, expected_data)
