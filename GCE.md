# GCE Usage

## Docs:
- https://cloud.google.com/compute/docs/instances/stop-start-instance
- https://cloud.google.com/compute/docs/instances/connecting-to-instance

```bash
# start GCE from local computer
gcloud compute instances start --project "coms6111-268404" --zone "us-east1-d" "cs6111-instance"

# ssh to GCE from local computer
# da2897's compute engine
gcloud beta compute --project "coms6111-268404" ssh --zone "us-east1-d" "[username]@cs6111-instance"

# stop GCE from local computer (always stop after using) 
# da2897's compute engine
gcloud compute instances stop --project "coms6111-268404" --zone "us-east1-d" "cs6111-instance"
```