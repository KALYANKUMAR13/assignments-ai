CHART_NAME   := inference-service
RELEASE_NAME := inference-app
NAMESPACE    := default
CHART_DIR    := ./inference-app
VALUES_FILE  := ./inference-app/values.yaml

.PHONY: all load deploy forward clean

## Load image + deploy helm chart
all: load deploy

load:
	docker save $(CHART_NAME):latest -o /tmp/$(CHART_NAME).tar
	minikube image load /tmp/$(CHART_NAME).tar

deploy:
	helm upgrade --install $(RELEASE_NAME) $(CHART_DIR) \
		--namespace $(NAMESPACE) \
		--create-namespace \
		--values $(VALUES_FILE) \
		--wait

forward:
	kubectl port-forward svc/$(RELEASE_NAME) 8080:8080 -n $(NAMESPACE)

clean:
	helm uninstall $(RELEASE_NAME) -n $(NAMESPACE) || true