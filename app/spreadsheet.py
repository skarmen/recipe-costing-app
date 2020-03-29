import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from .utils import get_a1_notation
from datetime import datetime, date
import threading
# import ipdb;ipdb.set_trace()

SHEET_NAME = "recipe-costing-public"

def get_client(sheet_name=SHEET_NAME):
    """
    Connect sheets with the web app
    Use Google Sheets & Python Auth
    """
    # use creds to create a client to interact with the Google Drive API
    scope = [
        "https://www.googleapis.com/auth/drive",
        "https://spreadsheets.google.com/feeds",
    ]
    # See if an environment variable called GOOGLE_CRED is present
    # If so use that otherwise use file based credentials.
    creds_env = os.environ.get("GOOGLE_CRED")
    if creds_env:
        # Here instead of reading a file we parse the json from the str & then
        # use the dictionary method for google auth
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(creds_env), scope
        )
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "client_secret.json"
            ),
            scope
        )

    client = gspread.authorize(creds)

    # Extract and print all of the values
    # pprint(records[0:2]) # e is a list of dictionaries
    from pprint import pprint
    # pprint(dir(client))
    # print(client.list_spreadsheet_files())
    # Find a workbook by name and open the first sheet
    client = client.open(sheet_name)
    return client


client = get_client()


def get_recipe_info(request_form_dict):
    """Gets the basic recipe info which the user enters in the web form"""
    # return dict which need to be unpacked in order to be used
    # in other functions using (**kwargs)
    return {
        "date": request_form_dict["date"][0],
        "recipe_name": request_form_dict["recipe-name"][0],
        "recipe_group": request_form_dict["recipe-group"][0],
        "recipe_yield_qty": request_form_dict["yield-qty"][0],
        "recipe_yield_units": request_form_dict["yield-units"][0],
        "recipe_ingredients": request_form_dict["ingredient"],
        "ingredients_qty": request_form_dict["recipe-qty"],
        "ingredients_units": request_form_dict["units"],
        "ingredients_notes": request_form_dict["notes"],
    }


def create_temp_recipe_sheet(request_form_dict):
    """
    Triggered by "Submitt" Button from add_recipe_to_sheet()
    Duplicates the master template sheet when the user selects exisitng
    recipe group from the dropdown menu (ALWAYS) - program's default behaviour
    Temp sheet will be deleted when recipe is copied to correct group (sheet)
    """
    recipe_info = get_recipe_info(request_form_dict)
    recipe_name = recipe_info["recipe_name"]
    master_template_sheet = client.worksheet("recipe-template")
    temp_recipe_sheet = master_template_sheet.duplicate(
        None, None, recipe_name
    )
    return temp_recipe_sheet


def create_recipe_group_sheet(new_recipe_group_input):
    """
    Triggered by "Create New Recipe Group" Button
    Duplicates the 'empty-template' worksheet when the user creates new
    recipe group
    """
    empty_template_sheet = client.worksheet("empty-template")
    # user cancel the prompt request for new group the sheet won't be duplicate
    if new_recipe_group_input == "":
        print("new_recipe_group_input_lower:", new_recipe_group_input)
        return
    else:
        new_recipe_group_sheet = empty_template_sheet.duplicate(
            None, None, new_recipe_group_input
        )
        print("new_recipe_group_sheet:", new_recipe_group_sheet)
    return new_recipe_group_sheet


