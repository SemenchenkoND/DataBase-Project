import os
from operator import index
from re import match
from xml.dom.minidom import ProcessingInstruction

import openpyxl
import pandas as pd
#from tabulate import tabulate
from pprint import pprint
import re

def check_date_format(date_str):
    """
    Проверяет, соответствует ли строка формату.
    """
    pattern = r"^\d{2}\.\d{2}\.\d{2}$"
    pattern1 = r"^\d{2}\.\d{2}\.\d{2},\d{2}\.\d{2}\.\d{2}$"
    match = re.match(pattern, date_str)
    match1 = re.match(pattern1, date_str)
    return bool(match) or bool(match1)

def len_spaces(text):
  """
  Подсчитывает количество пробелов перед числом в строке.

  """
  for i, char in enumerate(text):
    if char.isdigit():
      return i
  return 0

def preserve_leading_spaces(x):
    """Функция сохраняет ведущие пробелы в строке."""
    return str(x)

def check_empty_values(df,col_names):
    rows=len(df.axes[0])
    cols = len(df.axes[1])
    empty_positions = {}

    for row in range(2,rows+2):
        #print(len(df['g1'][row]))
        empty_positions[row] = []
        for col in col_names:
            if df[col][row]=='':
                #print(col, row_index)
                empty_positions[row].append({col:"Пустое значение"})
                #naming = {empty_positions[row].append(col): 'Пустое значение'}
    return empty_positions

def check_spaces_before(number):
    """
    Проверяет, есть ли пробел перед числом.
    """
    #length=len(number)
    number_str = str(number)
    #if length==1 and len_spaces(number_str)==2: return True
    #elif length==2 and len_spaces(number_str)==1: return True
    #else: return False
    return number_str.endswith(" ")


def check_spaces(df,col_names,list_mistake):
    rows = len(df.axes[0])
    cols = len(df.axes[1])
    for row in range(2,rows+2):
        for col in col_names[:1]:
            if len(df['g1'][row])!=3:
                list_mistake[row].append({col: "Наличие пробела"})
    return list_mistake

def g7(df,list_mistake):
    rows = len(df.axes[0])
    col='g7'
    for row in range(2,rows+2):
        if check_date_format(df[col][row])!=True:
            list_mistake[row].append({col: "Неверный формат кода"})
    return list_mistake

def g6(df,list_mistake):
    rows = len(df.axes[0])
    col='g6'
    for row in range(2,rows+2):
        if df[col][row].isupper()==True:
            list_mistake[row].append({col: "Все буквы заглавные"})
    return list_mistake

def positive_values(df,list_mistake,cols):
    cols.append('g5')
    rows = len(df.axes[0])
    for row in range(2, rows + 2):
        for col in cols:
            if df[col][row] < 0:
                list_mistake[row].append({col: "Отрицательное значение"})
    return list_mistake


def main():
    #os.chdir("D:/Учеба МЭИ/7 семестр/СУБД/СУБД лаб FOR STUD/файлы на 2024/по вариантам XLS/v7 гранты")
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)
    pd.set_option('display.expand_frame_repr', True)

    book=openpyxl.open("test_integrity_Gr_prog.xlsx",read_only=True)

    sheet=book.active

    #print(sheet[1][2].value)
    big_sp=[]
    for row in sheet.iter_rows(values_only=True):
        st=list(row)
        st1=st[0]
        #if st1!='g1': st1="'"+st1+"'"
        st[0]=st[1]
        st[1]=st1
        big_sp.append(st)
        #print(*st)

    '''
    print(type(big_sp[22][1]))
    print(type(big_sp[23][1]))
    if big_sp[22][1]==big_sp[23][1]: print(True)'''
    #print(big_sp[0])
    df=pd.DataFrame(big_sp[1:],columns=big_sp[0])
    df.index=range(2,len(df.axes[0])+2)

    df.style.set_properties(**{'text-align': 'left'})


    #print(df.iloc[21,1])
    #print(df.iloc[22,1])
    #if df.iloc[21,1]!=df.iloc[22,1]: print(True)


    #ff.set_table_styles(overwrite=False)

    #print(tabulate(df,headers=big_sp[0],colalign="center"))

    #dfStyler = ff.style.set_properties(**{'text-align': 'left'})

    #ff.rename(columns=big_sp[0])
    '''
    for i in range(len(df['z2'])):
        print(i)
    print(len(df['z2']))

    '''
    #print(df.isnull())
    #empty_positions = check_empty_values_with_positions(df,big_sp[0])
    empty_positions = check_empty_values(df,big_sp[0])
    #for i in empty_positions:
    print("Ошибки/неточности по БД")
    empty_positions=check_spaces(df,big_sp[0],empty_positions)
    empty_positions=g7(df,empty_positions)
    empty_positions=g6(df,empty_positions)
    empty_positions=positive_values(df,empty_positions,list(df.columns[-5:]))
    #print(df['g1'][22][1])
    #print(df['g1'][23][2])
    #print(int(df['g1'][23]))
    #if int(df['g1'][23])<10 and df['g1'][23][1]==' ': print(True)
    #else:print(False)
    #print(empty_positions.keys(), empty_positions.values())
    #pprint(empty_positions)
    #print(len(empty_positions))
    #for i in empty_positions:
    for i in range(len(empty_positions)):
        print(f'Строка {list(empty_positions.keys())[i]}: {list(empty_positions.values())[i]}')

if __name__ == '__main__':
    main()