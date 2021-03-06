MonkeyType Helpers
---

Description
---
This repo contains a few snippets that allow one to use apply MonkeyType onto modules within PyCharm by using the ExternalTools functionality within PyCharm.

Purpose
---
This was created in order to quickly be able to perform the following:
1) Infer and add types/annotations onto methods that are not typed properly
   - **Note**: I currently don't know how to use stubs to generate patches to apply, if someone knows, please do leave a comment, so I can apply it :)!
2) Use the recently generated/corrected method return types and signatures to create patches which contain also contain reformatted docstrings 

Notes
---
   - This external tool makes a backup in the same folder of the associated script/module/.py file being imported from the script the external tool is running on. 
      - I'm not sure how this external tool reacts to improperly formatted .py files, or folders where one does not have write permissions.
   - Pyment re-formats to `reST` docstrings, but you can change this and other Pyment settings in `monkeytype_run.py` to fit your needs.
   - Delete the patches found in the patches folder, and run the test `test_monkeytype_run.py` if you're interested in testing/stepping through the code.
      - You can also test the pycharm external tool by running it on the modules found in this repo.

Walkthrough of Setup
---
1) Clone repo
2) Install the following dependencies:
   - monkeytype
   - black
   - isort
   - [pyment](https://github.com/dadadel/pyment) (use the github version since the pypi version isn't updated)
   - pytest
3) Follow steps in images below

4) ### Create a PyCharm External Tool (*Might differ for PCs*)
   ![image text](./imgs/001_monkeytype_external_tool_arguments.png)
   -  *Note, you can hard-code to a specific interpreter, but make sure that that interpreter contains all dependencies found on the script you are running the external tool on*
   -  *In this example, the script path is hard-coded*
   ![image text](./imgs/002_external_tools_menu.png)

5) ### Right-Click and Run External Tool on Module of Interest
   ![image text](./imgs/003_select_run_and_create_associated_patches.png)

6) ### Select Project Directory the script is a part of (this will contain your monkeytype.sqlite3 db, and your script/package/module must be found somewhere (nested or not) in this folder)
   ![image text](./imgs/004_select_root_directory_that_will_contain_monkeytypesqlite3_and_contains_module.png)
   
   ![image text](./imgs/005_terminal_output.png)
   -  *Example output shown above*
   
   ![image text](./imgs/006_generated_patch.png)
   -  *Patch for import dependency shown in red on left panel above*

7) ### Right-Click on Patch, Select Apply Patch
   ![image text](./imgs/007_apply_patch_option.png)

8) ### Select File to Patch and Click on Show Difference
   ![image text](./imgs/008_apply_patch_window.png)

9) ### Merge Desired Changes =)
   ![image text](./imgs/009_show_diff.png)