def copy_temp_sheet(
    temp_recipe_sheet,
    recipe_group_sheet,
    value_render_option="FORMATTED_VALUE"
):
    """Copy contents from souce sheet to target sheet, including formulas"""

    temp_recipe_sheet_title = temp_recipe_sheet.title
    print("temp_recipe_sheet_title:", temp_recipe_sheet_title)
    # list of list static values, get_all_values() to determine the range of
    # the sheet when insertng
    temp_sheet_static_values = temp_recipe_sheet.get_all_values()
    print("temp_sheet_static_values :", temp_sheet_static_values)

    # len of outer list [[], []] = 2 rows
    num_rows = len(temp_sheet_static_values)
    # len of inner list [[1,2,3]] = 3 cols
    num_col = len(temp_sheet_static_values[0])
    start_row_number = 1
    start_col_number = 1
    end_row_number = num_rows
    end_col_number = num_col

    a1_notation = get_a1_notation(
        start_row_number,
        start_col_number,
        end_row_number,
        end_col_number,
        temp_recipe_sheet_title,
    )
    value_render_option = "FORMULA"
    params = {"valueRenderOption": value_render_option}
    result = client.values_get(a1_notation, params)
    print("result_of_value_get:", result)
    dynamic_values = result["values"]
    print("before_date_dynamic_values:", dynamic_values)
    # recipe_info_headers = dynamic_values[0]
    # print('recipe_info_headers', recipe_info_headers)
    # recipe_info_user_input = dynamic_values[1]
    # print('recipe_info_user_input:', recipe_info_user_input)

    # get the static date value and convert it to string value.
    # values_get() convert the statuc string date into a random number (43877)
    date_string = temp_sheet_static_values[1][1]
    print("date_string:", date_string)
    # get date object
    date_obj = datetime.strptime(date_string, "%Y-%m-%d").date()
    print("date_obj:", date_obj)
    # format the date object with strftime;
    # replace the element in the list with the correct date format
    dynamic_values[1][1] = date_obj.strftime("%Y-%m-%d")  # fixed date format
    print("after_date_dynamic_values:", dynamic_values)
    for i, row in enumerate(dynamic_values):
        index = i + 1
        print("inserting row, index:", index, "row:", row)
        recipe_group_sheet.insert_row(
            row, index, value_input_option="USER_ENTERED"
        )
        """
        cell = recipe_group_sheet.cell(
            index,7,value_render_option='FORMATTED_VALUE'
        )
        # print('cell:', cell)
        """


def get_recipe_group_sheet(recipe_group):
    """
    Gets the sheet by name (group) and returns that worksheet in order
    to be used in all other functions
    """
    titles_list = get_existing_sheet_names()
    # if the workksheet already exists, return it
    if recipe_group in titles_list:
        recipe_group_sheet = client.worksheet(recipe_group)
        print("recipe_group_sheet:", recipe_group_sheet)
        return recipe_group_sheet
    else:
        raise ValueError("Invalid recipe group: %s" % recipe_group)
        # create_recipe_group_sheet

    # otherwise, create it then return it
    # return recipe_group_sheet


def delete_temp_recipe_sheet(client, temp_recipe_sheet):
    """Deletes temp_recipe_sheet"""
    client.del_worksheet(temp_recipe_sheet)


def add_recipe_to_sheet(request_form_dict):
    """
    Triggered by the "Submit" button
    Adds a recipe to the temp_recipe_sheet,
    Copies the new recipe from temp_recipe_sheet
    Inserts it in the correct sheet (newly created group sheet or existing one)
    Deletes the temp sheet once the recipe has been inserted in the correct one
    Returns the total recipe cost
    """
    recipe_info = get_recipe_info(request_form_dict)
    recipe_group = recipe_info["recipe_group"]
    recipe_ingredients = recipe_info["recipe_ingredients"]
    recipe_yield_qty = recipe_info["recipe_yield_qty"]
    recipe_yield_units = recipe_info["recipe_yield_units"]

    temp_recipe_sheet = create_temp_recipe_sheet(request_form_dict)
    insert_ingredients(temp_recipe_sheet, **recipe_info)
    unit_cost = get_unit_cost(temp_recipe_sheet, recipe_ingredients)
    total_product_cost = get_final_recipe_cost(
        temp_recipe_sheet, recipe_ingredients
    )
    recipe_group_sheet = get_recipe_group_sheet(recipe_group)
    copy_temp_sheet(
        temp_recipe_sheet,
        recipe_group_sheet,
        value_render_option="FORMATTED_VALUE"
    )
    insert_recipe_to_ingredients_list(
        temp_recipe_sheet,
        request_form_dict,
        recipe_yield_qty,
        recipe_yield_units,
        recipe_ingredients,
    )
    delete_temp_recipe_sheet(client, temp_recipe_sheet)
    return total_product_cost


