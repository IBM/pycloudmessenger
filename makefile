.PHONY: all test creds depend basic castor ffl configure test
  
all: test

creds:
	ifeq ($(creds), )
		$(error 'creds' variable is not set)
	endif

depend:
	@command -v jq >/dev/null 2>&1 || { echo >&2 "Error - package jq required, but not available."; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo >&2 "Error - package python3 required, but not available."; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo >&2 "Error - package docker required, but not available."; exit 1; }

basic: depend
	@test -f $(creds) && python3 -m examples.basic.basic_client --credentials=$(creds) || echo "No certificate"

castor: depend
	@test -f $(creds) && python3 -m examples.castor.sample_client --credentials=$(creds) || echo "No certificate"

rest:
	@test -f $(creds) && python3 -m examples.castor.sample_rest --credentials=$(creds) || echo "No certificate"
	#@test -f $(creds) && python3 -m examples.castor.sample_rest --credentials=$(creds) --proxies=$(proxies) || echo "No certificate"

ffl: depend
	@test -f $(creds) && python3 -m examples.ffl.sample --credentials=$(creds) || echo "No certificate"

configure: depend
	./rabbit.sh

clean:
	-docker rm -f $(shell docker ps -a | grep rabbit_mq | cut -d' ' -f1)

test: configure
	python3 -m pytest tests/basic/test_basic.py -srx -s --credentials=$(creds)
