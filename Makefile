.PHONY: docker-build
docker-build:
	docker build -t podcast2pdf .

.PHONY: docker-run
docker-run:
	docker run -it -v ~/samples/:/app/samples/ --env FETCH_PAGE_NUM='2' podcast2pdf

.PHONY: all
all:
	make docker-build
	make docker-run