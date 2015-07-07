# vagrant

`vagrant` is a service that is used to build [vagrant](http://vagrantup.com) image that contains preinstalled
Armada platform.
Using this image is a recommended way to learn Armada. It is also a convenient base for vagrant images
for your own microservices.

This image should normally be available at the address `http://vagrant.armada.sh/armada.box` and
usually there is no need to build it from scratch. But if you want to alter the way it is built,
you can do it using this service.


# Building the service.

`vagrant` needs its configuration at the time of the build so it has to be put inside the container.
It should be put into the directory `./config/`.
The main configuration file is called [build-server.json](config/build-server.json) and consists
of a json object like the one below.

    {
        "host": "vbox.initech.com",
        "port": 22,
        "user": "service",
        "ssh_key": "service@vbox.initech.com.key",
        "http_proxy": "http://w3cache.initech.com:8080"
    }

First 4 fields are required and they should provide ssh credentials to a Linux machine
with [VirtualBox](https://www.virtualbox.org/) and [vagrant](http://vagrantup.com) installed.
That machine will be used to create `armada.box` image.

Creating an image may involve downloading of large amount of data from the internet (system update, new packages etc.).
In case you want to use some local HTTP proxy to speed things up, you can supply its address as key `http_proxy`.

Once you have proper configuration set, you can build the service with command:

    armada build vagrant



# Using the service.

After the service has been built it contains proper Armada image in the container. To access it run:

    armada run vagrant

The image can be accessed using endpoint `/armada.box`.


## Vagrantfile for your services.

Another endpoint provided by the service is [/ArmadaVagrantfile.rb](src/static/ArmadaVagrantfile.rb).
It returns Ruby script that provides single function `armada_vagrantfile()`. Running this function from the
`Vagrantfile` script for your armadized service takes care of setting up convenient development environment for it.

Example `Vagrantfile` for service `badguys-finder`:

    require 'open-uri'
    armada_vagrantfile_path = File.join(Dir.tmpdir, 'ArmadaVagrantfile.rb')
    IO.write(armada_vagrantfile_path, open('http://vagrant.armada.sh/ArmadaVagrantfile.rb').read)
    load armada_vagrantfile_path

    armada_vagrantfile(
        :microservice_name => 'badguys-finder',
        :origin_dockyard_address => 'dockyard.initech.com'
    )

Available parameters:

* `:microservice_name`.
    To take advantage of most Armada goodies, your service source code should reside in directory
    `/opt/:microservice_name/` inside the container. If you pass it to `armada_vagrantfile()` function,
    it will map files from your hard drive directly into VirtualBox virtual machine.
    It will also set environment variable `MICROSERVICE_NAME` which in turn will supply this name as default
    to `armada` commands. That way you can just type `armada run`, `armada ssh` etc. without typing service name everytime.

* `:origin_dockyard_address`.
    Address of the dockyard from which your service image will be downloaded.


For more options and list of their advantages, take a look into Armada guides in the section about
microservice's development environment.
