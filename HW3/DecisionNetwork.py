"""
    Homework 3 for CSCI561: Introduction to Artificial Intelligence.
    Implementation of Decision Network based on Bayesian Network.
    Copyright by Zhiyuan Wang.
"""

"""
    Definition of 3 types of nodes in the network.
"""
class ChanceNode:
    name = ''
    parents = []
    prob_table = None  # the type of key in prob_table should change from strings to tuple!!!
    value = False  # for substitution when doing inference

    def __init__(self, name, parents, prob_table):
        self.name = name
        self.parents = parents
        self.prob_table = prob_table

    """
        Get probability of certain value, given evidences.
        @:param value: True or False.
        @:param evidences: a dict containing the evidences.
    """
    def get_prob(self, value, evidences):
        prob = self.prob_table[get_values_in_event(evidences, self.parents)]
        return prob if value else (1 - prob)


class DecisionNode:
    name = ''
    value = False  # for substitution when doing inference

    def __init__(self, name):
        self.name = name


class UtilityNode:
    name = ''
    parents = []
    val_table = None

    def __init__(self, name, parents, val_table):
        self.name = name
        self.parents = parents
        self.val_table = val_table

    """
        Given a certain event, return the corresponding utility value.
        @:param event: a dict containing its parents' value.
    """
    def get_utility_value(self, event):
        return self.val_table[get_values_in_event(event, self.parents)]

"""
    Definition of a query to do with the network.
"""
class Query:
    type = ''  # 'P', 'EU' or 'MEU'
    query_var = None  # a dict or a list
    evidence_var = None  # a dict

    def __init__(self, query_type, query_var, evidence_var):
        self.type = query_type
        self.query_var = query_var
        self.evidence_var = evidence_var

"""
    Definition of a Factor data structure.
    @:parameter variable_list
    @:parameter cpt: conditional probability table. A dict whose keys are tuple of values (e.g. (True, False, True)),
        and values are probabilities of the tuples. The values in the tuple are in the order of variable_list.
"""
class Factor:
    variable_list = []
    cpt = None

    def __init__(self, var_list, prob):
        self.variable_list = var_list
        self.cpt = prob

    """
        Get probability of a certain event.
    """
    def get_prob(self, event):
        return self.cpt[get_values_in_event(event, self.variable_list)]

    """
        Do the multiply of two factors pointwisely.
    """
    @staticmethod
    def pointwise_multiply(factor1, factor2, network):
        list_vars = list(set(factor1.variable_list) | set(factor2.variable_list))
        prob_table = dict()
        for event in get_all_events(network, list_vars, {}):
            prob_table[get_values_in_event(event, list_vars)] = factor1.get_prob(event) * factor2.get_prob(event)
        return Factor(list_vars, prob_table)

    """
        Eliminate some specific variable by summing up its corresponding dimensions.
    """
    def sum_out(self, var_name, decision_network):
        list_vars = [name for name in self.variable_list if name != var_name]
        prob_table = dict()
        for event in get_all_events(decision_network, list_vars, {}):
            prob_table[get_values_in_event(event, list_vars)] = (self.get_prob(extend(event, var_name, True))
                                                                  + self.get_prob(extend(event, var_name, False)))
        return Factor(list_vars, prob_table)

    """
        Normalize all the probabilities in each entry, i.e. to make sure the sum of all entries is 1.
    """
    def normalize(self):
        total = 0
        for key, value in self.cpt.iteritems():
            total += value
        for key, value in self.cpt.iteritems():
            self.cpt[key] = value / total
        return self


