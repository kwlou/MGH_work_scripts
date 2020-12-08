
#random helper functions to be put into properly labeled python functions later

def string_intersection(str1,str2):
    # compares two strings to return a list of their index of intersection
    index_of_intersection=[]
    for i,strings in enumerate(zip(str1,str2)):
        if strings[0] == strings[1]:
            index_of_intersection.append(i)
    return index_of_intersection