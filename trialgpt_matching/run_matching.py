__author__ = "qiao"

"""
Running the TrialGPT matching for three cohorts (sigir, TREC 2021, TREC 2022).
"""

import json
from nltk.tokenize import sent_tokenize
import os
import sys
from pathlib import Path

from TrialGPT.trialgpt_matching.TrialGPT_matching import trialgpt_matching

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
	corpus = sys.argv[1]
	model = sys.argv[2] 
	
	dataset = json.load(open(PROJECT_ROOT / "dataset" / corpus / "retrieved_trials.json"))

	output_path = PROJECT_ROOT / "results" / f"matching_results_{corpus}_{model}.json" 

	# Dict{Str(patient_id): Dict{Str(label): Dict{Str(trial_id): Str(output)}}}
	if output_path.exists():
		output = json.load(open(str(output_path)))
	else:
		output = {}

	for instance in dataset:
		# Dict{'patient': Str(patient), '0': Str(NCTID), ...}
		patient_id = instance["patient_id"]
		patient = instance["patient"]
		sents = sent_tokenize(patient)
		sents.append("The patient will provide informed consent, and will comply with the trial protocol without any practical issues.")
		sents = [f"{idx}. {sent}" for idx, sent in enumerate(sents)]
		patient = "\n".join(sents)

		# initialize the patient id in the output 
		if patient_id not in output:
			output[patient_id] = {"0": {}, "1": {}, "2": {}}
		
		for label in ["2", "1", "0"]:
			if label not in instance: continue

			for trial in instance[label]: 
				trial_id = trial["NCTID"]

				# already calculated and cached
				if trial_id in output[patient_id][label]:
					continue
				
				# in case anything goes wrong (e.g., API calling errors)
				try:
					results = trialgpt_matching(trial, patient, model)
					output[patient_id][label][trial_id] = results

					with open(str(output_path), "w") as f:
						json.dump(output, f, indent=4)

				except Exception as e:
					print(e)
					continue
