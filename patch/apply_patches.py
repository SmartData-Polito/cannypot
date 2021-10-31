from pypatchin import patch
import config

if __name__ == "__main__":
    config_values = config.Config()

    patch.apply_all_patches_to_files(config_values.all_files_to_patch, config_values.patch_dir_name, config_values.target_dir_name, config_values.patched_file_dir_name)
