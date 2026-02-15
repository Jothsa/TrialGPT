__author__ = "qiao"

"""
Using GPT to aggregate the scores by itself.
"""

from beir.datasets.data_loader import GenericDataLoader
import json
from nltk.tokenize import sent_tokenize
import os
import sys
import time
from pathlib import Path

from TrialGPT.trialgpt_ranking.TrialGPT_ranking import trialgpt_aggregation

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
	corpus = sys.argv[1] 
	model = sys.argv[2]

	# the path of the matching results
	matching_results_path = sys.argv[3]
	results = json.load(open(matching_results_path))

	# loading the trial2info dict
	trial2info = json.load(open(PROJECT_ROOT / "dataset" / "trial_info.json"))
	
	# loading the patient info
	_, queries, _ = GenericDataLoader(data_folder=str(PROJECT_ROOT / "dataset" / corpus / "")).load(split="test")
	
	# output file path
	output_path = PROJECT_ROOT / "results" / f"aggregation_results_{corpus}_{model}.json"

	if output_path.exists():
		output = json.load(open(str(output_path)))
	else:
		output = {}

	# patient-level
	for patient_id, info in results.items():
		# get the patient note
		patient = queries[patient_id]
		sents = sent_tokenize(patient)
		sents.append("The patient will provide informed consent, and will comply with the trial protocol without any practical issues.")
		sents = [f"{idx}. {sent}" for idx, sent in enumerate(sents)]
		patient = "\n".join(sents)

		if patient_id not in output:
			output[patient_id] = {}
		
		# label-level, 3 label / patient
		for label, trials in info.items():
				
			# trial-level
			for trial_id, trial_results in trials.items():
				# already cached results
				if trial_id in output[patient_id]:
					continue

				if type(trial_results) is not dict:
					output[patient_id][trial_id] = "matching result error"

					with open(str(output_path), "w") as f:
						json.dump(output, f, indent=4)

					continue

				# specific trial information
				trial_info = trial2info[trial_id]	

				try:
					result = trialgpt_aggregation(patient, trial_results, trial_info, model)
					output[patient_id][trial_id] = result 

					with open(str(output_path), "w") as f:
						json.dump(output, f, indent=4)

				except:
					continue
