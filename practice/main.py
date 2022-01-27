import sys
import itertools


class Client:
    def __init__(self, id, liked_ingredients, disliked_ingredients):
        self.id = id
        self.liked_ingredients = liked_ingredients
        self.disliked_ingredients = disliked_ingredients

    def approve_pizza(self, ingredients):
        has_approved = True
        for liked_ingredient in self.liked_ingredients:
            if liked_ingredient not in ingredients:
                has_approved = False
                break

        for disliked_ingredient in self.disliked_ingredients:
            if disliked_ingredient in ingredients:
                has_approved = False
                break
        return has_approved

    def __repr__(self):
        return "Client #{}".format(self.id)


def get_scoring(clients, ingredients):
    approved_client_count = 0
    for client in clients:
        is_potential_client = client.approve_pizza(ingredients)
        if is_potential_client:
            approved_client_count += 1
    return approved_client_count


def get_clients_and_ingredients_from_file(filename):
    clients = []
    ingredients = set()
    with open(filename, 'r') as f:
        # Parse the initial first line
        potential_client_count = int(f.readline())

        for i in range(potential_client_count):
            # Parse the first line for the liked ingredient line
            line = f.readline().split()
            liked_ingredients = line[1:]
            for ingredient in liked_ingredients:
                ingredients.add(ingredient)

            # Parse the second line for the disliked ingredient line
            line = f.readline().split()
            disliked_ingredients = line[1:]
            for ingredient in disliked_ingredients:
                ingredients.add(ingredient)

            client = Client(i, liked_ingredients, disliked_ingredients)
            clients.append(client)
        ingredients = list(ingredients)
    return clients, ingredients


def plot_ingredients(clients, ingredients):
    print('Ingredients', ingredients)
    for i, client in enumerate(clients):
        output = ''
        for ingredient in ingredients:
            if ingredient in client.liked_ingredients:
                output += 'L'
            elif ingredient in client.disliked_ingredients:
                output += 'D'
            else:
                output += '.'
        print('CLIENT {}: {}'.format(i, output))


def plot_potential_clients(clients, chosen_ingredients):
    for i, client in enumerate(clients):
        is_potential_client = client.approve_pizza(chosen_ingredients)
        print('CLIENT {}: Results : {} - {} || {}'.format(
            i,
            is_potential_client,
            client.liked_ingredients,
            client.disliked_ingredients,
        ))


def choose_ingredients_solver_brute(clients, ingredients):
    # Generate all combinations with itertools
    combinations = []
    for i in range(1, len(ingredients)+1):
        combinations += list(itertools.combinations(ingredients, i))

    best_combination = None
    best_approved_client_count = 0
    # Iterate all combination and keep the max approved_client_count
    for combination in combinations:
        approved_client_count = get_scoring(clients, combination)

        if best_approved_client_count < approved_client_count:
            best_combination = combination
            best_approved_client_count = approved_client_count
    return (best_combination, best_approved_client_count)


def choose_ingredients_solver_brute_bis(clients, ingredients):
    # Generate the n-1 length combination
    depth = 0
    length = len(ingredients) - depth
    combinations = list(itertools.combinations(ingredients, length))

    best_combination = None
    best_approved_client_count = 0
    # Iterate all combination and keep the max approved_client_count
    for combination in combinations:
        approved_client_count = get_scoring(clients, combination)

        if best_approved_client_count < approved_client_count:
            best_combination = combination
            best_approved_client_count = approved_client_count
    return (best_combination, best_approved_client_count)


def choose_ingredients_solver_with_count_dict(clients, ingredients):
    liked_ingredients_count_dict = {}
    disliked_ingredients_count_dict = {}

    # Generate intial hashmap with zeros
    for ingredient in ingredients:
        liked_ingredients_count_dict[ingredient] = 0
        disliked_ingredients_count_dict[ingredient] = 0

    # Iterate each clients in order to fill hashmap liked and disliked values
    for client in clients:
        for liked_ingredient in client.liked_ingredients:
            liked_ingredients_count_dict[liked_ingredient] += 1

        for disliked_ingredient in client.disliked_ingredients:
            disliked_ingredients_count_dict[disliked_ingredient] += 1

    # Keep ingredients that the ratio like/dislike is highest
    chosen_ingredients = []
    for ingredient in ingredients:
        if liked_ingredients_count_dict[ingredient] \
          > disliked_ingredients_count_dict[ingredient]:
            chosen_ingredients.append(ingredient)

    # Count the approved client with the generated chosen_ingredients
    approved_client_count = get_scoring(clients, chosen_ingredients)
    return (chosen_ingredients, approved_client_count)


