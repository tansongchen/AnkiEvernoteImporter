# coding:utf-8
import re
import json
import codecs
import functools
import os.path
from random import random
from random import randint
from pprint import pprint
from copy import deepcopy
def strF2H(ustring):
    '''
    convert full width character to half width
    input: a unicode object
    return: a unicode object
    '''
    h_ustring = ""
    assert isinstance(ustring, str)
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:
            #  white space
            inside_code = 32
        elif 65281 <= inside_code <= 65374:
            #  other characters
            inside_code -= 65248

        h_ustring += chr(inside_code)
    return h_ustring
def extract_content_between(obj_str, match_re, return_str_before_first_match=False):
    '''
    extract content between the start of two equal pattern found in a str,
    also extract the content after the last match
    input: obj_str, the string to extract content from, must be a unicode object
           match_re, the pattern to be matched
    return: a list of str
    return_str_before_first_match: whether to return the str before the first match of the given patter
    '''
    assert isinstance(obj_str, str)
    retype = type(re.compile(r'a str'))
    assert isinstance(match_re, retype)
    
    match_results_iter = match_re.finditer(obj_str)
    returned_str_l = []
    start_index = None
    end_index = None
    first_start_index = None
    for match_result in match_results_iter:
        if first_start_index is None:
            first_start_index = match_result.start()
        if not (start_index is None):
            end_index = match_result.start()
            returned_str_l.append(obj_str[start_index:end_index])
        start_index = match_result.start()
    returned_str_l.append(obj_str[start_index:])
    if return_str_before_first_match:
        returned_str_l = [obj_str[:first_start_index]] + returned_str_l
    if len(returned_str_l) == 2 and returned_str_l[0] == returned_str_l[1]:
        returned_str_l = returned_str_l[:1]
    return returned_str_l
def iter_through_general(obj_iter, path, yield_flags=True, final_yield_object=None):
    '''
    iter through an object following the given path
    yield_flags: control whether to yield the flags indicating the path at the global level
    final_yield_object: internal parameter, don't modify
    obj_iter: an iterable variable
    path: a sequence, each element has the following structure
        (how_to_iter, what_to_iter, yield_flag)
        how_to_iter: a str, accept the following values
            'all' or 'all_values': iter through key-value pair for dict, and all elements for other type
                if yield_flag is True, attach key or index to the final yield object
            'all_keys', only iter through the keys of a dict
                obj_iter must be a dict
            'key', iter through the value of a given key
                what_to_iter must be a str representing a key in obj_iter
                if yield_flag is True, attach key to the final yield object
                ignored when obj_iter is not dict
            'keys', iter through the values of a given set of keys
                what_to_iter must be a tuple with elements reprenting keys in obj_iter
                if yield_flag is True, attach key to the final yield object
                ignored when obj_iter is not dict
            'index', iter through a given element
                what_to_iter must be an int within bound
                if yield_flag is True, attach index to the final yield object
                ignored when obj_iter is dict
            'indexes', iter through the elements with given indexes
                what_to_iter must be an list of int within bound
                if yield_flag is True, attach key to the final yield object
                ignored when obj_iter is dict
        what_to_iter: content decided by how_to_iter
            ignored for the following values of how_to_iter
                all, all_values, all_keys
        yield_flag: True or False
            True: depending on how_to_iter, attch different flags to the final result
            False: no flag wil be yield
            ignored for the following values of how_to_iter
                all_keys
    '''
    is_dict = isinstance(obj_iter, dict)
    if final_yield_object is None:
        final_yield_object = []
    if len(path) == 0:
        if yield_flags:
            final_yield_object.append(obj_iter)
            yield final_yield_object
        else:
            yield obj_iter
    else:
        how_to_iter, what_to_iter, yield_flag = path.pop(0)
        assert isinstance(how_to_iter, str)
        if how_to_iter in ['all', 'all_values', 'keys', 'indexes']:
            if how_to_iter in ['keys', 'indexes']:
                assert hasattr(what_to_iter, '__iter__')
                for item in what_to_iter:
                    if is_dict:
                        assert how_to_iter == 'keys'
                        assert isinstance(item, str)
                        assert item in obj_iter
                    else:
                        assert how_to_iter == 'indexes'
                        assert isinstance(item, int)
                        assert item < len(obj_iter)
                temp_iterator = ((item, obj_iter[item]) for item in what_to_iter)
            else:
                temp_iterator = iter(obj_iter.items()) if is_dict else enumerate(obj_iter)
            for flag, sub_obj_iter in temp_iterator:
                final_yield_object_copy = deepcopy(final_yield_object)
                if yield_flag:
                    final_yield_object_copy.append(flag)
                for value in iter_through_general(sub_obj_iter, deepcopy(path), yield_flags, final_yield_object_copy):
                    yield value
        elif how_to_iter == 'all_keys':
            assert is_dict
            for key in obj_iter.keys():
                if yield_flags:
                    final_yield_object.append(key)
                    yield final_yield_object
                else:
                    yield key
        elif how_to_iter in ['key', 'index']:
            if is_dict:
                assert how_to_iter == 'key'
                assert isinstance(what_to_iter, str)
                assert what_to_iter in obj_iter
            else:
                assert how_to_iter == 'index'
                assert isinstance(what_to_iter, int)
                assert what_to_iter < len(obj_iter)     
            sub_obj_iter = obj_iter[what_to_iter]
            if yield_flag:
                final_yield_object.append(what_to_iter)
            for value in iter_through_general(sub_obj_iter, deepcopy(path), yield_flags, final_yield_object):
                yield value
        else:
            raise ValueError('Invalid path')
strip_white_space = lambda _str: _str.replace(' ', '')
new_line_join = lambda str_l: '\n'.join(str_l)
def codecs_open_r_utf8(file_path):
    with codecs.open(file_path, 'r', 'utf-8') as f:
        returned_str = f.read()
    return returned_str
# merge blank lines
def collapse_blank_line(base_str):
    match_double_line_feed_re = re.compile(r'\n\n|\n \n')
    while match_double_line_feed_re.search(base_str):
        base_str = match_double_line_feed_re.sub(r'\n', base_str)
    return base_str
def custom_html_element(_str):
    """
    convert the markdown notations in a string to html tags
    currently, only two kinds of markdown notation exist in all the strings
    ** and *
    """
    formatted_str = _str
    # format triple asterisk
    match_double_asterisk_re = re.compile('__(.*?)__')
    # replace ***...*** with <strong>...</strong>
    formatted_str = match_double_asterisk_re.sub(r'<strong>\1</strong>', formatted_str)
    # format double asterisk
    match_double_asterisk_re = re.compile('\*\*(.*?)\*\*')
    # replace **...** with <ins>...</ins>
    formatted_str = match_double_asterisk_re.sub(r'<strong><ins>\1</ins></strong>', formatted_str)
    # format single asterisk
    # replace *...* with <?>...</?>
    match_single_asterisk_re = re.compile('\*(.*?)\*')
    formatted_str = match_single_asterisk_re.sub(r'\1', formatted_str)
    return formatted_str
def is_file_and_json_load(file_name_str):
    if os.path.isfile(file_name_str):
        with codecs.open(file_name_str, 'r', encoding='utf-8') as f:
            json_d = json.load(f)
        return json_d
