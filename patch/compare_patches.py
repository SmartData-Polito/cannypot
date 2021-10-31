from pypatchin import compare
import config

if __name__ == "__main__":
    config_values = config.Config()

    print(compare.compare_latest_vs_generated_list_of_files(config_values.all_files_to_patch, config_values.latest_dir_name, config_values.patched_file_dir_name))
