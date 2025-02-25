# Config Loki

## Logueo a Loki a través de Kafka usando Alloy y Opentelemetry

- loki
- alloy
- grafana
- kafka
- opentelemetry

---

<ins> Deploy stack loki-grafana-alloy:</ins>

`docker compose -f loki-fundamentals/docker-compose.yml up -d`

Alloy http://localhost:12345

Grafana http://localhost:3000


---
<ins>Greenhouse app:</ins>

`docker compose -f loki-fundamentals/greenhouse/docker-compose-micro.yml up -d --build`


Carnivorous Greenhouse http://localhost:5005/login

Explorer Grafana: http://localhost:3000/a/grafana-lokiexplore-app/explore

---
<ins>Fuente</ins>

https://grafana.com/docs/loki/latest/send-data/alloy/examples/alloy-kafka-logs/?pg=blog&plcmt=body-txt
