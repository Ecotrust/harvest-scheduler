# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  config.vm.forward_port 80, 8080

  if File.directory?("../cost_model")
    config.vm.share_folder "v-cost-model", "/usr/local/apps/cost_model", "../cost_model"
  end

  if File.directory?("../harvest-scheduler")
    config.vm.share_folder "v-harvest-scheduler", "/usr/local/apps/harvest-scheduler", "../harvest-scheduler"
  end
  
  config.vm.provision :shell, :inline => "sudo apt-get update && sudo apt-get -y install python-pip build-essential python-dev python-numpy"
end
