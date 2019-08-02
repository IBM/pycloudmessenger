.PHONY: all test

all: test

ifeq ($(creds), )
$(error 'creds' variable is not set)
endif

depend:
	@command -v python3 >/dev/null 2>&1 || { echo >&2 "Error - package python3 required, but not available."; exit 1; }

basic: depend
	@test -f $(cert) && python3 -m tests.basic.basic_client --credentials=$(creds) --feed_queue='feed queue' --reply_queue='reply queue' || echo "No certificate"

castor: depend
	@test -f $(creds) && python3 -m tests.castor.sample_client --credentials=$(creds) || echo "No certificate"