def choose_ingredients_solver_with_count_dict_bis_helper(
    clients,
    ingredients,
    min_max_approved_client_count,
):
    min_approved_client_count = min_max_approved_client_count["min"]
    max_approved_client_count = min_max_approved_client_count["max"]
    # print(len(clients), len(ingredients), min_approved_client_count, max_approved_client_count)

    # Count the approved client with the generated ingredients
    approved_client_count = get_scoring(clients, ingredients)

    if approved_client_count < min_approved_client_count:
        return (ingredients, approved_client_count)

    if approved_client_count > max_approved_client_count:
        min_max_approved_client_count["max"] = approved_client_count

    liked_ingredients_count_dict = {}
    disliked_ingredients_count_dict = {}

    # Generate intial hashmap with empty list
    for ingredient in ingredients:
        liked_ingredients_count_dict[ingredient] = 0
        disliked_ingredients_count_dict[ingredient] = 0

    # Iterate each clients in order to fill hashmap liked and disliked values
    for client in clients:
        for ingredient in client.liked_ingredients:
            if ingredient in ingredients:
                liked_ingredients_count_dict[ingredient] += 1

        for ingredient in client.disliked_ingredients:
            if ingredient in ingredients:
                disliked_ingredients_count_dict[ingredient] += 1

    # Keep ingredients that the ratio like/dislike is negative
    ingredients_to_remove = []
    for ingredient in ingredients:
        if disliked_ingredients_count_dict[ingredient] \
          and (
              liked_ingredients_count_dict[ingredient] <=
              disliked_ingredients_count_dict[ingredient]
          ):
            ingredients_to_remove.append(ingredient)

    best_combination = ingredients
    best_approved_client_count = approved_client_count
    if len(ingredients_to_remove):
        for ingredient_to_remove in ingredients_to_remove:
            new_ingredients = [i for i in ingredients if i not in [ingredient_to_remove]]
            (chosen_ingredients, approved_client_count) = \
                choose_ingredients_solver_with_count_dict_bis_helper(
                    clients,
                    new_ingredients,
                    min_max_approved_client_count,
                )
            if best_approved_client_count < approved_client_count:
                best_combination = chosen_ingredients
                best_approved_client_count = approved_client_count
    return (best_combination, best_approved_client_count)


def choose_ingredients_solver_with_count_dict_bis_2_helper(
    clients,
    ingredients,
    approved_client_count,
    liked_ingredients_count_dict,
    disliked_ingredients_count_dict,
):
    # Keep ingredients that the ratio like/dislike is negative
    lowest_ratio = 0
    ingredient_to_remove = None
    for ingredient in ingredients:
        if len(disliked_ingredients_count_dict[ingredient]):
            ratio = len(liked_ingredients_count_dict[ingredient]) - \
                len(disliked_ingredients_count_dict[ingredient])
            if ratio <= 0 and ratio <= lowest_ratio:
                lowest_ratio = ratio
                ingredient_to_remove = ingredient

    if ingredient_to_remove:
        # Remove ingredients
        new_ingredients = set(ingredients)
        new_ingredients.remove(ingredient_to_remove)

        # Remove clients
        new_clients = set(clients)
        clients_to_remove = \
            liked_ingredients_count_dict[ingredient_to_remove]
        clients_to_add = \
            disliked_ingredients_count_dict[ingredient_to_remove]

        for client_to_remove in clients_to_remove:
            new_clients.remove(client_to_remove)

        # Update approved_client_count
        new_approved_client_count = \
            approved_client_count + len(clients_to_add) - len(clients_to_remove)

        # Update count_dict
        new_liked_ingredients_count_dict = dict(liked_ingredients_count_dict)
        new_disliked_ingredients_count_dict = dict(disliked_ingredients_count_dict)

        new_liked_ingredients_count_dict.pop(ingredient_to_remove)
        new_disliked_ingredients_count_dict.pop(ingredient_to_remove)

        for client_to_remove in clients_to_remove:
            for ingredient in client_to_remove.liked_ingredients:
                if ingredient in new_liked_ingredients_count_dict:
                    new_liked_ingredients_count_dict[ingredient] = \
                        list(new_liked_ingredients_count_dict[ingredient])
                    new_liked_ingredients_count_dict[ingredient].remove(client_to_remove)

            for ingredient in client_to_remove.disliked_ingredients:
                if ingredient in new_disliked_ingredients_count_dict:
                    new_disliked_ingredients_count_dict[ingredient] = \
                        list(new_disliked_ingredients_count_dict[ingredient])
                    new_disliked_ingredients_count_dict[ingredient].remove(client_to_remove)

        return choose_ingredients_solver_with_count_dict_bis_2_helper(
            new_clients,
            new_ingredients,
            new_approved_client_count,
            new_liked_ingredients_count_dict,
            new_disliked_ingredients_count_dict,
        )
    else:
        return (
            clients,
            ingredients,
            approved_client_count,
            liked_ingredients_count_dict,
            disliked_ingredients_count_dict,
        )


