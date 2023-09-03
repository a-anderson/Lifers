import pydeck as pdk
import pandas as pd


def map_deck(map_data):
    layer = pdk.Layer(
        "ScatterplotLayer",
        map_data,
        get_position=["lng", "lat"],
        get_fill_color=[0, 204, 136],
        pickable=True,
        opacity=0.8,
        radius_scale=1000,
        get_radius="num_species",
        radius_min_pixels=2,
        radius_max_pixels=50,
    )

    view_state = pdk.ViewState(
        latitude=map_data["lat"].mean(),
        longitude=map_data["lng"].mean(),
        zoom=5.5,
        bearing=0,
        pitch=0,
    )

    chart = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{locName}\n{tooltip_species}"},
    )
    return chart
