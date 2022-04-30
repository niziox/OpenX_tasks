import urllib.request
import json
from copy import copy
import argparse

# node representing each seller
class Node:
    def __init__(self, seller_id, name, domain, seller_type, is_passthrough, depth=1, leaf=False):
        self.seller_id = seller_id
        self.name = name
        self.domain = domain
        self.seller_type = seller_type
        self.is_passthrough = is_passthrough
        self.depth = depth
        self.leaf = leaf
        if not leaf:
            self.leaves = []

    def __str__(self):
        return str(self.seller_id)


class SupplyChain:
    def __init__(self):
        self.root_name = 'OpenX'
        self.leaves = []
        self.max_depth = 0
        self.insert()

    # insert data from json
    def insert(self):

        def _insert(node_depth, domain_name):
            nodes_list = []

            # 'if' because of lack of data, this example only have ascendeum json
            url_path = 'https://' + str(domain_name) + '/sellers.json'
            if str(domain_name) == 'ascendeum.com':
                with urllib.request.urlopen(url_path) as url:
                    data_leaf = json.loads(url.read().decode())

                    for i in data_leaf['sellers']:
                        is_leaf = i['seller_type'] == 'PUBLISHER'
                        if not is_leaf:
                            node_depth += 1
                        new_node = Node(i['seller_id'], i['name'], i['domain'], i['seller_type'], i['is_passthrough'],
                                        node_depth, is_leaf)

                        nodes_list.append(new_node)

                        if is_leaf:
                            if new_node.depth > self.max_depth:
                                self.max_depth = new_node.depth

                        if not is_leaf:
                            nodes = _insert(new_node.depth, i['domain'])

                            new_node.leaves = copy(nodes)

            return nodes_list

        with urllib.request.urlopen("https://openx.com/sellers.json") as url:
            data = json.loads(url.read().decode())

        for i in data['sellers']:
            is_leaf = i['seller_type'] == 'PUBLISHER'
            new_node = Node(i['seller_id'], i['name'], i['domain'], i['seller_type'], i['is_passthrough'], 1, is_leaf)
            self.leaves.append(new_node)

            if not is_leaf:
                nodes = _insert(new_node.depth, i['domain'])

                new_node.leaves = copy(nodes)

    # checking if domain is direct or indirect
    def is_direct(self, domain_name):

        def _is_direct(domain_name, node):
            for i in node:
                if i.domain == domain_name:
                    return 'indirect' if i.seller_type == 'INTERMEDIARY' else 'direct'

                # 'if' because of lack of data, this example only have ascendeum json
                if str(i.domain) == 'ascendeum.com':
                    if not i.leaf:
                        _is_direct(domain_name, i.leaves)

        return _is_direct(domain_name, self.leaves)

    def __str__(self):
        return str(self.leaves)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain")
    args = parser.parse_args()
    config = vars(args)
    domain_name = 'gamepress.gg' if str(config['domain']) == 'None' else str(config['domain'])

    # creating an instance of a class
    sup_chain = SupplyChain()

    # printing the maximum depth of our Supply Chain
    print(f'\nmaximum depth of the Supply Chain: {sup_chain.max_depth}\n')

    # checking if a domain is direct or indirect Seller
    print(f'Is {domain_name} direct or indirect?: {sup_chain.is_direct(domain_name)}\n')