"""
    The class representing the decision network.
    Contains lists of chance nodes, decision nodes and utility node.
"""
class DecisionNetwork:
    list_chance_node = []
    list_decision_node = []
    local_utility_node = None
    name_to_pos_dict = None
    list_vars = []

    def __init__(self, chance_nodes, decision_nodes, this_utility_node, name_dict):
        self.list_chance_node = chance_nodes
        self.list_decision_node = decision_nodes
        self.local_utility_node = this_utility_node
        self.name_to_pos_dict = name_dict
        for node in self.list_chance_node:
            self.list_vars.append(node.name)

    """
        Handle the query by calling different query handler with respect to the query type.
        @:param query: an object in the class of Query.
    """
    def handle_query(self, query):
        if query.type == 'P':
            result = self.prob_query_handler(query.query_var, query.evidence_var)
            return "{0:.2f}".format(result)
        elif query.type == 'EU':
            result = self.exp_util_handler(query.query_var, query.evidence_var)
            return int(round(result))
        elif query.type == 'MEU':
            meu, action = self.max_exp_util_handler(query.query_var, query.evidence_var)
            string = ""
            for logic in action:
                string += (('+' if logic else '-') + ' ')
            string += str(int(round(meu)))
            return string

    def prob_query_handler(self, query_vals, evidence_vals):
        query_vars = []
        for key, value in query_vals.iteritems():
            query_vars.append(key)
        factor = self.elimination_ask(query_vars, evidence_vals)
        # factor is a Factor object
        event = evidence_vals.copy()
        event.update(query_vals)
        return factor.get_prob(get_values_in_event(event, factor.variable_list))

    def exp_util_handler(self, query_vals, evidence_vals):
        # assert utility_node != None
        new_evidences = evidence_vals.copy()
        new_evidences.update(query_vals)
        vars_list = [name for name in self.local_utility_node.parents if name not in new_evidences]
        factor = self.elimination_ask(vars_list, new_evidences)
        total = 0
        for event in get_all_events(self, vars_list, new_evidences):
            total += factor.get_prob(get_values_in_event(event, factor.variable_list)) \
                     * utility_node.get_utility_value(event)
        return total

    def max_exp_util_handler(self, query_nodes, evidence_vals):
        candidate_events = get_all_events(self, query_nodes, {})  # possible assignments to query nodes
        # additional dimensions
        hidden_vars = [name for name in self.local_utility_node.parents
                       if name not in evidence_vals and name not in query_nodes]
        max_eu = float("-inf")
        best_action = ()
        for candidate_event in candidate_events:
            evidence = evidence_vals.copy()
            evidence.update(candidate_event)  # update with candidate event
            factor = self.elimination_ask(hidden_vars, evidence_vals)
            # for name in hidden_vars:
            #    factor = factor.sum_out(name, self)
            total = 0
            total_prob = 0
            for event in get_all_events(self, hidden_vars, evidence):
                # total += factor.get_prob(get_values_in_event(event, factor.variable_list)) \
                #         * utility_node.get_utility_value(event)
                prob = factor.get_prob(event)
                total_prob += prob
                # total += factor.get_prob(event) * self.local_utility_node.get_utility_value(event)
                total += prob * self.local_utility_node.get_utility_value(event)
            total /= total_prob
            if total > max_eu:
                max_eu = total
                best_action = get_values_in_event(evidence, query_nodes)
        return max_eu, best_action

    """
        Core algorithm. Do the query with elimination variable algorithm.
        @:param query_vars: a dict whose entry is variable name and value is True or False.
        @:param evidence: a dict similar to query_vars. But is the evidence of the query.
    """
    def elimination_ask(self, query_vars, evidence):
        factors = []
        vars_list = self.get_relevant_vars(query_vars, evidence)
        # while len(vars) > 0:
        for var_name in reversed(vars_list):
            # var_name = self.select_next_var(vars, factors)
            factors.append(self.make_factor(var_name, evidence))
            if var_name not in query_vars and var_name not in evidence:
                factors = self.sum_out(var_name, factors)
        return self.pointwise_product(factors).normalize()

    """
        Make a new factor with respect to the variable name and existing evidences.
    """
    def make_factor(self, var, evidences):
        var_list = []
        prob_table = dict()
        if var not in evidences:
            var_list.append(var)
        chance_node = self.list_chance_node[self.name_to_pos_dict[var][1]]
        for p in chance_node.parents:
            if p not in evidences:
                var_list.append(p)
        for event in get_all_events(self, var_list, evidences):
            prob_table[get_values_in_event(event, var_list)] = chance_node.get_prob(event[var], event)
        return Factor(var_list, prob_table)

    """
        Do the pointwise multiply to a list of factors to get a final factor which is the product of the list.
        @:param factors: a list of factors.
    """
    def pointwise_product(self, factors):
        return reduce(lambda f, g: Factor.pointwise_multiply(f, g, self), factors)

    """
        Eliminate some specific variable in the list of factors by summing out corresponding entries.
    """
    def sum_out(self, name, factors):
        result, factor_containing_name = [], []
        for factor in factors:
            if name in factor.variable_list:
                factor_containing_name.append(factor)
            else:
                result.append(factor)
        result.append(self.pointwise_product(factor_containing_name).sum_out(name, self))
        return result

    """
        An optimization method to reduce the variables to be considered by only counting the ancestors of query
        and evidence variables.
        Performed a DFS on the ancestors of all the variables in query variables and evidences, and sorted them in
        the order of occurance in the original text.
    """
    def get_relevant_vars(self, query_vars, evidence):
        relevant_vars = []
        check_list = []
        for x in query_vars:
            if x in self.list_vars:
                check_list.append(x)
        for key, value in evidence.iteritems():
            # only investigate chance nodes, don't put decision nodes in relevant vars
            if self.name_to_pos_dict[key][0] == 'c' and key not in check_list:
                check_list.append(key)
        while len(check_list) > 0:
            first = check_list.pop(0)
            if first not in relevant_vars:
                relevant_vars.append(first)
                the_tuple = self.name_to_pos_dict[first]
                if the_tuple[0] == 'c':
                    for p in self.list_chance_node[the_tuple[1]].parents:
                        if self.name_to_pos_dict[p][0] == 'c':
                            check_list.append(p)
            # else: if first is already in the relevant_vars, then its parents must already in the checklist
        relevant_vars.sort(lambda a, b: self.list_vars.index(a) - self.list_vars.index(b))
        for x in query_vars:
            if x not in self.list_vars and x not in relevant_vars:
                relevant_vars.append(x)
        return relevant_vars

