import langextract as lx
import textwrap

prompt = textwrap.dedent("""
    Extract characters, emotion and relationships from the following text:
    do not paraphrase or overlap entities. provide meaningful attributes for each entity to add context.
    """)

examples = [
    lx.data.ExampleData(
        text="Romeo. But soft! what light through yonder window breaks? It is the east, and Juliet is the sun.",
        extractions=[
            lx.data.Extraction(
                extraction_class="Character",
                extraction_text="Romeo",
                attributes={"emotional_state": "wonder"}
            ),
            lx.data.Extraction(
                extraction_class="Emotion",
                extraction_text="But soft!",
                attributes={"feelings": "gentle awe"}
            ),
            lx.data.Extraction(
                extraction_class="Relationship",
                extraction_text="Juliet is the sun",
                attributes={"type": "metaphor"}
            ),
        ]
    )
]

input_text = "Lady Juliet gazed longingly at the stars, her heart aching for Romeo"

result = lx.extract(
    prompt_description=prompt,
    text_or_documents=input_text,
    examples=examples,
    model_id="gemini-2.5-flash",
)

jsonl_path = "test_output/extration_result.jsonl"
html_path = "test_output/visualization.html"

lx.io.save_annotated_documents([result], output_name=jsonl_path)
print(f"Extraction result saved to: {jsonl_path}")

html_content = lx.visualize([jsonl_path])

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"Visualization saved to: {html_path}")