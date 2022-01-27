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


