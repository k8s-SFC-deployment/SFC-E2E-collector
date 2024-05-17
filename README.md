# SFC E2E Collector

<div align="center">

  ![thumbnail](/assets/images/collector.png)

</div>

collect `e2e_latency_total` and `e2e_count_total` for each SFC path.

## Run

```bash
$ docker build -t sfc-e2e-collector .
$ docker run -it --rm -v $(pwd):/app --cpus 1 -p 5000:5000 sfc-e2e-collector
```