"""
    Get all the events (value assignments to all variables).
    @:param list_vars: list of variable names
    @:param evidences: dict of evidence variable value assignments.
    @:return an iterator of a list of all possible events.
"""
def get_all_events(network, list_vars, evidences):
    if len(list_vars) == 0:
        yield evidences
    else:
        first, rest_vars = list_vars[0], list_vars[1:]
        for event in get_all_events(network, rest_vars, evidences):
            for x in [True, False]:
                yield extend(event, first, x)

"""
    Helper method, to extend the existing dict by adding new entries.
"""
def extend(evidences, name, value):
    new_evidences = evidences.copy()
    # if isinstance(name, list) and isinstance(value, list):
    new_evidences[name] = value
    return new_evidences

"""
    Helper method. Get values of variables in the event in the form of tuple.
"""
def get_values_in_event(event, list_vars):
    if isinstance(event, tuple) and len(event) == len(list_vars):
        return event
    else:
        return tuple([event[name] for name in list_vars])

"""
    Below is some functions dealing with the input.
"""
def read_query_and_evidence_vars(param):
    query_var = dict()
    evidence_var = dict()
    query_str = param[0].split(',')
    for string in query_str:
        chars = string.split()
        if len(chars) == 3:
            name = chars[0]
            val = chars[2] == '+'
            query_var[name] = val
    if len(param) == 2:
        evidence_str = param[1].split(',')
        for item in evidence_str:
            chars = item.split()
            if len(chars) == 3:
                name = chars[0]
                val = chars[2] == '+'
                evidence_var[name] = val
    return query_var, evidence_var


def read_query_line(line):
    if line[:1] == 'P':
        q_type = 'P'
        param = line[2:-1].split('|')
        query_var, evidence_var = read_query_and_evidence_vars(param)
        return Query(q_type, query_var, evidence_var)
    elif line[:2] == 'EU':
        q_type = 'EU'
        param = line[3:-1].split('|')
        query_var, evidence_var = read_query_and_evidence_vars(param)
        return Query(q_type, query_var, evidence_var)
    else:  # MEU
        q_type = 'MEU'
        query_var = []
        evidence_var = dict()
        param = line[4:-1].split('|')
        query_str = param[0].split(',')
        for string in query_str:
            names = string.split()
            query_var.append(names[0])
        if len(param) == 2:
            evidence_str = param[1].split(',')
            for item in evidence_str:
                chars = item.split()
                if len(chars) == 3:
                    evidence_var[chars[0]] = chars[2] == '+'
        return Query(q_type, query_var, evidence_var)


