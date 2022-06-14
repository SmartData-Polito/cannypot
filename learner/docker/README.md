# Readme for Docker

Tested on version: `Docker version 20.10.7, build 20.10.7-0ubuntu5~20.04.2`.

## Build docker image

From the `cannypot/learner` directory, you can build the image with: 
 
 ```
 sudo docker build . -t cannypot_image
 ```

Options:
- Add `--no-cache` if something doesn't work when you are trying to rebuild it
- Add `-t` to assign a custom tag to the image
- Add `--network host` if you want to use the host network
- Add `--build-arg` if you need to specify extra arguments

## Run docker image

To run the image on port 22 (if it is not already in use by ssh): 
```
sudo docker run -dti --name cannypot_container -p 22:2222 cannypot_image
```

## Data Persistency: Volumes

If you want to persist logs and config information, you need to use volumes. To do so, you need to save config information **before** running the image with volumes.

After the image is running, retrieve the container name with the command: 

```
sudo docker ps 
```

Then, copy the content of the logs and config directories into the your filesystem (e.g., `/data/cannypot/`): 

```
sudo docker cp cannypot_container:/opt/learner/cowrie/etc /data/cannypot/ 
sudo docker cp cannypot_container:/opt/learner/cowrie/var /data/cannypot/ 
sudo chown -R 1500:1500 /data/cannypot/etc/ /data/cannypot/var/
```

This will copy `var` and `etc` directories inside `/data/cannypot/` directory, so that they can be used as volumes later. Note that uuid 1500 is the user cowrie specified inside the Dockerfile.

Now, you can stop the container and re-run it specifying the volumes (use port 2222 instead of 22 if it is already in use by ssh): 

```
sudo docker run -dti --memory="500m" -p 22:2222 -v /data/cannypot/var:/opt/learner/cowrie/var -v /data/cannypot/etc:/opt/learner/cowrie/etc cannypot_image
```

**Warning**: if you use volumes before copying the directories as specified before, the run operation overrides the whole content of `etc` and `var` folders, making you lose the configuration information. 


