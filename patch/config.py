class Config:
    def __init__(self):
        # PATCH
        self.patch_dir_name = "../learner/patches/"

        # ORIGINAL (Where patches should be computed)
        # You need to specify your own path (needed only if you need to recompute patches)
        self.original_dir_name = "../../cowrie-fee98d47d3042136951105297e62f919b39d7494/"

        # LATEST (Where patches should be computed)
        self.latest_dir_name = "../cowrie-learner/"

        # TO COPY DIR
        self.to_copy_dir_name = "../learner/"

        # NEW ORIGINAL (Where patches should apply to)
        self.target_dir_name = "../cowrie/"

        # GENERATED (Where new patched files should be saved)
        self.patched_file_dir_name = "../learnerUpdated/"

        # MULTIPLE FILES TO PATCH (DO NOT MODIFY THIS VARIABLE)
        self.all_files_to_patch = ["src/cowrie/ssh/factory.py",
                                   "src/cowrie/shell/avatar.py",
                                   "src/cowrie/shell/honeypot.py",
                                   "src/cowrie/shell/protocol.py",
                                   "src/twisted/plugins/cowrie_plugin.py",
                                   "src/cowrie/core/realm.py",
                                   "etc/cowrie.cfg.dist",
                                   "etc/.gitignore",
                                   "/var/lib/cowrie/tty/.gitignore",
                                   "README.rst",
                                   "docs/README.rst",
                                   "requirements.txt",
                                   ".gitignore"
                                   ]

        self.all_dir_to_copy = [   # (DO NOT MODIFY THIS VARIABLE)
            "src/cowrie/learning",  # entire directory
        ]

        self.all_files_to_copy = [  # (DO NOT MODIFY THIS VARIABLE)
            "etc/cowrie.cfg",
            "etc/userdb.txt",
            "bin/clear_status"
        ]
