# StackOverFix

### Current Workflow Idea:

1. User writes python code with a python library and gets some exception
2. Exception is caught and passed through stackoverfix package which attaches the error stack trace to the user's clipboard
3. In the designated prompgitt areas, user pastes the stack trace in a textbox
4. User attaches the snippet area of interest as well separately in a textbox
5. First API call is to evaluate whether documentation is required or not to generate an appropriate search phrase to find the corresponding error in the documentation through faiss. If required, then phrase is provided, else FALSE is returned. If FALSE, send information to Gemini api and retrieve generated text solving the error
6. If phrase is provided, search the vector store and retrieve top 2 results
7. Second API call to take in the additional information from the vector store ONLY if it is useful, else to inform that vector store was not useful and correct the code on its own

---
