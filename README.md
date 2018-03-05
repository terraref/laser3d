# PLY to LAS conversion extractor

This extractor converts PLY 3D point cloud files into LAS files.

_Input_

  - Evaluation is triggered whenever a file is added to a dataset
  - Checks whether there are 2 east/east .PLY files
  
_Output_

  - The dataset containing the .PLY file will get a corresponding .LAS file merging the two PLY files.
  
### Docker
The Dockerfile included in this directory can be used to launch this extractor in a container.

_Building the Docker image_
```
docker build -f Dockerfile -t terra-ext-ply2las .
```

_Running the image locally_
```
docker run \
  -p 5672 -p 9000 --add-host="localhost:{LOCAL_IP}" \
  -e RABBITMQ_URI=amqp://{RMQ_USER}:{RMQ_PASSWORD}@localhost:5672/%2f \
  -e RABBITMQ_EXCHANGE=clowder \
  -e REGISTRATION_ENDPOINTS=http://localhost:9000/clowder/api/extractors?key={SECRET_KEY} \
  terra-ext-ply2las
```
Note that by default RabbitMQ will not allow "guest:guest" access to non-local addresses, which includes Docker. You may need to create an additional local RabbitMQ user for testing.

_Running the image remotely_
```
docker run \
  -e RABBITMQ_URI=amqp://{RMQ_USER}:{RMQ_PASSWORD}@rabbitmq.ncsa.illinois.edu/clowder \
  -e RABBITMQ_EXCHANGE=terra \
  -e REGISTRATION_ENDPOINTS=http://terraref.ncsa.illinosi.edu/clowder//api/extractors?key={SECRET_KEY} \
  terra-ext-ply2las
```
