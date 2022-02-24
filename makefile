.PHONY: all test creds depend basic castor ffl configure test
  
all: test

opts=--log-cli-level=DEBUG
opts=--log-cli-level=INFO

credentials:
	test -f "$(creds)"

depend:
	@command -v jq >/dev/null 2>&1 || { echo >&2 "Error - package jq required, but not available."; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo >&2 "Error - package python3 required, but not available."; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo >&2 "Error - package docker required, but not available."; exit 1; }

basic: credentials depend
	python3 -m examples.basic.basic_client --credentials=$(creds)

castor: credentials depend
	python3 -m examples.castor.sample_client --credentials=$(creds)

rest: credentials
	python3 -m examples.castor.sample_rest --credentials=$(creds)

ffl: credentials depend
	python3 -m examples.ffl.sample --credentials=$(creds)

configure: depend
	./rabbit.sh

clean:
	-docker rm -f $(shell docker ps -a | grep rabbit_mq | cut -d' ' -f1)

test: credentials configure
	#python3 -m pytest tests/ffl/ffl.py -srx -s --credentials=$(creds) $(opts)
	python3 -m pytest tests/basic/test_basic.py --credentials=$(creds) $(opts)

train: credentials depend
	python3 -m pytest tests/train.py --credentials=$(creds) $(opts)
