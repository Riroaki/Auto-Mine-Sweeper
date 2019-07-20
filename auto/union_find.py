"""
Use union find to form disjoint groups from edges <i, j>.
"""


def union_find(edges: list, n: int) -> list:
    # Use union find to form disjoint groups
    def find_root(x: int) -> int:
        if root_list[x] == x:
            return x
        else:
            root_list[x] = find_root(root_list[x])
            return root_list[x]

    root_list = [i for i in range(n)]
    for p, q in edges:
        root_p = find_root(p)
        root_q = find_root(q)
        # Join two relations
        if root_p != root_q:
            root_list[root_q] = root_p
    # Compress root
    for i in range(n):
        find_root(i)
    # Form groups, each group has same roots
    group_dict = {}
    for i in range(n):
        root = root_list[i]
        if root not in group_dict:
            group_dict[root] = [i]
        else:
            group_dict[root].append(i)
    group_list = list(group_dict.values())
    return group_list


def test():
    # Test codes
    edge_list = [(1, 2), (3, 4), (2, 3), (6, 8), (5, 6), (9, 0)]
    total = 10
    print(union_find(edge_list, total))


if __name__ == '__main__':
    test()
