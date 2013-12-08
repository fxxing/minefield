#!/usr/bin/env python
# coding: utf-8

import os
import sys
import re
import pydot


CLASS_PATTERN = re.compile(ur"@interface\s+(?P<class>\w+)\s*:\s*(?P<superclass>\w+)(\s*<(?P<protocols>.*)>)?")
PROTOCOL_PATTERN = re.compile(ur"@protocol\s+(?P<protocol>\w+)(\s*<\s*(?P<superprotocol>\w+)\s*>)?")


class ObjcType(object):
    def __init__(self):
        super(ObjcType, self).__init__()
        self.name = ""

    def get_super(self):
        pass

    def get_children(self):
        pass

    def __eq__(self, other):
        return self.name == other.name


class ObjcClass(ObjcType):
    def __init__(self):
        super(ObjcClass, self).__init__()

        self.superclass = None
        self.subclasses = set()
        self.protocols = set()

    def get_super(self):
        return self.superclass

    def get_children(self):
        return self.subclasses


class ObjcProtocol(ObjcType):
    def __init__(self):
        super(ObjcProtocol, self).__init__()

        self.superprotocol = None
        self.subprotocols = set()

    def get_super(self):
        return self.superprotocol

    def get_children(self):
        return self.subprotocols


class ObjcParser(object):
    def __init__(self, dirs):
        super(ObjcParser, self).__init__()

        self.dirs = dirs
        self.classes = {}
        self.protocols = {}

    def parse(self):
        for adir in self.dirs:
            self._parse_path(adir)

    def dump(self):
        print "========== PROTOCOLS =========="
        self._dump_hierarchy(self.protocols)
        print
        print "========== CLASSES =========="
        self._dump_hierarchy(self.classes)

    def write_graphviz(self):
        self._write_graphviz("protocol", self.protocols)
        # self._write_graphviz("class", self.classes)

    def write_node(self, node_name, end_nodes):
        graph_name = node_name.lower()
        graph = pydot.Dot(graph_name, graph_type="digraph", rankdir="RL")

        def _write_node(node):
            graph.add_node(pydot.Node(node.name, shape="box"))
            if node.name != node_name and node.get_super():
                graph.add_edge(pydot.Edge(src=node.name, dst=node.get_super().name))
            if node.name not in end_nodes:
                for subnode in node.get_children():
                    _write_node(subnode)

        _write_node(self.classes[node_name])

        graph.write(graph_name + ".dot", format="raw")
        graph.write(graph_name + ".png", format="png")

    def _write_graphviz(self, name, holder):
        graph = pydot.Dot(name, graph_type="digraph", rankdir="RL")
        for node in holder.values():
            graph.add_node(pydot.Node(node.name, shape="box"))
            if node.get_super():
                graph.add_edge(pydot.Edge(src=node.name, dst=node.get_super().name))
        graph.write(name + ".dot", format="raw")
        graph.write(name + ".png", format="png")

    def _parse_path(self, adir):
        for root, dirs, files in os.walk(adir):
            for filename in files:
                if not (filename.endswith(".h") or filename.endswith(".m")):
                    continue
                content = self._read_file(os.path.join(root, filename))
                self._parse_classes(content)
                self._parse_protocols(content)

    def _get_or_create(self, holder, name, instance_class):
        if name in holder:
            value = holder[name]
        else:
            value = instance_class()
            value.name = name
            holder[name] = value
        return value

    def _parse_classes(self, content):
        for match in CLASS_PATTERN.finditer(content):
            class_name = match.group("class")
            superclass_name = match.group("superclass")
            protocols = match.group("protocols")
            if protocols:
                protocol_names = [name.strip() for name in protocols.split(",")]
            else:
                protocol_names = []
            aclass = self._get_or_create(self.classes, class_name, ObjcClass)
            superclass = self._get_or_create(self.classes, superclass_name, ObjcClass)
            aclass.superclass = superclass
            superclass.subclasses.add(aclass)
            for protocol_name in protocol_names:
                protocol = self._get_or_create(self.protocols, protocol_name, ObjcProtocol)
                aclass.protocols.add(protocol)

    def _parse_protocols(self, content):
        for match in PROTOCOL_PATTERN.finditer(content):
            protocol_name = match.group("protocol")
            superprotocol_name = match.group("superprotocol")
            protocol = self._get_or_create(self.protocols, protocol_name, ObjcProtocol)
            if superprotocol_name:
                superprotocol = self._get_or_create(self.protocols, superprotocol_name, ObjcProtocol)
                superprotocol.subprotocols.add(protocol)
                protocol.superprotocol = superprotocol

    def _find_root(self, holder):
        roots = []
        for value in holder.values():
            if not value.get_super():
                roots.append(value)
        return roots

    def _dump_hierarchy(self, holder):
        roots = self._find_root(holder)

        def _dump_node(node, level):
            line = '    ' * level + node.name
            # hack
            if hasattr(node, 'protocols'):
                line += '    ' + " ".join([p.name for p in node.protocols])

            print line
            for sub in node.get_children():
                _dump_node(sub, level + 1)

        for root in roots:
            _dump_node(root, 0)

    def _read_file(self, path):
        fp = open(path, "r")
        content = fp.read()
        fp.close()
        return content


if __name__ == "__main__":
    paths = sys.argv[1:]
    parser = ObjcParser(paths)
    parser.parse()
    # parser.write_node("CCNode", ["CCTransitionScene", "CCParticleSystemQuad"])
    # parser.write_node("CCTransitionScene", [])
    # parser.write_node("CCMenuItem", [])
    # parser.write_node("CCAction", ["CCActionInterval", "CCActionInstant"])
    parser.write_node("CCActionInterval", [])
    # parser.write_node("CCActionInstant", [])
    # parser.dump()
    # parser.write_graphviz()