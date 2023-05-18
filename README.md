# Trucks Filling Rate Maximization Django Application

This Django application implements a solution for maximizing the filling rate of trucks during transportation. The objective is to efficiently allocate products to trucks in order to utilize the available truck capacity effectively.

## Code Overview

The code consists of Django views that handle HTTP requests and responses. The key component is the `views.py` file, which contains the views and utility functions to extract data, define decision variables, and solve the optimization problem.

## Filling Rate Calculation

To calculate the filling rate for each truck, the application utilizes the `create_solution_table()` function defined in `views.py`. This function performs the following steps:

1. Initializes an empty `table` to store the truck inventory information.
2. For each `truck` in `trucks_per_type`:
   - Creates a `truck_inventory` list to store the inventory information of the current truck.
   - Initializes the `transported_volume` variable to keep track of the total volume of products transported by the truck.
   - For each `product` in `products`:
     - Appends the number of units of the current `product` carried by the `truck` to `truck_inventory`.
     - Updates the `transported_volume` by multiplying the number of units of the current `product` by its volume and adding it to the existing `transported_volume`.
   - Calculates the filling rate for the current `truck` by dividing the `transported_volume` by the capacity of the truck (`trucks_capacity[truck_type]`).
   - Appends the calculated filling rate to `truck_inventory`.
   - Appends the `truck_inventory` to the `table`.

The resulting `table` contains the truck inventory information sorted in descending order of filling rate.

## Usage

To use this Django application, follow these steps:

1. Set up the necessary environment with Python and Django.

2. Ensure that you have the required dependencies installed. Run the following command to install them:

   ```shell
   pip install -r requirements.txt
