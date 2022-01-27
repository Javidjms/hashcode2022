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


