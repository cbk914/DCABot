run : .dcapid .pollpid
kill : dcakill pollkill

# run dcabot on pi
.dcapid:
	nohup python3 dcabot.py >/dev/null 2>&1 & echo $$! > $@

# kill dcabot on pi
dcakill : .dcapid
	kill -9 `cat $<` && rm $<

# restart dcabot on pi
dcarestart: dcakill .dcapid

# run dcapoll on pi
.pollpid :
	nohup python3 dcapoll.py >/dev/null 2>&1 & echo $$! > $@

# kill dcapoll on pi
pollkill: .pollpid
	kill -9 `cat $<` && rm $<

# restart dcapoll on pi
pollrestart: pollkill .pollpid

clean:
	rm -f log/*

dcarunning:
	ps -aux | grep dcabot.py

pollrunning:
	ps -aux | grep dcapoll.py

.PHONY: run kill clean cleandb
