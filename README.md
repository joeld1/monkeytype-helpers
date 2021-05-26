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
2) Use the recently generated/corrected types/signature to create patches to apply in order to reformat docstrs for methods


Walkthrough of Setup
---

#### Will be updated with text later

![image text](./imgs/001-desiredtools.png)
![image text](./imgs/002-tool-monkeytype_run.png)
![image text](./imgs/003-tool-monkeytype_stub.png)
![image text](./imgs/004-tool-monkeytype_apply.png)
![image text](./imgs/005-tool-monkeytype_apply_ignore_existing_annotations.png)
![image text](./imgs/006-tool-monkeytype_stub_diff.png)
![image text](./imgs/007-tool-monkeytype_stub_omit_existing_annotations.png)
![image text](./imgs/008-tool-generatepymentpatch-reSTtoreST.png)
![image text](./imgs/009-runmonkeytype_run.png)
![image text](./imgs/010-runmonkeytype_run-outputsqlitedb.png)
![image text](./imgs/011-runmonkeytype_run-outputsqlitedb-recordsadded.png)
![image text](./imgs/012-runmonkeytype_apply_ignore_existing_annotations-pt1.png)
![image text](./imgs/013-runmonkeytype_apply_ignore_existing_annotations-pt2.png)
![image text](./imgs/014-runmonkeytype_apply_ignore_existing_annotations-correctedannotations.png)
![image text](./imgs/015-rungeneratepymentpatchoncorrectedoutput-reSTtoreST.png)
![image text](./imgs/016-rungeneratepymentpatchoncorrectedoutput-reSTtoreST-result.png)
![image text](./imgs/017-applypymentpatch-window.png)
![image text](./imgs/018-applypymentpatch-diff.png)
![image text](./imgs/019-applypymentpatch-afterapplyingpatch.png)
