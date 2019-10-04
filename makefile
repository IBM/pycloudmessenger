.PHONY: all test creds depend basic castor ffl

all: test

creds:
	ifeq ($(creds), )
		$(error 'creds' variable is not set)
	endif

depend:
	@command -v python3 >/dev/null 2>&1 || { echo >&2 "Error - package python3 required, but not available."; exit 1; }

basic: depend creds
	@test -f $(cert) && python3 -m examples.basic.basic_client --credentials=$(creds) --feed_queue='feed queue' --reply_queue='reply queue' || echo "No certificate"

castor: depend
	@test -f $(creds) && python3 -m examples.castor.sample_client --credentials=$(creds) || echo "No certificate"

ffl: depend
	@test -f $(creds) && python3 -m examples.ffl.sample --credentials=$(creds) || echo "No certificate"

test:
	python3 -m pytest tests/ffl/ffl.py -srx -s
