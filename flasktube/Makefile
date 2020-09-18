IMAGE_NAME = flasktube
VERSION = latest

build:
	docker build -t $(IMAGE_NAME):$(VERSION) .
run:
	docker run -p 5000:5000 --name flasktube --rm $(IMAGE_NAME):$(VERSION)
lint:
	docker run --rm -v $(PWD):/code eeacms/pylint
	