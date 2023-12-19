import collections
import itertools
import re
from typing import Generator, List, Dict, Pattern, Union

from networkx import DiGraph

L = '<'
R = '>'
LEFT = '<'
RIGHT = '>'

NodeObj = collections.namedtuple('NodeObj', 'name node')


class NgrexMatch:
    """
    Match objects always have a boolean value of True.
    """

    def __init__(self, pattern: 'NgrexPattern', graph: DiGraph, nodes: List[NodeObj]):
        """
        Args:
            pattern: The expression object whose `finditer()` produced this instance
            graph: The graph passed to `finditer()`
            nodes:
        """
        self.pattern = pattern
        self.graph = graph
        self.nodes = nodes

    def __bool__(self):
        return True

    def group(self, group: Union[int, str]):
        """
        Returns the input node captured by the given group during the previous match operation.
        If a group number is negative or larger than the number of groups defined in the pattern,
        an IndexError exception is raised.

        If the pattern uses the name syntax, the group argument may also be a string identifying
        the group by its name. If a string argument is not used as a group name in the pattern,
        an IndexError exception is raised.

        Raises:
            IndexError
        """
        if isinstance(group, int):
            return self.nodes[group].node
        elif isinstance(group, str):
            for node in self.nodes:
                if node.name == group:
                    return node.node
            raise IndexError(group)
        else:
            raise TypeError(type(group))

    def groups(self):
        """
        Returns a list containing all the subgroups of the match, from 0 up to however many nodes
        are in the pattern.
        """
        return (node.node for node in self.nodes)


class NgrexPattern:
    """
    A NgrexPattern is a tgrep-type pattern for matching node configurations in Networkx structures.
    """

    def __init__(self):
        # The pattern string from which the ngrex object was compiled.
        self.pattern = ''  # type: str

    def finditer(self, graph: DiGraph) -> Generator[NgrexMatch, None, None]:
        """
        Returns an iterator yielding MatcherObj instances over all matches for the ngrex pattern 
        in graph.
        """
        raise NotImplementedError

    def __str__(self):
        return self.pattern


class NodePattern(NgrexPattern):
    def __init__(self, attributes: Dict[str, str], name: str = None):
        super(NodePattern, self).__init__()
        self.name = name
        self.attributes = _get_attributes_regex(attributes)
        self.pattern = '{' + _attributes_to_str(self.attributes) + '}'
        if name:
            self.pattern += '=' + name

    def finditer(self, graph):
        for node in graph.nodes():
            if self.attributes:
                if _match(self.attributes, graph.nodes[node]):
                    yield NgrexMatch(self, graph, [NodeObj(self.name, node)])
            else:
                yield NgrexMatch(self, graph, [NodeObj(self.name, node)])


class EdgePattern(NgrexPattern):
    def __init__(self, governor: NgrexPattern, dependant: NgrexPattern, edge_attributes,
                 direction: str = LEFT):
        """
        Args:
            direction: right if 'governor >edge dependant', left if 'dependant <edge governor'
        """
        super(EdgePattern, self).__init__()
        self.governor = governor
        self.dependant = dependant
        self.direction = direction
        self.edge_attributes = _get_attributes_regex(edge_attributes)

        if self.direction == LEFT:
            args = (dependant, '<', governor)
        else:
            args = (governor, '>', dependant)
        self.pattern = '(%s) %s{%s} (%s)' % (args[0].pattern,
                                             args[1],
                                             _attributes_to_str(self.edge_attributes),
                                             args[2].pattern)

    def finditer(self, graph):
        governors = self.governor.finditer(graph)
        dependants = self.dependant.finditer(graph)
        for gov, dep in itertools.product(governors, dependants):
            for parent, child, e in graph.edges(data=True):
                if parent == gov.group(0) and child == dep.group(0):
                    if _match(self.edge_attributes, e):
                        if self.direction == LEFT:
                            yield NgrexMatch(self, graph, dep.nodes + gov.nodes)
                        else:
                            yield NgrexMatch(self, graph, gov.nodes + dep.nodes)


class CoordinationPattern(NgrexPattern):
    def __init__(self, pattern1: NgrexPattern, pattern2: NgrexPattern, is_conj: bool = True):
        """
        Args:
            is_conj: if is_conj is true, then it is an "AND"; otherwise, it is an "OR".
        """
        super(CoordinationPattern, self).__init__()
        self.pattern1 = pattern1
        self.pattern2 = pattern2
        self.is_conj = is_conj
        self.pattern = '{} {} {}'.format(pattern2.pattern,
                                         '&' if is_conj else '|',
                                         pattern1.pattern)

    def finditer(self, graph):
        if self.is_conj:
            matchers1 = self.pattern1.finditer(graph)
            matchers2 = self.pattern2.finditer(graph)
            for m1, m2 in itertools.product(matchers1, matchers2):
                if m1.group(0) == m2.group(0):
                    nodes = list(m1.nodes)
                    if len(m2.nodes) > 2:
                        nodes.extend(m2.nodes[1:])
                    yield NgrexMatch(self, graph, nodes)
        else:
            yield from self.pattern1.finditer(graph)
            yield from self.pattern2.finditer(graph)


def validate_names(pattern):
    def _helper(p, names):
        if isinstance(p, NodePattern):
            if p.name in names and names[p.name] != p:
                raise KeyError(p.name)
            if p.name:
                names[p.name] = p
        elif isinstance(p, EdgePattern):
            _helper(p.governor, names)
            _helper(p.dependant, names)
        elif isinstance(p, CoordinationPattern):
            _helper(p.pattern1, names)
            _helper(p.pattern2, names)

    _helper(pattern, {})


def _get_attributes_regex(attributes: Dict[str, str]) -> Dict[str, Pattern]:
    def _get_regex(v):
        # remove /xxxx/
        v = v[1:-1]
        if v:
            if v[0] != '^':
                v = '^' + v
            if v[-1] != '$':
                v += '$'
        return re.compile(v)

    return {k: _get_regex(v) for k, v in attributes.items()}


def _match(attributes, element):
    for k, v in attributes.items():
        if k not in element or not v.match(element[k]):
            return False
    return True


def _attributes_to_str(attributes):
    return ','.join(['{}:/{}/'.format(k, v.pattern) for k, v in attributes.items()])
