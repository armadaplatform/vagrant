# -*- mode: ruby -*-
# vi: set ft=ruby :

$SERVICE_NAME = "vagrant"
$DOCKYARD_ADDRESS = "dockyard.armada.sh"

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    # Every Vagrant virtual environment requires a box to build off of.
    config.vm.box = "armada"
    config.vm.box_url = "http://vagrant.armada.sh/armada.box"

    config.vm.provision "shell", inline: "sudo -u vagrant echo export MICROSERVICE_NAME='#{$SERVICE_NAME}' >> /home/vagrant/.bashrc"

    #--- Sciagniecie obrazu uslugi.
    config.vm.provision "shell", inline: "docker pull #{$DOCKYARD_ADDRESS}/#{$SERVICE_NAME}:latest | true"
    config.vm.provision "shell", inline: "docker tag #{$DOCKYARD_ADDRESS}/#{$SERVICE_NAME} #{$SERVICE_NAME} | true"


    #--- Forwarding portow.
    config.vm.network "public_network", :adapter => 2


    #--- Podmapowanie katalogow.
    config.vm.synced_folder "..", "/projects"
    config.vm.synced_folder "./", "/opt/#{$SERVICE_NAME}"

    #--- Uruchomienie Armady.
    $armada_start_script = <<SCRIPT
        docker rm -f `docker ps | grep armada | cut -f 1 -d ' '`
        sudo service armada start
        armada dockyard set origin #{$DOCKYARD_ADDRESS}
SCRIPT
    config.vm.provision "shell", inline: $armada_start_script
end
