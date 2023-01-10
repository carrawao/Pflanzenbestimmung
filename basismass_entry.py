class Basismass_Entry:

    def __init__(self, values: set, probability: float, is_omega: bool) -> None:
        self.values = values
        self.probability = probability
        self.is_omega = is_omega

    def are_values_equal_to(self, values_to_check: set) -> bool:
        return (self.values == values_to_check)

    def get_subset_of_values(self, values: set) -> set:
        return self.values.intersection(values)

    def set_probability(self, probability: float):
        self.probability = probability