PY=../.venv/bin/python
.PHONY: data features eval latency deck samples demo all
data:        ## generate the extra generator families and merge the manifest
	scripts/run_generation.sh
features:    ## cache frozen XLS-R embeddings for every clip, codec and prefix
	$(PY) eval/build_features.py --prefixes 0.5,1,1.5,2,2.5,3,3.5,4
eval:        ## every number in results.json, then the shipped model
	$(PY) eval/experiments.py
latency:     ## forward latency and capacity on this machine
	$(PY) eval/latency.py
samples:     ## bundle the demo samples with their true origins
	$(PY) scripts/make_samples.py
deck:        ## the six-slide SIH deck from results.json
	$(PY) scripts/build_deck.py
demo:        ## operator console on http://127.0.0.1:8770, offline
	scripts/demo.sh
all: features eval latency samples deck