def insert_ingredients(
    temp_recipe_sheet,
    recipe_name,
    date,
    recipe_yield_qty,
    recipe_yield_units,
    recipe_ingredients,
    ingredients_qty,
    ingredients_units,
    ingredients_notes,
    **kwargs,
):
    """
    Inserts the ingreds the user enter in the form into the selected sheet rows
    """
    recipe_info_list = [
        recipe_name, date, recipe_yield_qty, recipe_yield_units
    ]
    print("recipe_info_list:", recipe_info_list)
    temp_recipe_sheet.insert_row(
        recipe_info_list, 2, value_input_option="USER_ENTERED"
    )
    for i, ingredient in enumerate(recipe_ingredients):
        ingredient_list_of_columns = []
        ingredient_list_of_columns.append(ingredient)
        ingredient_list_of_columns.append(ingredients_qty[i])
        ingredient_list_of_columns.append(ingredients_units[i])
        ingredient_list_of_columns.append(ingredients_notes[i])
        ingredient_list_of_columns.append("")  # secondary untis column
        ingredient_list_of_columns.append(
            """=ARRAY_CONSTRAIN(ARRAYFORMULA(INDEX('INGREDIENT COST'!$A$1:$I$950,
            MATCH($A5,'INGREDIENT COST'!$A$1:$A$950,0),
            MATCH("COST / RECIPE UNIT ",'INGREDIENT COST'!$A$1:$I$1,0))), 1, 1)
            """
        )
        ingredient_list_of_columns.append("=B5*F5")
        temp_recipe_sheet.insert_row(
            ingredient_list_of_columns, 5, value_input_option="USER_ENTERED"
        )
        print("ingredient_list_of_columns:", ingredient_list_of_columns)


def get_recipe_cost(temp_recipe_sheet, recipe_ingredients):
    """
    Gets the recipe cost without the labour and packaging
    Returns the new row location of recipe cost to be used inother functions
    """
    # recipe_ingredients = recipe_info['recipe_ingredients']
    template_recipe_cost_column = "G"
    template_recipe_cost_row = 5
    print("template_recipe_cost_row:", template_recipe_cost_row)
    """
    template_total_recipe_cost_row_cell = master_template_sheet.cell(
        template_total_recipe_cost_row,7
    )
    print(
        'template_total_recipe_cost_row_cell:',
         template_total_recipe_cost_row_cell
    )
    """
    new_recipe_cost_row_difference = len(recipe_ingredients) + 1
    print("new_recipe_cost_row_difference:", new_recipe_cost_row_difference)
    new_recipe_cost_row_location = (
        template_recipe_cost_row + new_recipe_cost_row_difference
    )
    print("new_recipe_cost_row_location:", new_recipe_cost_row_location)

    # Calcualtes the recipe cost formula and passed it to the google sheet
    recipe_cost_end_row_num = (
        template_recipe_cost_row
        + len(recipe_ingredients) - 1
    )
    print("recipe_cost_end_row_num:", recipe_cost_end_row_num)
    recipe_cost_start_row = (
        f"{template_recipe_cost_column}{template_recipe_cost_row}"  # G5
    )
    print("recipe_cost_start_row", recipe_cost_start_row)
    recipe_cost_end_row = (
        f"{template_recipe_cost_column}{recipe_cost_end_row_num}"
    )
    print("recipe_cost_end_row:", recipe_cost_end_row)
    recipe_cost_formula = (
        f"=SUM({recipe_cost_start_row}:{recipe_cost_end_row})"
    )
    print("recipe_cost_formula:", recipe_cost_formula)
    temp_recipe_sheet.update_cell(
        new_recipe_cost_row_location, 7, recipe_cost_formula
    )
    recipe_cost = temp_recipe_sheet.cell(
        new_recipe_cost_row_location, 7, value_render_option="FORMATTED_VALUE"
    ).value
    print("recipe_cost:", recipe_cost)
    return new_recipe_cost_row_location


