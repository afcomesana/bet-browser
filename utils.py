from Levenshtein import ratio

def min_levenshtein_distance(string:str,*args:str):
        '''Find max Levenshtein similarity between a string and a bunch of strings.
        Two identical strings has 1 similarity while two different strings has 0 similarity.'''
        maximum,value = 0, None
        for string1 in args:
            sim = ratio(string,string1)
            if sim > maximum:
                 maximum,value = sim, string1
        return value if maximum > 0.6 else None

def flatten_list( nested_list, flatenned_list = [] ):
    #Only allow using this function with 'list' objects
    if type(nested_list) != list:
        raise 'List required, %s used as argument.' % type(nested_list)
    
    # Wether all the items from nested_list were removed or it was an empty list:
    # We end the function:
    if len( nested_list ) == 0:
        return flatenned_list
    
    item = nested_list.pop(0)
    
    # If the item is also a list, we must flatten it as well:
    if type(item) == list:
        flatenned_list = flatten_list( item, flatenned_list )
        
    # Otherwise, add it as a normal item
    else:
        flatenned_list += [item]
        
    # Continue flattening the list:
    return flatten_list( nested_list, flatenned_list )

