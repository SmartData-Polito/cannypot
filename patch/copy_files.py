import config
from distutils.dir_util import copy_tree
from shutil import copyfile

if __name__ == "__main__":

    config_values = config.Config()

    # should copy from to_copy_dir_name to patched_file_dir_name

    for d in config_values.all_dir_to_copy:
        copy_tree(config_values.to_copy_dir_name + d, config_values.patched_file_dir_name + d)

    for f in config_values.all_files_to_copy:
        copyfile(config_values.to_copy_dir_name + f, config_values.patched_file_dir_name + f)
