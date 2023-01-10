import pandas as pd
import sys
from basismass import Basismass
from basismass_entry import Basismass_Entry

######################################################################
#### FUNCTIONS #######################################################
######################################################################

# reads the data subset from the csv file
def read_data_subset():
    return pd.read_csv("iris.data_subset_2.csv").to_numpy()

# reads the program arguments from stdin
def read_arguments():
    arguments = {
        "sepal-length": 0,
        "sepal-width": 0,
        "petal-length": 0,
        "petal-width": 0
    }

    for index, argument in enumerate(sys.argv):
        if argument == "--sepal_length":
            arguments["sepal-length"] = float(sys.argv[index + 1])
        elif argument == "--sepal_width":
            arguments["sepal-width"] = float(sys.argv[index + 1])
        elif argument == "--petal_length":
            arguments["petal-length"] = float(sys.argv[index + 1])
        elif argument == "--petal_width":
            arguments["petal-width"] = float(sys.argv[index + 1])

    return arguments


# configuration of the csv entries and the lookup values
# subset_index: the column index of the corresponding subset
# interval: the lookup interval for a given subset
#           entries in this interval are considered for the creation of the corresponding measure
# class_index: the column index of the entries class
# evidenz: the evidenz of the data
#          all values except omega of a measure equal either the evidenz or 0
#          the omega value equals either 1 - evidenz or 1
lookup_configuration = {
    "sepal-length": {
        "subset_index": 0,
        "interval": 1
    },
    "sepal-width": {
        "subset_index": 1,
        "interval": 0.5
    },
    "petal-length": {
        "subset_index": 2,
        "interval": 1
    },
    "petal-width": {
        "subset_index": 3,
        "interval": 0.5
    },
    "class_index": 4,
    "evidenz": 0.9
}

# defines the possible classes
plant_classes = {"Iris-setosa", "Iris-versicolor", "Iris-virginica"}

# creates the measure of a single subset and test value.
# it counts all entries in the definied lookup interval for the subset around the test value.
# afterwards it determines the relative values of each class and adjusts them to the definied evidenz.
# if there are no entries in the interval, the omega value is 1. Otherwise the omega value is 1 - evidenz
def get_basismass(subset_name, test_value, data_array) -> Basismass:
    class_values = {}
    for plant_class in plant_classes:
        class_values[plant_class] = 0

    # get total amount for each class in configured interval around the test value
    for data_row in data_array:
        data_value = data_row[lookup_configuration[subset_name]["subset_index"]]
        data_class = data_row[lookup_configuration["class_index"]]
        lookup_interval = lookup_configuration[subset_name]["interval"]

        if data_value > (test_value - lookup_interval) and data_value < (test_value + lookup_interval):
            class_values[data_class] = class_values[data_class] + 1

    # get and return relative amount of each class
    total_value = 0
    for plant_class in plant_classes:
        total_value = total_value + class_values[plant_class]

    if total_value == 0:
        return Basismass(plant_classes)
    else:
        basismass = Basismass(plant_classes)
        for plant_class in plant_classes:
            probability = class_values[plant_class] / total_value * lookup_configuration["evidenz"]
            basismass.set_entry_probability({plant_class}, probability)

        omega_probability = 1 - lookup_configuration["evidenz"]
        basismass.set_omega_probability(omega_probability)
        return basismass

# uses the dempster rule on the two given measures and returns the accumulated and corrected measure.
def dempster_regel(basismass1: Basismass, basismass2: Basismass):
    accumulated_basismass = Basismass(plant_classes)
    accumulated_basismass.set_omega_probability(0)

    for entry1 in basismass1.get_entries():
        for entry2 in basismass2.get_entries():
            accumulated_basismass = use_dempster_regel_for_entries(entry1, entry2, accumulated_basismass)

    accumulated_basismass.correct_conflict()
    return accumulated_basismass

# uses the dempster rule for the two given entries of the two given measures and returns the updated accumulated measure
def use_dempster_regel_for_entries(
    entry1: (Basismass_Entry),
    entry2: (Basismass_Entry),
    accumulated_basismass: Basismass
) -> Basismass:

    # handle special Omega case
    if entry1.is_omega and entry2.is_omega:
        old_value = accumulated_basismass.get_omega_probability()
        new_value = old_value + entry1.probability * entry2.probability
        accumulated_basismass.set_omega_probability(new_value)
    elif entry1.is_omega:
        old_value = accumulated_basismass.get_entry_probability(entry2.values)
        new_value = old_value + entry1.probability * entry2.probability
        accumulated_basismass.set_entry_probability(entry2.values, new_value)
    elif entry2.is_omega:
        old_value = accumulated_basismass.get_entry_probability(entry1.values)
        new_value = old_value + entry1.probability * entry2.probability
        accumulated_basismass.set_entry_probability(entry1.values, new_value)
    else:
        common_values = entry1.get_subset_of_values(entry2.values)
        old_value = accumulated_basismass.get_entry_probability(common_values)
        new_value = old_value + entry1.probability * entry2.probability
        accumulated_basismass.set_entry_probability(common_values, new_value)

    return accumulated_basismass

######################################################################
#### MAIN ############################################################
######################################################################

arguments = read_arguments()
csv_data = read_data_subset()

m0 = get_basismass("sepal-length", arguments["sepal-length"], csv_data)
m1 = get_basismass("sepal-width", arguments["sepal-width"], csv_data)
m2 = get_basismass("petal-length", arguments["petal-length"], csv_data)
m3 = get_basismass("petal-width", arguments["petal-width"], csv_data)

m4 = dempster_regel(m0, m1)
m5 = dempster_regel(m4, m2)
m6 = dempster_regel(m5, m3)
print(m6.to_dictionary())