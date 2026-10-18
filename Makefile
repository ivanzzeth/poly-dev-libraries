.PHONY: catalog check check-checkouts

catalog:
	python3 scripts/catalog.py generate

check:
	python3 scripts/catalog.py check

check-checkouts:
	python3 scripts/catalog.py check --checkouts
