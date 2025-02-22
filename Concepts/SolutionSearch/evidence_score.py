import openai

def check_relevance_with_llm(error, retrieved_solutions):
    """Use an LLM to score evidence relevance before ranking."""
    prompt = f"Error: {error['message']}\n\nStack Trace:\n{error['code_snippet']}\n\nSolutions:\n" + "\n\n".join(
        [f"{i+1}. {sol['title']} - {sol['body'][:300]}" for i, sol in enumerate(retrieved_solutions)]
    ) + "\n\nRate each solution from 1 to 5 (1 = not relevant, 5 = highly relevant)."

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )

    scores = response["choices"][0]["message"]["content"]
    return scores
