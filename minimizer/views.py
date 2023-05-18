from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pulp import LpVariable, LpInteger, LpBinary, LpProblem, LpMinimize, lpSum, LpStatus, value


@csrf_exempt
def index(request):
    context = {}
    if request.method == 'POST':
        number_of_products = request.POST.get('number_of_products', 0)
        number_of_trucks = request.POST.get('number_of_trucks', 0)
        if number_of_trucks.isdigit() and number_of_products.isdigit():
            number_of_products = request.session['number_of_products'] = int(number_of_products)
            number_of_trucks = request.session['number_of_trucks'] = int(number_of_trucks)
        else:
            number_of_products = 0
            number_of_trucks = 0

        context |= {
            'number_of_products': range(number_of_products),
            'number_of_trucks': range(number_of_trucks),
        }

    if request.htmx:
        return render(request, 'user-form.html', context)

    return render(request, 'index.html', context)


def extract_products(request, number_of_products):
    return [
        request.POST.get(f'product_{i + 1}', f'default_product{i + 1}')
        for i in range(number_of_products)
    ]


def extract_products_volumes(request, number_of_products):
    return {
        request.POST.get(f'product_{i + 1}', f'default_product{i + 1}'): float(
            request.POST.get(f'volume_{i + 1}', '0')
        )
        for i in range(number_of_products)
    }


def extract_products_demand(request, number_of_products):
    return {
        request.POST.get(f'product_{i + 1}', f'default_product{i + 1}'): int(
            request.POST.get(f'demand_product_{i + 1}', '0')
        )
        for i in range(number_of_products)
        if request.POST.get(f'demand_product_{i + 1}', '0').isdigit()
    }


def extract_trucks(request, number_of_trucks):
    return [
        request.POST.get(f'Truck_{i + 1}', f'default_truck_{i + 1}')
        for i in range(number_of_trucks)
    ]


def extract_trucks_capacity(request, number_of_trucks):
    return {
        request.POST.get(f'Truck_{i + 1}', f'default_truck{i + 1}'): float(
            request.POST.get(f'capacity_{i + 1}', '0')
        )
        for i in range(number_of_trucks)
    }


def extract_trucks_per_type(request, number_of_trucks):
    trucks_per_type = []
    for i in range(number_of_trucks):
        number_of_trucks_per_type = request.POST.get(f'Number_of_Truck_{i + 1}', '0')
        if number_of_trucks_per_type.isdigit():
            trucks_per_type.extend(
                f"{request.POST.get(f'Truck_{i + 1}', f'default_truck_{i + 1}')}_{j + 1}"
                for j in range(int(number_of_trucks_per_type))
            )
    return trucks_per_type


def define_decision_variables(products, trucks_per_type):
    x = LpVariable.dicts("X", (products, trucks_per_type), 0, None, LpInteger)
    y = LpVariable.dicts("Y", trucks_per_type, 0, 1, LpBinary)
    return x, y


def define_objective_function(x, y, trucks_per_type):
    prob = LpProblem("MinimizeTransportationCost", LpMinimize)
    prob += (
        lpSum([y[truck_per_type] for truck_per_type in trucks_per_type]),
        "number_of_trucks_used",
    )
    return prob


def add_constraints(prob, x, y, products, products_demand, products_volumes, trucks_per_type, trucks_capacity):
    for product in products:
        prob += (
            lpSum([x[product][truck_per_type] for truck_per_type in trucks_per_type]) == products_demand[product],
            f"sum_of_trucks_for_{product}",
        )

    for truck_per_type in trucks_per_type:
        truck_type_name = truck_per_type.split("_")[0] + "_" + truck_per_type.split("_")[1]
        prob += (
            lpSum([x[product][truck_per_type] * products_volumes[product] for product in products]) <= trucks_capacity[
                truck_type_name] * y[truck_per_type],
            f"sum_of_products_for_{truck_per_type}",
        )


def create_solution_table(trucks_per_type, products, products_volumes, trucks_capacity, x):
    table = []
    for truck in trucks_per_type:
        truck_inventory = [truck]
        transported_volume = 0
        for product in products:
            truck_inventory.append(value(x[product][truck]))
            transported_volume += value(x[product][truck]) * products_volumes[product]
        truck_inventory.append(
            round(transported_volume / trucks_capacity[truck.split("_")[0] + "_" + truck.split("_")[1]] * 100, 2)
        )
        table.append(truck_inventory)
    return sorted(table, key=lambda x: x[-1], reverse=True)


@csrf_exempt
def solution(request):
    context = {}
    if request.method == 'POST':
        number_of_products = request.session['number_of_products']
        number_of_trucks = request.session['number_of_trucks']
        products = extract_products(request, number_of_products)
        products_volumes = extract_products_volumes(request, number_of_products)
        products_demand = extract_products_demand(request, number_of_products)
        trucks = extract_trucks(request, number_of_trucks)
        trucks_capacity = extract_trucks_capacity(request, number_of_trucks)
        trucks_per_type = extract_trucks_per_type(request, number_of_trucks)
        x, y = define_decision_variables(products, trucks_per_type)
        prob = define_objective_function(x, y, trucks_per_type)
        add_constraints(prob, x, y, products, products_demand, products_volumes, trucks_per_type, trucks_capacity)
        prob.solve()
        status = LpStatus[prob.status]
        context["status"] = status
        context["products"] = products
        if status == "Optimal":
            table = create_solution_table(trucks_per_type, products, products_volumes, trucks_capacity, x)
            context["table"] = sorted(table, key=lambda x: x[-1], reverse=True)
            context["number_of_trucks_used"] = value(prob.objective)
    return render(request, 'solution.html', context)
