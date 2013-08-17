# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "precise64"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"

  config.vm.forward_port 80, 8080
  config.vm.forward_port 443, 8443
  config.vm.forward_port 8000, 8000
  config.vm.forward_port 5432, 5433

  if File.directory?("../cost_model")
    config.vm.share_folder "v-cost-model", "/usr/local/apps/cost_model", "../cost_model"
  end

  if File.directory?("../harvest-scheduler")
    config.vm.share_folder "v-harvest-scheduler", "/usr/local/apps/harvest-scheduler", "../harvest-scheduler"
  end
  
  Vagrant::Config.run do |config|
    config.vm.provision :shell, :inline => "sudo apt-get -y install python-pip  build-essential python-dev && sudo pip install python-numpy"
  end
end
