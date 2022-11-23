"""Remove ingredient from shopping list feature tests."""
import json
from project.account import *
from project.db import RecipeRepo
from project.ingredient_query import get_ingredients_of_recipe
from project.shopping_list import get_shopping_list_of_account
from pytest_bdd import (
    given,
    scenario,
    then,
    when,
    parsers
)


@scenario('features/Remove_Ingredient_From_Shopping_List.feature',
          'Attempt to remove item while not logged in (Error Flow)')
def test_attempt_to_remove_item_while_not_logged_in_error_flow():
    """Attempt to remove item while not logged in (Error Flow)."""


@scenario('features/Remove_Ingredient_From_Shopping_List.feature',
          'Attempt to remove non-existent ingredient (Error Flow)')
def test_attempt_to_remove_nonexistent_ingredient_error_flow():
    """Attempt to remove non-existent ingredient (Error Flow)."""


@scenario('features/Remove_Ingredient_From_Shopping_List.feature', 'Logged in user removes ingredient (Normal Flow)')
def test_logged_in_user_removes_ingredient_normal_flow():
    """Logged in user removes ingredient (Normal Flow)."""


@given(parsers.parse('the following entries exist in the shopping list for user "{username}"\n{table_data}'))
def the_following_entries_exist_in_the_shopping_list_for_user_abc(postgresql, app, username, table_data):
    with app.app_context():
        user_id = search_account_by_name(username)[0]

        table_data = json.loads(table_data)[1:]
        cur = postgresql.cursor()
        for (ingredient_id, name, quantity) in table_data:
            cur.execute("INSERT INTO shopping_items VALUES (%s, %s);", (user_id, ingredient_id))
        postgresql.commit()

        (shopping_list, err) = get_shopping_list_of_account(user_id)
        assert len(shopping_list) == len(table_data)


@given(parsers.parse('the recipe "{recipe_title}" exists in the system'))
def the_recipe_stew_exists_in_the_system(app, recipe_title):
    with app.app_context():
        recipe_id = RecipeRepo.insert_recipe(recipe_title, 1, None, None, "", [])
        assert recipe_id is not None


@given(parsers.parse('user "{username}" with password "{password}" exists in the system'))
def user_abc_with_password_123_exists_in_the_system(app, username, password):
    with app.app_context():
        if search_account_by_name(username):
            assert True
        else:
            res = db_save_account(username, "dummy@dummy.com", password)
            assert res[1] is None


@given(parsers.parse('the recipe "stew" has the following ingredients\n{table_data}'))
def the_recipe_stew_has_the_following_ingredients(postgresql, app, table_data):
    with app.app_context():
        table_data = json.loads(table_data)[1:]
        cur = postgresql.cursor()
        for (ingredient_id, name, quantity) in table_data:
            cur.execute("INSERT INTO ingredients VALUES (%s, %s, %s, %s);", (ingredient_id, name, quantity, 1))
        postgresql.commit()

        ingredients = get_ingredients_of_recipe(1)
        assert len(ingredients) == len(table_data)


@given('the user is not logged into the system')
def the_user_is_not_logged_into_the_system(client):
    with client.session_transaction() as session:
        if "id" in session:
            client.get('/logout')
        assert not ("id" in session)


@given(parsers.parse('user "{name}" is logged into the system'))
def user_abc_is_logged_into_the_system(client, name):
    user = search_account_by_name(name)
    payload = {'email': user[2], 'password': 123}
    client.post('/login', data=payload)
    with client.session_transaction() as session:
        assert session["id"] == user[0]


@when(parsers.parse('attempting to remove the ingredient with id "{ingredient_id}"'))
def attempting_to_remove_the_ingredient_with_id_8(client, ingredient_id):
    client.post(f'/api/shopping_list/remove_ingredient/{ingredient_id}')


@when(parsers.parse('attempting to remove the ingredient with id "{ingredient_id}"'))
def attempting_to_remove_the_ingredient_with_id_9(client, ingredient_id):
    client.post(f'/api/shopping_list/remove_ingredient/{ingredient_id}')


@then('the "not logged in" error message is issued')
def the_not_logged_in_error_message_is_issued(client):
    with client.session_transaction() as session:
        assert not ("id" in session)


@then(parsers.parse('the user "{username}" has the following ingredients in their shopping list\n{table_data}'))
def the_user_abc_has_the_following_ingredients_in_their_shopping_list(app, username, table_data):
    with app.app_context():
        table_data = json.loads(table_data)[1:]
        user_id = search_account_by_name(username)[0]
        (shopping_list, err) = get_shopping_list_of_account(user_id)
        assert len(shopping_list) == len(table_data)


# Response messages from API not supported here
@then('the "item not in shopping list" error message is issued')
def the_item_not_in_shopping_list_error_message_is_issued():
    """the "item not in shopping list" error message is issued."""
