__author__ = "qiao"

"""
generate the search keywords for each patient
"""

import json
from TrialGPT.api.generate_client import generate_client
import sys
from pathlib import Path

client = generate_client()


def get_keyword_generation_messages(note):
	system = 'You are a helpful assistant and your task is to help search relevant clinical trials for a given patient description. Please first summarize the main medical problems of the patient. Then generate up to 32 key conditions for searching relevant clinical trials for this patient. The key condition list should be ranked by priority. Please output only a JSON dict formatted as Dict{{"summary": Str(summary), "conditions": List[Str(condition)]}}.'

	prompt =  f"Here is the patient description: \n{note}\n\nJSON output:"

	print("PROMPT:", prompt)

	messages = [
		{"role": "system", "content": system},
		{"role": "user", "content": prompt}
	]
	
	return messages


if __name__ == "__main__":
	# the corpus: trec_2021, trec_2022, sigir, or synthea
	corpus = sys.argv[1]

	# the model index to use
	model = sys.argv[2]

	outputs = {}
	
	queries_path = (
    Path(__file__).resolve().parents[1]
    / "dataset"
    / corpus
    / "queries.jsonl"
)

	with open(str(queries_path), "r") as f:
		note = "";
		if corpus == "synthea":
				data = json.load(f)
				for entry in data:
					note = json.dumps(entry, indent=2)
					messages = get_keyword_generation_messages(note)
					messages = get_keyword_generation_messages(note)

					response = client.chat.completions.create(
						model=model,
						messages=messages,
						#temperature=0,
					)

					output = response.choices[0].message.content
					output = output.strip("`").strip("json")
					
					outputs[entry["_id"]] = json.loads(output)

					results_path = Path(__file__).resolve().parents[1] / "results"

					with open(str(results_path / f"retrieval_keywords_{model}_{corpus}.json"), "w") as f:
						json.dump(outputs, f, indent=4)
		else:
			for line in f.readlines():
				entry = json.loads(line)
				note = entry["text"]
				messages = get_keyword_generation_messages(note)

				response = client.chat.completions.create(
					model=model,
					messages=messages,
					#temperature=0,
				)

				output = response.choices[0].message.content
				output = output.strip("`").strip("json")
				
				outputs[entry["_id"]] = json.loads(output)

				results_path = Path(__file__).resolve().parents[1] / "results"

				with open(str(results_path / f"retrieval_keywords_{model}_{corpus}.json"), "w") as f:
					json.dump(outputs, f, indent=4)
