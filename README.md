# StackOverFix

### Current Workflow Idea:

1. User writes python code with a python library and gets some exception
2. Exception is caught and passed through stackoverfix package which attaches the error stack trace to the user's clipboard
3. In the designated prompt areas, user pastes the stack trace in a textbox
4. User attaches the snippet area of interest as well separately in a textbox
5. First API call is to generate an appropriate search phrase to find the corresponding error in the documentation through faiss
6. Retrieve top 3 results from vector store
7. Second API call to take in the additional information from the vector store ONLY if it is useful, else to inform that vector store was not useful and correct the code on its own

---
