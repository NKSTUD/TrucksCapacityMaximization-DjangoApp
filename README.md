# Trucks Filling Rate Maximization - Django Application

This Django application optimizes the filling rate of trucks during transportation, ensuring efficient product allocation to maximize truck capacity usage.

## Code Overview

The core functionality lies in the [`views.py`](https://github.com/NKSTUD/Trucks-filling-rate-maximization-simple-django-web-app/blob/main/minimizer/views.py) file, which includes views and utility functions for data extraction, defining decision variables, and solving the optimization problem.

## Filling Rate Calculation

The filling rate is calculated using the `create_solution_table()` function in `views.py`, which determines the transported volume and filling rate for each truck and stores the data in a `table`, sorted by filling rate in descending order.

## Usage

1. Set up the environment with Python and Django.
2. Install the required dependencies:

   ```shell
   pip install -r requirements.txt
   ```
