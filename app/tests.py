
from spreadsheet_final import get_client



def copy_sheet(source_sheet_name, target_sheet_name):
  '''Copy the contents from souce sheet to target sheet, including formulas
  '''
  client = get_client()
  source_sheet = client.worksheet(source_sheet_name)
  target_sheet = client.worksheet(target_sheet_name)

  # use get_all_values() to determine the range
  static_values = source_sheet.get_all_values()
  print('static_values:', static_values)
  num_rows = len(static_values)
  num_cols = len(static_values[0])

  start_row_number = 1
  start_col_number = 1
  end_row_number = num_rows
  end_col_number = num_cols

  a1_notation = get_a1_notation(
    start_row_number, start_col_number, end_row_number, end_col_number,
    source_sheet_name 
  )
  value_render_option = 'FORMULA'
  params = {'valueRenderOption': value_render_option}
  result = client.values_get(a1_notation, params)
  dynamic_values = result['values']
  print('dynamic_values:', dynamic_values)

  for i, row in enumerate(dynamic_values):
    index = i + 1
    print('inserting row, index:', index, 'row:', row)
    target_sheet.insert_row(row, index, value_input_option='USER_ENTERED')



def int_to_letter(number):
  # from https://stackoverflow.com/questions/18544419
  # chr(65) == 'A'
  assert 1 <= number <= 26, 'number must represent a letter of the alphabet'
  return chr(64 + number)

def get_a1_notation(
  start_row_number, start_col_number,
  end_row_number, end_col_number,
  sheet_name=None
):
  '''
  Get the A1 notation for use in gspread.Spreadsheet.values_get()

  A1 notation is 1-indexed.
  '''

  start_col_letter = int_to_letter(start_col_number)
  end_col_letter = int_to_letter(end_col_number)

  prefix = f'{sheet_name}!' if sheet_name else ''
  rval = (
    f'{prefix}'
    f'{start_col_letter}{start_row_number}:'
    f'{end_col_letter}{end_row_number}'
  )
  print('get_a1_notation() rval:', rval)
  return rval

### TESTS

def test_copy_sheet(client):
  print('test_copy_sheet()')

  # the source sheet is expected to exist
  # TODO: create the source sheet programmatically and delete it afterwards
  source_sheet_name = 'test_source'
  target_sheet_name = 'test_target'

  source_sheet = client.worksheet(source_sheet_name)
  
  # create the target worksheet if it does not already exist
  try:
    target_sheet = client.worksheet(target_sheet_name)
    client.del_worksheet(target_sheet)
  except:
    pass
  target_sheet = client.add_worksheet(target_sheet_name, 1, 1)

  copy_sheet(source_sheet_name, target_sheet_name)

  source_values = source_sheet.get_all_values()
  target_values = target_sheet.get_all_values()
  print('source_values:', source_values)
  print('target_values:', target_values)

  assert source_values == target_values, (source_values, target_values)

def test_int_to_letter(client):
  print('test_int_to_letter()')
  number = 1
  expected_letter = 'A'
  actual_letter = int_to_letter(number)
  assert expected_letter == actual_letter, (expected_letter, actual_letter)

def test_get_a1_notation(client):
  print('test_get_a1_notation()')
  start_row_number = 1
  start_col_number = 1
  end_row_number = 4
  end_col_number = 2
  sheet_name = 'source_sheet'
  expected = 'source_sheet!A1:B4'
  actual = get_a1_notation(
    start_row_number, start_col_number, end_row_number, end_col_number,
    sheet_name
  )
  assert expected == actual, (expected, actual)

def run_tests():
  print('Running tests...')
  client = get_client()
  test_int_to_letter(client)
  test_get_a1_notation(client)
  test_copy_sheet(client)
  print('Tests passed!')


if __name__=='__main__':
  #print('this is in spreadsheet.py __main__')
  #get_ingredients_by_category()

  run_tests()
