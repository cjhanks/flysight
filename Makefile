VIRTUAL_ENV=${PWD}/venv
ARGS=

.ONESHELL:
initialize: fetch virtualenv dep run
	echo "Done."

.ONESHELL:
fetch:
	cd data
	./get.sh

.ONESHELL:
protocol:
	protoc message.proto --python_out flysight/

virtualenv:
	python3 -m venv ${VIRTUAL_ENV}

.ONESHELL:
dep:
	. ${VIRTUAL_ENV}/bin/activate
	pip3 install -r requirements.txt

.ONESHELL:
run:
	export PYTHONPATH=${PYTHONPATH}:$(PWD)
	. ${VIRTUAL_ENV}/bin/activate
	python3 flysight/run.py $(ARGS)
