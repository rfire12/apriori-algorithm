from itertools import combinations
from copy import copy
import sys
import operator



def get_initial_combination(transactions):
    occurrences = {}
    for transaction in transactions:
        for item in transaction:
            occurrences[item] = 0 if occurrences.get(
                item, None
            ) == None else occurrences.get(
                item
            )  # It initilizes the current key in the key if it doesn't exists
            occurrences[item] += 1
    return occurrences


def delete_items_dont_meet_min_support(items, min_support):
    return dict(filter(lambda item: item[1] >= min_support, items.items()))


def create_combinations(items, combination_length):
    items_combination = list(
        combinations(items, combination_length)
    )  # Creates combinations of 2. It creates a list of tuples
    return list(
        map(lambda item: list(item),
            items_combination))  # Casts a list of tuples to a list of lists


def combinations_to_string(items):
    items_key = list(map(lambda item: ",".join(item), items))
    return items_key


def count_occurrences_of_combinations(combinations, transactions):
    occurrences = {}
    for combination in combinations:
        occurrences[combination] = 0
        for transaction in transactions:
            count = 0
            split_items = combination.split(",")
            for item in split_items:
                if item in transaction:
                    count += 1
            if count == len(
                    split_items):  # If the items are in the same transaction
                occurrences[combination] += 1
    return occurrences


def get_items(combinations):
    new_items_dict = {}
    for combination in combinations:
        items = combination.split(",")
        for item in items:
            new_items_dict[item] = None
    return list(new_items_dict.keys())


def generate_rules_items(transactions, min_support, items_combinations, combinations_size, previous_combination):
    filtered_occurrences = delete_items_dont_meet_min_support(
        items_combinations, min_support)
    filtered_occurrences_items = list(filtered_occurrences.keys())

    if len(filtered_occurrences_items) == 0:
        return previous_combination

    if combinations_size > 2:  # If the rules have more than 1 element
        previous_combination += filtered_occurrences_items

    items = get_items(filtered_occurrences_items)
    items_combinations = create_combinations(items, combinations_size)
    items_combinations_string = combinations_to_string(items_combinations)
    items_combinations_occurrances = count_occurrences_of_combinations(
        items_combinations_string, transactions)
    combinations_size += 1
    return generate_rules_items(transactions, min_support, items_combinations_occurrances, combinations_size, previous_combination)


def list_of_strings_to_list_of_lists(list_to_parse):
    return list(map(lambda string: string.split(","), list_to_parse))


def create_rule_set(items):
    rule_set = {}
    for combination_size in range(1, len(items)):
        keys_list = list(combinations(items, combination_size))
        keys = combinations_to_string(keys_list)

        for key in keys:
            keys_list = key.split(",")
            rule_set[key] = []
            for item in items:
                if item not in keys_list:
                    rule_set[key].append(item)

    return rule_set


def generate_rules(rules_items):
    rules_sets = []
    for items in rules_items:
        rules_sets.append(create_rule_set(items))
    return rules_sets


def get_rule_occurrence(rule_items, transactions):
    occurrance = 0
    for transaction in transactions:
        rule_in_transaction = True
        for item in rule_items:
            if item not in transaction:
                rule_in_transaction = False
        if rule_in_transaction:
            occurrance += 1
    return occurrance


def get_rules_confidence(rules_sets, rules_items, transactions):
    rules_confidence = []
    for rule_set, rule_item in zip(rules_sets, rules_items):
        rule_key_ocurrences = count_occurrences_of_combinations(
            list(rule_set.keys()), transactions)
        rule_set_copy = copy(rule_set)
        for rule_key, key_ocurrences in rule_key_ocurrences.items():
            rule_occurrences = get_rule_occurrence(rule_item, transactions)
            confidence = rule_occurrences / key_ocurrences
            rule_set_copy[rule_key] = round(confidence, 2)
        rules_confidence.append(rule_set_copy)
    return rules_confidence


def get_filtered_rules(rules, rules_confidence, min_confidence):
    filtered_rules = []
    for rules_set_confidence in rules_confidence:
        filtered_rule_set = {}
        for rule_key, value in rules_set_confidence.items():
            if value >= min_confidence:
                filtered_rule_set[rule_key] = value
        filtered_rules.append(filtered_rule_set)
    return filtered_rules


def print_output(rules, filtered_rules_keys_by_confidence):
    output = []
    for rules_set, rules_filtered_set in zip(rules, filtered_rules_keys_by_confidence):
        for rules_set_key, rules_filtered_key in zip(rules_set, rules_filtered_set):
            rule_size = len((rules_filtered_key + "," +
                             " ".join(rules_set[rules_filtered_key])).split(","))
            output.append(["Rule: %s -> %s . Confidence: %.2f" % (rules_filtered_key, " ".join(
                rules_set[rules_filtered_key]), rules_filtered_set[rules_filtered_key]), rule_size, rules_filtered_set[rules_filtered_key]])
    rules = sorted(output, key=operator.itemgetter(1, 2))
    for rule in rules:
      print(rule[0])

def read():
    filename = open(sys.argv[1], "r")
    min_support = int(sys.argv[2])
    min_confidence = float(sys.argv[3])
    file_string = filename.read()
    file_lines = file_string.split("\n")
    file_lines = list(map(lambda file_line: file_line.split(), file_lines))
    return file_lines, min_support, min_confidence


def main():
    transactions, min_support, min_confidence = read()

    initial_combination = get_initial_combination(transactions)
    rules_string_items = generate_rules_items(
        transactions, min_support, initial_combination, 2, [])
    rules_items = list_of_strings_to_list_of_lists(rules_string_items)
    rules = generate_rules(rules_items)
    rules_confidence = get_rules_confidence(rules, rules_items, transactions)
    filtered_rules_keys_by_confidence = get_filtered_rules(
        rules, rules_confidence, min_confidence)
    print_output(rules, filtered_rules_keys_by_confidence)


main()
