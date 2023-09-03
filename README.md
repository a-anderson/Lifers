# Lifers: eBird Needs Finder

This Streamlit application helps birdwatchers find bird species in their region of interest using the eBird API.

## Table of Contents

-   [About](#about)
-   [Features](#features)
-   [Getting Started](#getting-started)
-   [Usage](#usage)
-   [Installation](#installation)
-   [Contributing](#contributing)
-   [License](#license)

## About

The Lifers app is designed to help birdwatchers locate recently observed bird species. It uses the [eBird API](https://documenter.getpostman.com/view/664302/S1ENwy59) to retrieve recent observations and cross-references them with your lifelist to highlight species you've never seen.

## Features

-   Select the region you want to find recently observed bird species.
-   Upload your eBird lifelist to compare against recent observations.
-   Visualize bird species distribution on an interactive map.
-   Access species information and observation details.

## Getting Started

To use the Lifers app, you'll need:

1. A valid eBird account.
2. An eBird API token. If you don't have an API token you can apply for one at the [eBird keygen page](https://ebird.org/api/keygen).
3. A CSV file containing your birdwatching lifelist.
   The CSV file can be downloaded from your [Life List page](https://ebird.org/lifelist?time=life&r=world). Please do not change the structure or contents of the CSV file before loading it into the app.

## Usage

1. Set your region preferences (country, subregion).
2. Upload your birdwatching lifelist CSV file.
3. Choose the number of recent days to retrieve observations.
4. Click "Find Species" to reveal observations of birds that are not in your life list.
5. Explore species details, observation locations, and more. Please note that private locations do not have hotspot links in eBird.

## Installation

1. Clone this repository.
2. Install the required packages:
    - Install Python ≥ 3.11
    - [Install Poetry](https://python-poetry.org/docs/)
    - Move to the Lifers folder and run `poetry init`
3. Set your eBird API passkey as an environment variable:

    `export EBIRD_API_TOKEN=<your_ebird_api_passkey_here>`

4. Run the Lifers app:

    `poetry run streamlit run lifers/lifers.py`

    OR if you would prefer to set your token at the same time as running the app:

    `EBIRD_API_TOKEN=<your_ebird_api_passkey_here> poetry run streamlit run lifers/lifers.py`

## License

This project is licensed under the [MIT License](LICENSE).
