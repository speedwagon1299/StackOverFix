import openai

def generate_final_answer(error, top_solutions):
    """Use an LLM to generate a debugging solution using retrieved SO answers."""
    prompt = f"Error: {error['message']}\n\nStack Trace:\n{error['code_snippet']}\n\nSolutions:\n" + "\n\n".join(
        [f"- {sol['title']} - {sol['body'][:300]}" for sol in top_solutions]
    ) + "\n\nGenerate a well-structured debugging solution with citations."

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]
