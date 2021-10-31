from pypatchin import patch
import config

if __name__ == "__main__":

    config_values = config.Config()

    patch.compute_and_save_patches_for_list_of_files(config_values.all_files_to_patch, config_values.original_dir_name, config_values.latest_dir_name, config_values.patch_dir_name)