def get_unit_cost(temp_recipe_sheet, recipe_ingredients):
    """
    Gets the unit cost of the recipe based on the recipe cost (w/o lbr & pack)
    divide by the yield qty
    XXX The unit cost cell is being update here with the formula =Gx/C2,
    XXX needs to be used before the temp sheet gets copied into a new group
    XXX otherwise the formila will be broken
    Returns the unit value
    """
    new_recipe_cost_row_location = get_recipe_cost(
        temp_recipe_sheet, recipe_ingredients
    )
    template_unit_cost_row = 6
    template_recipe_cost_column = "G"
    new_unit_cost_row_difference = len(recipe_ingredients) + 1
    print("new__unit_cost_row_difference", new_unit_cost_row_difference)
    new_unit_cost_row_location = (
        template_unit_cost_row
        + new_unit_cost_row_difference
    )
    print("new_unit_cost_row_location", new_unit_cost_row_location)
    templte_yield_qty_column = "C"
    template_yield_qty_row = 2
    unit_cost_formula = (
        f"={template_recipe_cost_column}{new_recipe_cost_row_location}/"
        f"{templte_yield_qty_column}{template_yield_qty_row}"
    )
    print("unit_cost_formula:", unit_cost_formula)
    # XXX WE ARE UPDATING THE UNIT COST HERE
    temp_recipe_sheet.update_cell(
        new_unit_cost_row_location, 7, unit_cost_formula
    )
    new_unit_cost = temp_recipe_sheet.cell(
        new_unit_cost_row_location, 7, value_render_option="FORMATTED_VALUE"
    ).value
    print("new_unit_cost:", new_unit_cost)
    return new_unit_cost


def get_final_recipe_cost(temp_recipe_sheet, recipe_ingredients):
    """Get the final recipe cost including packaging and labour
    This is being returned to the user once they submit the order
    """
    new_recipe_cost_row_location = get_recipe_cost(
        temp_recipe_sheet, recipe_ingredients
    )
    template_total_cost_row = 10
    template_recipe_cost_column = "G"
    new_total_cost_row_difference = len(recipe_ingredients) + 1
    print("new_total_cost_row_difference :", new_total_cost_row_difference)
    new_total_cost_row_location = (
        template_total_cost_row + new_total_cost_row_difference
    )
    print("new_total_cost_row_location:", new_total_cost_row_location)
    template_packaging_cost_row = 7
    template_labour_cost_row = 8
    new_packaging_cost_row_difference = len(recipe_ingredients) + 1
    print(
        "new_packaging_cost_row_difference:", new_packaging_cost_row_difference
    )
    new_packaging_cost_row_location = (
        template_packaging_cost_row + new_packaging_cost_row_difference
    )
    print("new_packaging_cost_row_location:", new_packaging_cost_row_location)
    new_labour_cost_row_difference = len(recipe_ingredients) + 1
    print("new_labour_cost_row_difference:", new_labour_cost_row_difference)
    new_labour_cost_row_location = (
        template_labour_cost_row + new_labour_cost_row_difference
    )
    print("new_labour_cost_row_location:", new_labour_cost_row_location)
    total_cost_formula = (
        f"={template_recipe_cost_column}{new_recipe_cost_row_location}+"
        f"{template_recipe_cost_column}{new_packaging_cost_row_location}+"
        f"{template_recipe_cost_column}{new_labour_cost_row_location}"
    )
    print("total_cost_formula:", total_cost_formula)
    temp_recipe_sheet.update_cell(
        new_total_cost_row_location, 7, total_cost_formula
    )
    total_product_cost = temp_recipe_sheet.cell(
        new_total_cost_row_location, 7, value_render_option="FORMATTED_VALUE"
    ).value
    print("total_product_cost:", total_product_cost)
    return total_product_cost


def get_existing_sheet_names():
    """
    Gets all the exisiting worksheets names
    Remove  the sheets which shouldn't load on the dropdown menu of the portal
    """

    # this has the same functinality, using list comprehension
    """
    titles_list = [
    worksheet.title.lower()
    for worksheet in client.worksheets()
    if worksheet.title.lower() not in remove_list
    ]
    """
    remove_list = [
        "INGREDIENT COST","recipe-template", "empty-template", "TEMPLATES >>>"
    ]
    titles_list = []
    substring = "19"
    for worksheet in client.worksheets():
        # worksheet_title_lower = worksheet.title.lower()
        worksheet_title = worksheet.title
        if substring in worksheet_title:
            remove_list.append(worksheet_title)
        if worksheet_title not in remove_list:
            titles_list.append(worksheet_title)
    print("titles_list:", titles_list)
    return titles_list


