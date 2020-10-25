#!/usr/bin/env python
class JsonTraverse:
    """
    Traverse a json dict.
    Usage:
        >> json_dict = json.load(json_file)
        >> traverser = JsonTraverse(data)
    value = traverser(['interface_speed', 'current', 'string'], default="UNKNOWN", starting_default_index=2)
    """
    def __init__(self, json_dict):
        self.json_dict = json_dict

    def __call__(self, nested_keys, default, attribute=None, starting_default_index=None):
        return self._inner_deep_dict_traverse(collection=self.json_dict, nested_keys=nested_keys,
                                              attribute=attribute, default=default,
                                              starting_default_index=starting_default_index,
                                              depth=0)

    @staticmethod
    def _inner_deep_dict_traverse(collection, nested_keys, default, attribute, starting_default_index, depth):
        starting_default_index = starting_default_index if starting_default_index is not None else len(nested_keys)

        for idx, cur_key in enumerate(nested_keys):
            if isinstance(collection, dict):
                # go deep
                depth += 1
                try:
                    collection = collection[cur_key]
                except KeyError as e:
                    # Key is not found in dict: wrong path
                    if default and idx >= starting_default_index:
                        return default
                    # No default or index is below starting default index
                    JsonTraverse._raise_exception(nested_keys, attribute, e)

            elif isinstance(collection, list):
                # go wide
                for item_list in collection:
                    if not isinstance(item_list, (dict, list)):
                        # Ignore all non dict\list
                        continue

                    try:
                        # recursion with dict\list and the next nested_keys
                        # fix starting default index to the new structure
                        collection = JsonTraverse._inner_deep_dict_traverse(
                            collection=item_list,
                            nested_keys=[cur_key] + nested_keys[idx + 1:],
                            attribute=attribute,
                            default=default,
                            starting_default_index=starting_default_index - depth,
                            depth=depth
                        )
                        return collection
                    except KeyError as e:
                        # Key was not found in list - continue with next list item
                        continue
                else:
                    # No list item fit nested keys: wrong path
                    JsonTraverse._raise_exception(nested_keys, attribute)
            else:
                raise AssertionError(f"Type not supported (yet): {type(collection)}")

        # Finished looking - return the last collection or value (str, int, float, etc)
        return JsonTraverse._check_attribute(collection, attribute, nested_keys)

    @staticmethod
    def _check_attribute(collection, attribute, nested_keys):
        if not attribute:
            return collection
        try:
            return next(col for key, value in attribute.items() for col in collection if col[key] == value)
        except StopIteration as e:
            raise JsonTraverse._raise_exception(nested_keys, attribute, e)

    @staticmethod
    def _raise_exception(path, attribute, e=None):
        # do something with exception
        output = '->'.join(path)
        if attribute:
            output += f" [{attribute}]"
        raise KeyError(f"Nested path was not found in json: {output}")