def choose_ingredients_solver_with_count_dict_bis(clients, ingredients):
    # Count the approved client with the generated ingredients
    initial_approved_client_count = get_scoring(clients, ingredients)
    return choose_ingredients_solver_with_count_dict_bis_helper(
        clients,
        ingredients,
        {
            "min": initial_approved_client_count,
            "max": initial_approved_client_count,
        }
    )


def choose_ingredients_solver_with_count_dict_bis_2(clients, ingredients):
    clients = set(clients)
    ingredients = set(ingredients)
    # Count the approved client with the generated ingredients
    initial_approved_client_count = get_scoring(clients, ingredients)

    liked_ingredients_count_dict = {}
    disliked_ingredients_count_dict = {}

    # Generate intial hashmap with empty list
    for ingredient in ingredients:
        liked_ingredients_count_dict[ingredient] = set()
        disliked_ingredients_count_dict[ingredient] = set()

    # Iterate each clients in order to fill hashmap liked and disliked values
    for client in clients:
        for ingredient in client.liked_ingredients:
            if ingredient in ingredients:
                liked_ingredients_count_dict[ingredient].add(client)

        for ingredient in client.disliked_ingredients:
            if ingredient in ingredients:
                disliked_ingredients_count_dict[ingredient].add(client)

    results = choose_ingredients_solver_with_count_dict_bis_2_helper(
        clients,
        ingredients,
        initial_approved_client_count,
        liked_ingredients_count_dict,
        disliked_ingredients_count_dict,
    )
    return (list(results[1]), results[2])


def choose_ingredients_solver_with_chain(clients, ingredients):
    clients = set(clients)
    ingredients = set(ingredients)

    approved_client_count = 0
    current_ingredients = set()
    for client in clients:
        has_break = False
        for disliked_ingredient in client.disliked_ingredients:
            if disliked_ingredient in current_ingredients:
                has_break = True
                break

        if has_break:
            continue

        for liked_ingredient in client.liked_ingredients:
            current_ingredients.add(liked_ingredient)
        approved_client_count += 1
    return (current_ingredients, approved_client_count)


def choose_ingredients_solver_with_chain_bis(clients, ingredients):
    clients = set(clients)
    ingredients = set(ingredients)

    approved_client_count = 0
    current_ingredients = set()
    forbidden_ingredients = set()
    for client in clients:
        has_break = False
        for disliked_ingredient in client.disliked_ingredients:
            if disliked_ingredient in current_ingredients:
                has_break = True
                break

        if has_break:
            continue

        for liked_ingredient in client.liked_ingredients:
            if liked_ingredient in forbidden_ingredients:
                has_break = True
                break

        if has_break:
            continue

        for disliked_ingredient in client.disliked_ingredients:
            forbidden_ingredients.add(disliked_ingredient)

        for liked_ingredient in client.liked_ingredients:
            current_ingredients.add(liked_ingredient)
        approved_client_count += 1
    return (current_ingredients, approved_client_count)


def write_file(chosen_ingredients, filename):
    with open(filename, 'w') as f:
        chosen_ingredients_length = len(chosen_ingredients)
        f.write('{} '.format(chosen_ingredients_length))
        for ingredient in chosen_ingredients:
            f.write('{} '.format(ingredient))


def main():
    if len(sys.argv) < 3:
        sys.exit('Syntax: %s <filename> <output>' % sys.argv[0])

    print('Running on file: %s' % sys.argv[1])
    clients, ingredients = get_clients_and_ingredients_from_file(sys.argv[1])

    # plot_ingredients(clients, ingredients)

    try:
        (chosen_ingredients, potential_client_count) =\
            choose_ingredients_solver_with_chain_bis(clients, ingredients)
    except KeyboardInterrupt:
        pass

    print('chosen_ingredients', chosen_ingredients)
    print('potential_client_count', potential_client_count)
    # plot_potential_clients(clients, chosen_ingredients)

    write_file(chosen_ingredients, sys.argv[2])


if __name__ == '__main__':
    main()
