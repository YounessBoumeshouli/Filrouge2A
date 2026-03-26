from llama_parse import LlamaParse
import os
from dotenv import load_dotenv

pdf_path = r"../data/marrakech-places-rag.pdf"
md_output = r"../data/marrakech-places-rag.md"


load_dotenv()

parser = LlamaParse(
    api_key=os.environ.get("llamaParse_Key"),
    result_type="markdown",
    verbose=True,
    language="fr",
)

documents = parser.load_data(pdf_path)

with open(md_output, "w", encoding="utf-8") as f:
    for doc in documents:
        f.write(doc.text + "---")
