from basismass_entry import Basismass_Entry

class Basismass:
    def __init__(self, omega_values: set) -> None:
        self.omega_values = omega_values
        self.basismass_entries = []
        self.set_omega_probability(1)

    def set_entry_probability(self, entry_values: set, probability: float) -> None:

        # only accepts subsets of omega
        if (entry_values > self.omega_values):
            return

        # check for existing entry
        for basismass_entry in self.basismass_entries:
            if basismass_entry.are_values_equal_to(entry_values):
                basismass_entry.set_probability(probability)
                return

        # create new entry if no existing entry was found
        if entry_values == self.omega_values:
            self.basismass_entries.append(Basismass_Entry(entry_values, probability, True))
        else:
            self.basismass_entries.append(Basismass_Entry(entry_values, probability, False))

    def get_entry_probability(self, entry_values: set) -> float:
        for basismass_entry in self.basismass_entries:
            if basismass_entry.are_values_equal_to(entry_values):
                return basismass_entry.probability
        return 0

    def set_omega_probability(self, probability: float) -> None:
        self.set_entry_probability(self.omega_values, probability)

    def get_omega_probability(self) -> float:
        return self.get_entry_probability(self.omega_values)

    def get_entries(self) -> list:
        entries = list(self.basismass_entries)
        return entries

    def correct_conflict(self):
        conflict_probability = 0
        for entry in self.basismass_entries:
            if len(entry.values) == 0:
                conflict_probability = entry.probability
                self.basismass_entries.remove(entry)

        for entry in self.basismass_entries:
            entry.probability = entry.probability / (1 - conflict_probability)

    def to_dictionary(self) -> dict:
        converted_basismass = {
            "Omega": self.get_omega_probability()
        }
        for entry in self.basismass_entries:
            if entry.is_omega:
                continue
            key = ", ".join(entry.values)
            converted_basismass[key] = entry.probability

        return converted_basismass

    def get_belief(self, entry_values: set) -> float:
        belief = 0

        for entry in self.basismass_entries:
            if entry.is_omega:
                continue

            if entry.values <= entry_values:
                belief = belief + entry.probability

        return belief

    def get_plausibilitaet(self, entry_values: set) -> float:
        plausbilität = 0

        for entry in self.basismass_entries:
            if entry.is_omega:
                continue

            intersection = entry_values.intersection(entry.values)
            if len(intersection) != 0:
                plausbilität = plausbilität + entry.probability

        return plausbilität