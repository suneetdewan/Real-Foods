'''
Suneet Dewan and Sam Spaeth
Stats Consulting
Real Food Project
This is the program that reads the text file and accordingly outputs requested analysis
'''


import numpy as numpy
#import matplotlib.pyploy as plt
import pandas as pd
from pandas import DataFrame, Series
import re
import string
pd.set_option('display.max_rows', 500)


def clean(data, priority_key_terms, key_terms):
    for index, row in data.iterrows():
        data.loc[index, "Description"] = row.Description.lower()

    for index, row in data.iterrows():
        word_list = row.Description.split()
        # for word in word_list:
        #     if word in remove:
        #         word_list.remove(word)
        for word_index in range(len(word_list)):
            changed = False
            for i in priority_key_terms:
                    if word_list[word_index] in i[1]:
                       word_list = [i[0]]
                       changed = True
                       break
            if not changed:
                for i in key_terms:
                    if word_list[word_index] in i[1]:
                       word_list = [i[0]]
                       changed = True
                       break
            if changed:
                break
        new_string = ""
        if (len(word_list)) != 0:
            for j in word_list[:-1]:
                new_string = new_string + j + " "
            new_string = new_string + word_list[-1]

        data.loc[index, "Description"] = new_string




def real_food_dummy(df):
    # Creates a new dummy variables with 1 if real and 0 if not real.
    
    for index, row in df.iterrows():
        if (row.Local == 'yes' or row.Fair == 'yes' or row.Ecological == 'yes' or row.Humane == 'yes') and row.Disqualifier == 'no':
            df.loc[index, "real_food"] = 'real';
        else:
            df.loc[index, "real_food"] = 'non-real';
    return df 

def key_words_use(df, keyword):

    for index, row in df.iterrows():
        if row.Description in keyword:
            df.loc[index, "Keyword"] = "Yes";
        else:
            df.loc[index, "Keyword"] = "No"

    g = df.groupby(['Keyword']).agg({'Cost': sum}).sort_values('Cost', ascending = False)
    g['Percentage'] = g.apply(lambda x: 100*x/float(x.sum()))

    return g

def key_food_category(df, cat, item):

    for index, row in df.iterrows():
        if row.Description == item:
            df.loc[index, "Item"] = "Yes"
        else:
            df.loc[index, "Item"] = "No"
    df = df[df.Category == cat]

    g = df.groupby(['Item']).agg({'Cost': sum}).sort_values('Cost', ascending = False)
    g['Percentage'] = g.apply(lambda x: 100*x/float(x.sum()))

    return g


def top_foods_category(df, number):
    # Number is the amount of top foods you want to see. 20 for top 20, 50 for top 50 etc
    # Returns a pandas.Series

    data_agg = df.groupby(['Category', 'Description']).agg({'Cost': sum})
    g = data_agg['Cost'].groupby(level = 0, group_keys = False)
    res = g.apply(lambda x: x.sort_values(ascending=False).head(number))


    res = pd.Series.to_frame(res)


    return res

def total_spend_category(df):
    # Returns a data frame
    # with the total money spend in each category
    g = df.groupby(['Category']).agg({'Cost': sum}).sort('Cost', ascending = False)
    g = df.groupby(level = 0).apply(lambda x: 100*x/float(x.sum()))
    return g

def spend_category_real(df):
    # Returns real v non-real spend in each category
    # Also what % of the category's spend is real v non-real
    real_spend_category = df.groupby(['Category', 'real_food']).agg({'Cost': 'sum'})
    real_spend_category['Percentage'] = real_spend_category.groupby(level=0).apply(lambda x: 100*x/float(x.sum()))

    return real_spend_category

def total_spend_food(df):
    # returns a dataframe with the food items where most money was spent
    g = df.groupby(['Description']).agg({'Cost': sum}).sort('Cost', ascending = False)
    return g

def top_n_food_spend(df, n):
    g = df.groupby(['Description']).agg({'Cost': sum}).sort('Cost', ascending = False).head(n)
    return g

def real_nonreal_spend(df):
    # Returns a dataframe with total spending in real v non-real spending
    real_spend = df.groupby(['real_food']).agg({'Cost':sum, })
    real_spend['Percentage'] = real_spend.apply(lambda x: 100*x/float(x.sum()))
    return real_spend

def real_food_percentage(df):
    # Returns the percentage of total spending spent on real foods

    data = real_food_dummy(df)
    real_spend = data.groupby(['real_food']).agg({'Cost':sum, })
    perct = 100 * real_spend.loc['real'] / real_spend.Cost.sum()
    return perct

