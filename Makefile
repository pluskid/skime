default: test

test: skime
	nosetests tests

skime/iset.py: skime/iset.yml skime/iset_gen.py
	(cd skime && python iset_gen.py)

skime/insns.py: skime/iset.yml skime/iset_gen.py
	(cd skime && python iset_gen.py)

skime: skime/iset.py skime/insns.py