def get_ingredients_by_category():
    """
    Gets all the ingredients from the ssheet, from the master 'INGREDIENT COST'
    sheet and organizes them by categories
    Puts them in dict keys: values - categories :[ingredient,ingredient,..]
    """
    # dict with categories as keys and list of ingreds as values for each key
    ingredients_dict = {}
    ingredients_sheet = client.worksheet("INGREDIENT COST")
    records = ingredients_sheet.get_all_records()
    for ingredient_dict in records:
        # access the values of each key and save it in variable
        ingredient = ingredient_dict["INGREDIENT"]
        price = ingredient_dict["PRICE"]
        # print('ingredient:', ingredient, 'price:', price )
        if ingredient_dict["PRICE"] == "":
            category = ingredient_dict["INGREDIENT"]
            # if category doesn't exist in the dict we have to initialize it
            if category not in ingredients_dict:
                ingredients_dict[category] = []
                # print('ingredients_dict', ingredients_dict)
        list_of_ingredients = ingredients_dict[category]
        """
        getting the list from ingredients_dict[category] = []
        & assigning it to a new var list_of_ingredients
        print('before adding to list of ingredinents:', list_of_ingredients)
        print()
        """
        if ingredient_dict["PRICE"] != "":
            list_of_ingredients.append(ingredient)
    print("after adding to list of ingredinents:", list_of_ingredients)
    return ingredients_dict


def get_ingredients_list():
    """
    Gets the ingredients from the ingredients dict and puts them in a list
    This is done so we can acess the ingredients in Javascript & compare if the
    user input for ingredient exists in the list.
    *JS needs list to use the "inlcudes()" method
    """
    ingredients_dict = get_ingredients_by_category()
    ingredients_list = []
    for _, ingredients in ingredients_dict.items():
        ingredients_list.extend(ingredients)
    print("ingredient_list:", ingredients_list)
    return ingredients_list


def insert_new_ingredient(new_ingredient_input):
    """
  Triggered by "Create New Ingredient" Button
  Inserts the user's new ingredient input into the at the bottom
  of the master INGREDIENT COST sheet at $0.00
  """
    new_ingredient_list_of_columns = []
    new_ingredient_list_of_columns.append(new_ingredient_input)
    print("new_ingredien_list_of_columns:", new_ingredient_list_of_columns)
    new_ingredient_list_of_columns.append("-")
    new_ingredient_list_of_columns.append("")
    new_ingredient_list_of_columns.append("")
    new_ingredient_list_of_columns.append("")
    new_ingredient_list_of_columns.append("")
    new_ingredient_list_of_columns.append("0.00")
    master_ingredient_sheet = client.worksheet("INGREDIENT COST")
    master_ingredient_sheet.append_row(
        new_ingredient_list_of_columns, value_input_option="RAW"
    )
    print("new_ingredien_list_of_columns:", new_ingredient_list_of_columns)


def insert_recipe_to_ingredients_list(
    temp_recipe_sheet,
    request_form_dict,
    recipe_yield_qty,
    recipe_yield_units,
    recipe_ingredients,
):
    """
    Adds a recipe as an ingredient to the master INGREDIENT COST sheet
    """
    temp_recipe_sheet_title = temp_recipe_sheet.title
    total_product_cost = get_final_recipe_cost(
        temp_recipe_sheet, recipe_ingredients
    )
    unit_cost = get_unit_cost(temp_recipe_sheet, recipe_ingredients)

    new_recipe_list_of_columns = []
    new_recipe_list_of_columns.append(temp_recipe_sheet_title)
    print("new_recipe_list_of_columns:", new_recipe_list_of_columns)
    new_recipe_list_of_columns.append(total_product_cost)
    new_recipe_list_of_columns.append(recipe_yield_qty)
    new_recipe_list_of_columns.append(recipe_yield_units)
    new_recipe_list_of_columns.append(recipe_yield_units)
    new_recipe_list_of_columns.append(recipe_yield_qty)
    new_recipe_list_of_columns.append(unit_cost)
    master_ingredient_sheet = client.worksheet("INGREDIENT COST")
    master_ingredient_sheet.append_row(
        new_recipe_list_of_columns, value_input_option="RAW"
    )
    print("new_recipe_list_of_columns:", new_recipe_list_of_columns)


if __name__ == "__main__":
    # print('this is in spreadsheet.py __main__')
    get_ingredients_by_category()
