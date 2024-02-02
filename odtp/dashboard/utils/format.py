def pd_transform_db_lists(items_list):
    if not items_list:
        return []
    return [str(item) for item in items_list]


def pd_lists_to_counts(items_list):
    if not items_list:
        return 0
    return len([str(item) for item in items_list])