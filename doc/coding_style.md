# Coding style guidelines (for CodingGameServer)

### code in Python
For the server, we follow PEP8 coding style, except for the following rules:
- W191 (indentations contain tabs)
- E303 (too many blank lines)
- E101 (indentation contains mixed spaces and tabs): just because some lines are split and indented with spaces (tabs do not work)
- E501 (line too long): we avoid them, but sometimes it is usefull (long comments, or long url in comments)
- N802 (function name should be lowercase)
- N803 (argument name should be lowercase)
- N806 (variable in function should be lowercase)


### ToDo List
We use the following convention/patterns for the todo list:
- "TODO:" general ToDo task (a question like "should we do this?")
- "FIXME:" something do not fully work, to fix
- "REVIEW" someone need to review this
- "NOTIMPLEMENTED" for a function/method/code not yet implemented (but should be)
these pattern may be preceded by ! or !! to indicate the priority ("!!FIXME" indicates high priority bug to fix)

