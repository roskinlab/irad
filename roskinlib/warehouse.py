import sys
import pathlib

class DirectoryWarehouse:
    def __init__(self, root_directory, *partition_keys, file_leaf=True, value_encoder=str):
        self.root_directory = pathlib.Path(root_directory)
        self.partition_keys = partition_keys
        self.file_leaf = file_leaf
        self.value_encoder = value_encoder

    def filename(self, filename_or_suffix, *args, **kwargs):
        directory, filename = self._make_dir_file_name(filename_or_suffix, args, kwargs, self.value_encoder)

        # make the directory
        directory.mkdir(parents=True, exist_ok=True)

        return directory / filename

    def open(self, filename_or_suffix, mode, *args, **kwargs):
        directory, filename = self._make_dir_file_name(filename_or_suffix, args, kwargs, self.value_encoder)

        # make the diretory
        directory.mkdir(parents=True, exist_ok=True)

        return (directory / filename).open(mode=mode)

    def exists(self, filename_or_suffix, *args, **kwargs):
        directory, filename = self._make_dir_file_name(filename_or_suffix, args, kwargs, self.value_encoder)

        return (directory / filename).exists()

    def partitions(self, suffix, *positional_args, **keyvalue_args):
        # convert the positional arguments into key/value arguments
        for key, value in zip(self.partition_keys, positional_args):
            assert key not in keyvalue_args, \
                'postional partition arguments overlap with given key/value arguments'
            keyvalue_args[key] = value

        # initilize
        dir_path = self.root_directory
        values = []

        # for each partition key
        for key in self.partition_keys[:-1]:
            # if defined, add value
            if key in keyvalue_args:
                value = self.value_encoder(keyvalue_args[key])
                dir_path = dir_path / (key + '=' + value)
                values.append(value)
            else:   # or iterate over the values in the warehouse
                key_label = key + '='
                if dir_path.is_dir():
                    for level in dir_path.iterdir():
                        if level.name.startswith(key_label):
                            value = level.name[len(key_label):]
                            yield from self.partitions(suffix, **keyvalue_args, **{key: value})
                break
        else:
            # the last value is treated differently
            if self.file_leaf:
                # if the final key is given
                final_key = self.partition_keys[-1]
                if final_key in keyvalue_args:
                    final_value = keyvalue_args[final_key]
                    # give the list without the last value
                    if final_value is None:
                        yield values
                    else:
                        final_value = self.value_encoder(final_value)
                        dir_path = dir_path / (final_key + '=' + final_value + suffix)
                        if dir_path.exists():
                            yield values + [final_value]
                else:   # otherwise, iterate over what's in the warehouse
                    key_label = final_key + '='
                    if dir_path.is_dir():
                        for level in dir_path.iterdir():
                            if level.name.startswith(key_label) and level.name.endswith(suffix):
                                suffix_stop = None if len(suffix) == 0 else -len(suffix)
                                value = level.name[len(key_label):suffix_stop]
                                yield values + [value]
            else:
                assert False, 'not let implemented'

    def _make_dir_file_name(self, filename_or_suffix, positional_args, keyvalue_args, value_encoder):
        # convert the positional arguments into key/value arguments
        for key, value in zip(self.partition_keys, positional_args):
            assert key not in keyvalue_args, \
                'postional partition arguments overlap with given key/value arguments'
            keyvalue_args[key] = value

        # if the last partition should be a file, don't include it
        if self.file_leaf:
            parts = self.partition_keys[:-1]
        else:
            parts = self.partition_keys

        # make the parts
        path_parts = (key + '=' + value_encoder(keyvalue_args[key]) for key in parts)
        directory = self.root_directory / pathlib.Path(*path_parts)

        # if the last partation should be the file
        if self.file_leaf:
            # form it
            final_key = self.partition_keys[-1]
            final_value = keyvalue_args[final_key]
            filename = final_key + '=' + value_encoder(final_value) + filename_or_suffix
        else:
            filename = filename_or_suffix

        return directory, filename
