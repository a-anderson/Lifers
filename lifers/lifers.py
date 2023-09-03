import os
import streamlit as st
import pandas as pd
import concurrent.futures
import ebird_api
import data
import visualise


def main():
    # Get API header:
    api_key = os.environ.get("EBIRD_API_TOKEN")

    if api_key is None:
        st.warning(
            "Environment variable 'EBIRD_API_TOKEN' is not set. Please set it before running the app."
        )
        return

    headers = {"X-eBirdApiToken": api_key}

    st.set_page_config(layout="wide")
    st.title("Lifers: An eBird Needs Finder")

    st.sidebar.title("Search Preferences")
    st.sidebar.divider()

    # Select region codes to search for lifers (e.g., AU-VIC-MEL for Melbourne, Australia)
    # Country selection
    country_codes = data.country_codes()
    country_list = list(country_codes.keys())
    selected_country = st.sidebar.selectbox(
        label="Select a country",
        options=country_list,
        index=country_list.index("Australia"),
    )

    # Subnational region selection
    subnational1_codes = ebird_api.get_subnational_codes(
        country_codes[selected_country], subnational_level=1, headers=headers
    )
    subnational1_names = sorted(list(subnational1_codes.keys()))
    selected_subnational1 = st.sidebar.selectbox(
        "Select a region", [""] + subnational1_names
    )

    # Sub-subnational region selection for level 2 subregions
    if selected_subnational1 != "":
        region_code = subnational1_codes[selected_subnational1]
        subnational2_codes = ebird_api.get_subnational_codes(
            region_code, subnational_level=2, headers=headers
        )
        subnational2_names = sorted(list(subnational2_codes.keys()))
        selected_subnational2 = st.sidebar.selectbox(
            "Select a sub-region", [""] + subnational2_names
        )
        if selected_subnational2 != "":
            region_code = subnational2_codes[selected_subnational2]
    else:
        region_code = country_codes[selected_country]

    st.sidebar.divider()

    # Select the number of days back to collect observations
    days_back = st.sidebar.number_input(
        "How many days of observations do you want to retrieve?", min_value=1, step=1
    )
    st.sidebar.divider()

    # File uploader for lifelist CSV
    csv_file = st.sidebar.file_uploader("Upload your lifelist CSV file", type=["csv"])

    find_button_pressed = st.sidebar.button(
        "Find Species", type="primary", use_container_width=True
    )

    if find_button_pressed and csv_file is not None:
        # Load lifelist CSV
        lifelist_df = data.load_lifelist_csv(csv_file)

        # Extract unique species from lifelist
        unique_species = lifelist_df["Species Code"].unique()

        if len(unique_species) == 0:
            st.warning("No species found in the lifelist CSV.")
        else:
            st.subheader("Species in your lifelist:")
            st.dataframe(
                lifelist_df[
                    [
                        "Species Number",
                        "Common Name",
                        "Scientific Name",
                        "Species Code",
                        "Category",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

            # Get recent observations for the region
            recent_observations = ebird_api.get_recent_observations(
                region_code, days_back, headers=headers
            )

            if recent_observations is not None:
                recent_obs_df = pd.DataFrame(recent_observations)
                needs_df = recent_obs_df.loc[
                    ~recent_obs_df["speciesCode"].isin(unique_species)
                ]
                needs_df.reset_index(drop=True, inplace=True)

                if needs_df.shape[0] > 0:
                    st.subheader(
                        f"Needed species observed in the past {days_back} days:"
                    )
                    st.dataframe(
                        data.format_needs_data(needs_df),
                        column_config={
                            "Species Information": st.column_config.LinkColumn(
                                "Species Information",
                                help="eBird species information link",
                            )
                        },
                        hide_index=True,
                        use_container_width=True,
                    )

                    # Recent needs by location
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        # Submit API call tasks and retrieve futures
                        futures = [
                            executor.submit(
                                ebird_api.get_recent_species_obs,
                                region_code,
                                species_code,
                                days_back,
                                headers=headers,
                            )
                            for species_code in needs_df["speciesCode"].unique()
                        ]
                        # Retrieve results from futures
                        results = [future.result() for future in futures]

                    region_needs_df = pd.concat(results, ignore_index=True)
                    region_loc_data = data.format_region_needs_data_for_map(
                        region_needs_df
                    )

                    st.subheader("Locations of all needed species observed:")
                    chart = visualise.map_deck(region_loc_data)
                    st.pydeck_chart(chart)

                    for location in sorted(region_needs_df["locName"].unique()):
                        location_data = region_needs_df.loc[
                            region_needs_df["locName"] == location
                        ]
                        location_data.reset_index(drop=True, inplace=True)
                        location_data = location_data.rename(
                            columns={
                                "comName": "Common Name",
                                "sciName": "Scientific Name",
                                "obsDt": "Date",
                                "howMany": "Count",
                            }
                        )

                        location_id = location_data["locId"][0]

                        location_link = ""
                        if not location_data["locationPrivate"][0]:
                            location_link = f"&emsp;&LongRightArrow; Hotspot Information: https://ebird.org/australia/hotspot/{location_id}<br>"

                        st.markdown(
                            f"<br>{location}:<br>"
                            + location_link
                            + f"&emsp;&LongRightArrow; Directions: <a href='https://maps.google.com/?q={location_data['lat'][0]},{location_data['lng'][0]}' target='_blank'>Google Maps</a>",
                            unsafe_allow_html=True,
                        )

                        st.dataframe(
                            location_data[
                                ["Common Name", "Scientific Name", "Date", "Count"]
                            ],
                            use_container_width=True,
                            hide_index=True,
                        )
                else:
                    st.info("No recent observations found for unseen species.")
    else:
        st.info(
            "Please select your preferences from the sidebar and upload a lifelist CSV file."
        )


if __name__ == "__main__":
    main()