def read_chance_node(lines):
    node_names = lines[0].split('|')
    name = node_names[0].split()[0]
    parents_names = []
    prob_table = dict()
    if len(node_names) == 2:  # has parents
        parents_names = node_names[1].split()
    for i in xrange(1, len(lines)):
        items = lines[i].split()
        values = []
        for j in xrange(1, len(items)):
            values.append(items[j] == '+')
        prob_table[tuple(values)] = float(items[0])
    return ChanceNode(name, parents_names, prob_table)


def read_utility_node(lines):
    node_names = lines[0].split('|')
    name = node_names[0].split()[0]
    if name != "utility":
        print "utility node format error!"
    parents_names = []
    val_table = dict()
    if len(node_names) == 2:
        parents_names = node_names[1].split()
    for i in xrange(1, len(lines)):
        items = lines[i].split()
        values = []
        for j in xrange(1, len(items)):
            values.append(items[j] == '+')
        val_table[tuple(values)] = int(items[0])
    return UtilityNode(name, parents_names, val_table)


def read_text_file(filename):
    res_list_of_chance_nodes = []
    res_list_of_decision_nodes = []
    res_single_utility_node = None
    res_list_of_queries = []
    res_name_to_pos_dict = dict()

    infile = open(filename, "r")
    # cache all the lines in text file
    list_of_lines = infile.read().splitlines()
    line_num = 0
    separator_line = []  # stores the positions of separator "******"
    var_sep_line = []

    for line in list_of_lines:
        if line[:6] == "******":
            separator_line.append(line_num)
        line_num += 1

    # read the queries
    for i in range(0, separator_line[0]):
        res_list_of_queries.append(read_query_line(list_of_lines[i]))

    # get the positions of separators between nodes
    var_sep_line.append(separator_line[0])
    for i in range(separator_line[0] + 1, len(list_of_lines)):
        if list_of_lines[i].count('*') == 3:
            var_sep_line.append(i)
    if len(separator_line) == 2:  # use the second separator "******\n" as end
        var_sep_line.append(separator_line[1])
    else:  # use end of file as end
        var_sep_line.append(len(list_of_lines))

    # read the chance and decision nodes
    for j in xrange(len(var_sep_line) - 1):
        start = var_sep_line[j] + 1
        end = var_sep_line[j+1]
        if list_of_lines[start+1] == "decision":
            res_list_of_decision_nodes.append(DecisionNode(list_of_lines[start]))
            res_name_to_pos_dict[res_list_of_decision_nodes[-1].name] = ('d', len(res_list_of_decision_nodes)-1)
        else:
            res_list_of_chance_nodes.append(read_chance_node(list_of_lines[start:end]))
            res_name_to_pos_dict[res_list_of_chance_nodes[-1].name] = ('c', len(res_list_of_chance_nodes)-1)

    if len(separator_line) == 2:  # one utility node
        res_single_utility_node = read_utility_node(list_of_lines[separator_line[1]+1:])
    return res_list_of_chance_nodes, res_list_of_decision_nodes, res_single_utility_node, \
           res_list_of_queries, res_name_to_pos_dict

"""
    Main method.
"""
if __name__ == '__main__':
    list_of_chance_nodes, list_of_decision_nodes, utility_node, list_of_queries, name_dict\
        = read_text_file("input.txt")
    network = DecisionNetwork(list_of_chance_nodes, list_of_decision_nodes, utility_node, name_dict)
    result_lines = []
    for query in list_of_queries:
        result_lines.append(str(network.handle_query(query)))
    outfile = open("output.txt", 'w')
    outfile.writelines("%s\n" % line for line in result_lines)
    outfile.close()