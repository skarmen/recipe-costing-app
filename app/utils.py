def int_to_letter(number):
  # from https://stackoverflow.com/questions/18544419
  # chr(65) == 'A'
  assert 1 <= number <= 26, 'number must represent a letter of the alphabet'
  return chr(64 + number)


def get_a1_notation(start_row_number, start_col_number,end_row_number, end_col_number,sheet_name=None):
  '''
  Get the A1 notation for use in gspread.Spreadsheet.values_get()
  A1 notation is 1-indexed.
  '''

  start_col_letter = int_to_letter(start_col_number)
  end_col_letter = int_to_letter(end_col_number)

  prefix = f'{sheet_name}!' if sheet_name else '' #ternary operator
  rval = (
    f'{prefix}'
    f'{start_col_letter}{start_row_number}:'
    f'{end_col_letter}{end_row_number}'
  )
  print('get_a1_notation() rval:', rval)
  return rval