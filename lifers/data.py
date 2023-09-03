import pandas as pd


def sciname_speciescodes():
    all_ebird_data = pd.read_csv(
        "lifers/ebird_taxonomy_v2022.csv", usecols=["SCI_NAME", "SPECIES_CODE"]
    )
    return dict(zip(all_ebird_data["SCI_NAME"], all_ebird_data["SPECIES_CODE"]))


def country_codes():
    countries_df = pd.read_csv("lifers/country_codes.csv")
    return dict(zip(countries_df["Country"], countries_df["Alpha-2"]))


def load_lifelist_csv(filepath):
    try:
        df = pd.read_csv(filepath)
    except pd.errors.ParserError:
        raise ValueError("Error parsing the CSV file")

    required_columns = [
        "Taxon Order",
        "Category",
        "Common Name",
        "Scientific Name",
        "Count",
        "Location",
        "S/P",
        "Date",
        "LocID",
        "SubID",
        "Exotic",
        "Countable",
    ]
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    df = df[df["Category"] == "species"]

    if "Species Code" not in df.columns:
        df["Species Code"] = df["Scientific Name"].map(sciname_speciescodes())

    df["Species Number"] = df.shape[0] - df.index.values

    return df


def format_needs_data(needs_data):
    needs_data["Species Information"] = (
        "https://ebird.org/australia/species/" + needs_data["speciesCode"]
    )
    needs_data = needs_data.rename(
        columns={"comName": "Common Name", "sciName": "Scientific Name"}
    )
    return needs_data[["Common Name", "Scientific Name", "Species Information"]]


def format_region_needs_data_for_map(region_needs_df):
    region_loc_data = (
        region_needs_df.groupby(["locName", "lat", "lng"])
        .agg({"comName": lambda x: sorted(set(x))})  # Sort the 'comName' values
        .reset_index()
    )
    region_loc_data["num_species"] = region_loc_data["comName"].apply(len)
    region_loc_data["tooltip_species"] = region_loc_data["comName"].apply(
        lambda x: "\n".join(f"{i+1}. {value}" for i, value in enumerate(x))
    )
    return region_loc_data[["locName", "lng", "lat", "tooltip_species", "num_species"]]
