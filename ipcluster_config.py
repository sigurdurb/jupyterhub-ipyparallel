# Configuration file for ipcluster.
import os

path_to_remote_home = os.path.join("/home",os.path.expanduser("~").split('/')[-1])
path_to_remote_profile = os.path.join(path_to_remote_home,".ipython/profile_jotunn")
path_to_remote_python_script = path_to_remote_home


c = get_config()

c.Cluster.controller_launcher_class = "ssh"
# the host to ssh to
c.SSHControllerLauncher.hostname = "jotunn.rhi.hi.is"


# tell the controller to listen on all ips, so the client can connect to it
c.Cluster.controller_args = ["--ip=*", "--profile-dir="+path_to_remote_profile]


c.Cluster.engine_launcher_class = "sshproxy"
c.SSHProxyEngineSetLauncher.hostname = "jotunn.rhi.hi.is"
# Tell the engines to run with MPI
c.SSHProxyEngineSetLauncher.ipcluster_args = ["--engines", "mpi"]

c.SSHLauncher.remote_profile_dir = path_to_remote_profile
c.SSHLauncher.remote_python = os.path.join(path_to_remote_python_script,"launch-python-for-ipy-ssh")
