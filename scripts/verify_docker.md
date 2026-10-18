The optional Compose file retains the official FalkorDB image's entrypoint and
module loading configuration. It was not executed in this workspace because
Docker is unavailable. The embedded FalkorDB path is the tested local setup.
The data volume does not by itself promise immediate persistence of every write;
configure the official server's persistence policy for a durable deployment.
