# StackOverFix

### Details of Project

StackOverFix is an AI-powered debugging assistant designed to help developers resolve Python exceptions efficiently by combining intelligent clipboard automation, vector-based documentation search, and large language model reasoning.

✂️ Automatically captures the stack trace of any caught Python exception and copies it to the user's clipboard via the stackoverfix package.

📚 Supports semantic documentation search across popular Python libraries:

1. NumPy

2. Pandas

3. PyTorch

4. Scikit-Learn

5. TensorFlow Keras

6.  Core Python

🔍 Uses `nomic-ai/nomic-embed-text-v1` to generate embeddings for documentation content stored in a FAISS vector store.

🎯 Applies `nvidia/nv-rerankqa-mistral-4b-v3` to rerank the top 25 search results and select the top 2 most relevant documentation snippets.

🧠 Combines the selected context (if useful) with prompt-driven reasoning using `gemini-2.0-flash-lite` to generate clear and accurate code corrections or explanations.

### BackEnd Set up

1. Create a `.env` file in root directory with `GEMINI_API_KEY` and `NVIDIA_API_KEY`

2. Run the following commands

```bash
cd Concepts/APICall
pip install -r requirements.txt
```

3. To run the backend server, run

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### FrontEnd Set up

1. Run the following commands

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

2. Open the link `https://localhost:5173`

### Workflow:

1. User writes python code with a python library and gets some exception
2. Exception is caught and passed through stackoverfix package which attaches the error stack trace to the user's clipboard
3. In the designated prompt areas, user pastes the stack trace in a textbox
4. User attaches the snippet area of interest as well separately in a textbox along with an optional prompt.
5. First API call is to evaluate whether documentation is required or not to generate an appropriate search phrase to find the corresponding error in the documentation through faiss. If required, then phrase is provided, else FALSE is returned. If FALSE, send information to Gemini api and retrieve generated text solving the error
6. If phrase is provided, search the vector store and retrieve top 2 results
7. Second API call to take in the additional information from the vector store ONLY if it is useful, else to inform that vector store was not useful and correct the code on its own

---

## 📽️ Demo

Watch the demo video:  

https://github.com/user-attachments/assets/4f622442-28ff-49c9-9054-e11de1cd3d6e