def shift_to_real(df, percentage):
    # Returns the amount of spending that is needed to be shifted if they want a certain percentage
    # of real food
    real_spend = df.groupby(['real_food']).agg({'Cost':sum, })
    target = (percentage/100.0) * real_spend.Cost.sum()
    Difference = target - real_spend.loc['real']

    return Difference

def change_category(df, category_set):
    for index, row in df.iterrows():
        for i in category_set:
            if row.Description in i[1]:
                df.loc[index, "Category"] = i[0]

    return df

def create_new_category(df, category_set):
    for index, row in df.iterrows():
        for i in category_set:
            if row.Description in i[1]:
                row.loc[index, "New_Category"] = [i[0]]
            else:
                row.loc[index, "New_Category"] = row.Category

    return df

def main():
    # Gross and complicated, but flexible, input reader.
    data_file = open("input.txt", "r")
    multi_line = False
    name = ''
    assignment = ''
    for line in data_file:
        if line[0] == "#" or line[0] == "\n":
            continue
        if line[0] == "\t":
            line = line[1:]
        line = "".join(line.split())
        row = line.split("\n")[0].split(':')
        if row[len(row)-1] == 'False' or row[len(row)-1] == 'True':
            tVal = row[1] == 'True'
            exec("%s = %r" % (row[0],tVal))
        else:
            if multi_line:
                if row[0][-1] == ']' or row[0][-1] == '}':
                    assignment = assignment + row[len(row)-1]
            if row[len(row)-1][-1] == ',':
                multi_line = True
            else:
                multi_line = False
            if not multi_line:
                if len(row) == 2:
                    exec("%s = %s" % (row[0],row[1]))
                elif len(row) == 1:
                    exec("%s = %s" % (name,assignment))
                name = ''
                assignment = ''
            elif multi_line:
                if len(row) == 2:
                    name = row[0]
                    assignment = assignment + row[1]
                else:
                    assignment = assignment + row[0]
    # Now that all of the input file has been read, on to the actual work

    #read the csv 
    #create df, the following line is temporary
    df = pd.read_csv(csv_file_name)
    df = real_food_dummy(df)


    #TODO
    #cleandata()
    clean(df, priority_key_terms, key_terms)

    ## if using percent
    #TODO
    'if (use_perc):'
    'if (print_perc_doll_conversion):'

    ## If creating new categories
    #TODO
    if (create_new_category):
        df = change_category(df, new_categories)

    if (output_clean):
        df.to_csv(("clean_" + csv_file_name), unicode = 'utf-8')
    # use the variable new_categories
    # new_categories[0][0] is the name of the first new category, new_categories[0][1] 
    #    is the set of item names to be added to the new category.
    ## if the new categories can overlap or not...

    #TODO
    if (top_n_per_category):
        if (output_terminal):
            print "\n\nTop", top_n, "per category."
            print top_foods_category(df, top_n)
        if (output_csv):
            top_foods_category(df, top_n).to_csv(base_name + "top_" + str(top_n) + "_per_category.csv", unicode = 'utf-8')

    #TODO
    if (use_key_words):
        if (output_terminal):
            print "\n\nPercent food budget is",
            for i in range(len(key_words)-1):
                print "%s, " % (key_words[i]), 
            print "or" + key_words[-1] + "."
            print key_words_use(df, key_words)
        if (output_csv):
            key_words_use(df, key_words).to_csv(base_name + "use_key_words.csv", unicode = 'utf-8')

    #TODO
    if (analyze_one_category):
        if (output_terminal):
            print "\n\nPercent %s in %s." % (item_to_analyze, category_to_analyze)
            print key_food_category(df, category_to_analyze, item_to_analyze)
        if (output_csv):
            key_food_category(df, category_to_analyze, item_to_analyze).to_csv(base_name + "analyze_one_category.csv", unicode = 'utf-8')
        #if (analyze_one_item):
            #item_to_analyze

    if (perc_real_per_category):
        if (output_terminal):
            print "\n\nPercent real per category."
            print spend_category_real(df)
        if (output_csv):
            spend_category_real(df).to_csv(base_name + "perc_real_per_category.csv", unicode = 'utf-8')

    if (real_v_nonreal):
        if (output_terminal):
            print "\n\nReal compared to non-real."
            print real_nonreal_spend(df)
        if (output_csv):
            real_nonreal_spend(df).to_csv(base_name + "real_v_nonreal.csv", unicode = 'utf-8')

    if (use_perc):
        print_string = "\n\nTo achieve  %i percent real food, shift $%i from non-real to real." % (perc_shift, shift_to_real(df, perc_shift))
        print print_string




# Table for each category, real v non-real percentage
if __name__ == "__main__":
    main()






