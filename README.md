# Industrial and Commercial Electricity Tariffs in the US

[![codecov](https://codecov.io/gh/we3lab/industrial-electricity-tariffs/graph/badge.svg?token=M1WHXPGH2F)](https://codecov.io/gh/we3lab/industrial-electricity-tariffs)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16739989.svg)](https://doi.org/10.5281/zenodo.16739989)

The most recent version of the dataset can be found in `industrial-electricity-tariffs.zip` at [Releases](https://github.com/we3lab/industrial-electricity-tariffs/releases).

We use a data format specified by Chapin et al. in [Electricity and natural gas tariffs at United States wastewater treatment plants](https://doi.org/10.1038/s41597-023-02886-6) that can represent all the complexities of electricity tariffs across the United States (tiered charges, multiple peak periods, daily demand charges, etc.).

## Data Processing Pipeline

The automated data processing pipeline releases a new version of the dataset every month to incorporate the most recent data from the [United States Utility Rate Database (USURDB)](https://apps.openei.org/USURDB/).

The specific GH Actions workflow defined by [process-tariff.yml](https://github.com/we3lab/industrial-electricity-tariffs/blob/main/.github/workflows/process-tariff.yml) conducts the following steps:

1. Raw data is downloaded from USURDB with [download.py](https://github.com/we3lab/industrial-electricity-tariffs/blob/main/code/download.py)
1. Downloaded data is filtered by sector, service type, and cutoff date  with [filter.py](https://github.com/we3lab/industrial-electricity-tariffs/blob/main/code/filter.py)
1. Filtered data is converted from USURDB to our format with [convert.py](https://github.com/we3lab/industrial-electricity-tariffs/blob/main/code/convert.py)
1. Converted data is merged with tariffs we had collected manually in [Electricity and natural gas tariffs at United States wastewater treatment plants](https://doi.org/10.1038/s41597-023-02886-6) using [merge.py](https://github.com/we3lab/industrial-electricity-tariffs/blob/main/code/merge.py)
1. The final dataset is validated using the validation algorithm from [Electricity and natural gas tariffs at United States wastewater treatment plants](https://doi.org/10.1038/s41597-023-02886-6) implemented in [validate.py](https://github.com/we3lab/industrial-electricity-tariffs/blob/main/code/validate.py)

Two versions of the dataset are created by default:
1. Bundled (i.e., generation + delivery)
1. Delivery only
 
However, a user could run the data processing pipeline with custom filtering arguments to create a version of the dataset
specific to their needs. Users can filter along the following dimensions:

- *Sector*: the consumer classification for this tariff
  - Options: "Industrial", "Commercial", or "Residential"
  - Default: ["Industrial", "Commercial"]
- *Service Type*: which components of generation, transmission, and delivery the tariff includes
  - Options: "Bundled", "Delivery", or "Delivery with Standard Offer"
  - Default: ["Bundled", "Delivery with Standard Offer"] for bundled and ["Delivery"] for delivery only
- *Cutoff Date*: the date before which this tariff must have come into effect and after which the tariff must still be in effect (i.e., `startdate <= cutoff_date` and `enddate >= cutoff_date`)
  - Options: any valid `datetime`
  - Default: `datetime.datetime.today()`

## Data Records
Each release of the data should have the following files (after unzipping `industrial-electricity-tariffs.zip`):
- `bundled` folder
- `delivery_only` folder
- `metadata_bundled.csv`
- `metadata_delivery_only.csv`
- `rejected_bundled.csv`
- `rejected_delivery_only.csv`

The `bundled` and `delivery` only folders each contain tariff data formatted as below. 
The corresponding metadata and reject lists are also described in subsequent sections.

### Tariff Format
Each CSV file in `bundled` or `delivery_only` folders is given the name of the USURDB label (or CWNS Number if from [Chapin et al. (2024)](https://doi.org/10.1038/s41597-023-02886-6)) corresponding to that tariff. Each row of the tariff structure corresponds to a different tariff, so if a municipality with a flat electricity tariff would have only one row whereas a municipality with a complex tariff structure would have many rows. The electricity and natural gas tariff data has the following columns:
-	**utility**: type of utility, i.e. “electric” or “gas”
-	**type**: type of charge. Options are “customer”, “demand”, and “energy”
-   **assessed**: time period on which demand charges are assessed. Either "daily" or "monthly", but defaults to "monthly" if no value is provided
-	**period**: name for the charge period. Only relevant for demand charges, since there can be multiple concurrent demand charges, i.e. a charge named “maximum” which is in effect 24 hours a day vs. a charge named “on-peak” which is only in effect during afternoon hours.
-	**basic_charge_limit (imperial)**: consumption limit above which the charge takes effect in imperial units (i.e., kWh of electricity and therms of natural gas). Default is 0. A limit is in effect until another limit supersedes it, e.g. if there are two charges, Charge 1 with basic_charge_limit = 0 and Charge 2 with basic_charge_limit = 1000, Charge 1 will be in effect until 1000 units are delivered, and Charge 2 will be in effect thereafter.
-	**basic_charge_limit (metric)**: consumption limit above which the charge takes effect in metric units (i.e., kWh of electricity and cubic meters of natural gas). Default is 0.  A limit is in effect until another limit supersedes it, e.g. if there are two charges, Charge 1 with basic_charge_limit = 0 and Charge 2 with basic_charge_limit = 1000, Charge 1 will be in effect until 1000 units are delivered, and Charge 2 will be in effect thereafter.
-	**month_start**: first month during which this charge occurs (1-12)
- **month_end**: last month during which this charge occurs (1-12)
-	**hour_start**: hour at which this charge starts (0-24)
-	**hour_end**: hour at which this charge ends (0-24)
-	**weekday_start**: first weekday on which this charge occurs (0 = Monday to 6 = Sunday)
-	**weekday_end**: last weekday on which this charge occurs (0 = Monday to 6 = Sunday)
-	**charge (imperial)**: cost represented as a float in imperial units. I.e., "$/month", "$/kWh", "$/kW", "$/therm", and "$/therm/hr" for customer charges, electric energy charges, electric demand charges, natural gas energy charges, and natural gas demand charges, respectively
-   **charge (metric)**: cost represented as a float in metric units. I.e., "$/month", "$/kWh", "$/kW", "$/m3", and "$/m3/hr" for customer charges, electric energy charges, electric demand charges, natural gas energy charges, and natural gas demand charges, respectively. A conversion factor of 2.83168 cubic meters to 1 therm was used.
-	**units**: units of the charge, e.g. “$/kWh”. If units are different between imperial and metric then imperial is listed followed by metric. E.g., "$/therm or $/m3".
-	**Notes**: any comments the authors felt would help explain unintuitive decisions in data collection or formatting

### Metadata Format
There should be both `metadata_bundled.csv` and `metadata_delivery_only.csv`.
The metadata spreadsheets contain information on each of the tariffs in their respective folders using the following format: 

- **label**: the label for this tariff from the USURDB database
- **eiaid**: the U.S. Energy Information Administration (EIA) identifier for the utility
- **name**: the name of this tariff. E.g., "Rate 50 - Commercial GSA-2 (51-1000 kW)"
- **utility**: the name of the electric utility. E.g., "Public Service Co of Colorado"
- **source**: link to the original source of this data, such as PDF or utility website
- **zipcode**: ZIP code of the utility that provides service under this tariff 
- **state**: the state for this tariff service area 
- **latitude**: estimated latitude for geospatial visualization. Converted from `zipcode` using [pgeocode](https://pgeocode.readthedocs.io/en/latest/)
- **longitude**: estimated longitude for geospatial visualization. Converted from `zipcode` using [pgeocode](https://pgeocode.readthedocs.io/en/latest/)
- **notes**: notes about this tariff from USURDB

### Reject List Format
The reject list provides a list of tariffs that were filtered and converted, but rejected as invalid by [validate.py](https://github.com/we3lab/industrial-electricity-tariffs/blob/main/code/validate.py). As such, it is a simple one-column spreadsheet:

- **tariff_id**: the ID of the rejected tariff. Usually this is the USURDB label, but if from [Chapin et al. (2024)](https://doi.org/10.1038/s41597-023-02886-6) then this is CWNS Number.
- **reason**: the reason why the tariff was rejected as invalid 

## Tests

To execute the tests, run the following command from the top level of the repository:

```python
python -m pytest tests
```

## Attribution & Acknowledgements

Casey S. Chen created the data conversion code under the guidance of Akshay K. Rao, Adhithyan Sakthivelu, Fletcher T. Chapin, and Meagan S. Mauter.

We are working for a publication accompanying this data set, and will add the citation to attribute once that is published. 


In the meantime, you can cite the dataset directly as described in [CITATION.cff](https://github.com/we3lab/valuing-flexibility-from-water/blob/main/CITATION.cff) or in `BibTeX` format:

```
@misc{chapin2025industrial,
  author={Chapin, Fletcher T.
  and Rao, Akshay K.
  and Sakthivelu, Adhithyan
  and Chen, Casey S.
  and Mauter, Meagan S.},
  title={Industrial and Commercial Electricity Tariffs in the United States},
  year={2025},
  month={Aug},
  day={1},
  version={2025.08.01},
  doi={10.5281/zenodo.16739989},
  url={https://github.com/we3lab/industrial-electricity-tariffs}
}
```

We also recommend that you cite the data descriptor from Nature Scientific Data where the data format was originally published:

&nbsp; Chapin, F.T., Bolorinos, J. & Mauter, M.S. Electricity and natural gas tariffs at United States wastewater treatment plants. *Sci Data* **11**, 113 (2024). DOI: [10.1038/s41597-023-02886-6](https://doi.org/10.1038/s41597-023-02886-6)

In `BibTeX` format:

```
@Article{chapin2024electricity,
  author={Chapin, Fletcher T.
  and Bolorinos, Jose
  and Mauter, Meagan S.},
  title={Electricity and natural gas tariffs at United States wastewater treatment plants},
  journal={Scientific Data},
  year={2024},
  month={Jan},
  day={23},
  volume={11},
  number={1},
  pages={113},
  abstract={Wastewater treatment plants (WWTPs) are large electricity and natural gas consumers with untapped potential to recover carbon-neutral biogas and provide energy services for the grid. Techno-economic analysis of emerging energy recovery and management technologies is critical to understanding their commercial viability, but quantifying their energy cost savings potential is stymied by a lack of well curated, nationally representative electricity and natural gas tariff data. We present a dataset of electricity tariffs for the 100 largest WWTPs in the Clean Watershed Needs Survey (CWNS) and natural gas tariffs for the 54 of 100 WWTPs with on-site cogeneration. We manually collected tariffs from each utility's website and implemented data checks to ensure their validity. The dataset includes facility metadata, electricity tariffs, and natural gas tariffs (where cogeneration is present). Tariffs are current as of November 2021. We provide code for technical validation along with a sample simulation.},
  issn={2052-4463},
  doi={10.1038/s41597-023-02886-6},
  url={https://doi.org/10.1038/s41597-023-02886-6}
}
```

This work was supported by the following grants and programs:

- Stanford Woods Institute [Mentoring Undergraduate in Interdisciplinary Research (MUIR)](https://woods.stanford.edu/educating-leaders/education-leadership-programs/mentoring-undergraduates-interdisciplinary-research) program
- [Department of Energy, the Office of Energy Efficiency and Renewable Energy, Advanced Manufacturing Office](https://www.energy.gov/eere/ammto/advanced-materials-and-manufacturing-technologies-office) (grant number DE-EE0009499)
- [National Alliance for Water Innovation (NAWI)](https://www.nawihub.org/) (grant number UBJQH - MSM)


The views and opinions of authors expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof. Neither the United States Government nor any agency thereof, nor any of their employees, makes any warranty, express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness of any information, apparatus, product, or process disclosed, or represents that its use would not infringe privately owned rights.
