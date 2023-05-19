# jupyterhub-ipyparallel
Setup and report for setting up Jupyterhub with ipyparallel. 


## Setup

There are two 'machines':

- 'Jötunn' where the controller will run and engines in mpi, and
- 'Jupyterhub' where it spawns user notebooks for users and the cluster will be started and communicated with through the client

Jötunn:

- runs as an ssh server
- has a user `demo` with password `whocares`
- has python packages `ipyparallel, mpi4py` 
- loads modules for openmpi or python has openmpi package

Jupyterhub:
- runs a notebook server that spawns notebooks
- has packages `ipyparallel, jupyter_server`
- has a user `<username>` with profile `jotunn`,
  configured to start the controller on `remote` via `ssh`,
  and engines on `remote` via `sshproxy` with `--engines=mpi`

On Jötunn:

* `module load python/3.6.1` 
* `pip3 install --user jotunn_python_requirements.txt` (for the demo) 
* Set the script: `launch-python-for-ipy-ssh` somewhere on the cluster, for example in the /opt/ folder or where you have python or other config files. This will load the required modules and tell python where it is. The `bash -l` creates a login shell so bashrc files, bash_profile, etc. will be sourced.
* Depending on where you put the script , change the path_to_remote_python_script in the ipcluster_config.py
* If the script name is changed, name of script in ipcluster_config.py needs to be changed. 
For our example we are telling our controller to run the machines with mpi_exec, and that is why we are loading that in the script.


The only issue here is that the python install on Jötunn could be better, it would need to be have all the things you need to do or one should be able to install it. 



On Jupyterhub:

* Create ssh keys for host jotunn.rhi.hi.is: 
If username is not the same, include `<username>@jotunn.rhi.hi.is`
```bash
ssh-keygen -f ~/.ssh/id_ecdsa -t ecdsa -b 521 -q -N ""
ssh-copy-id -i ~/.ssh/id_ecdsa jotunn.rhi.hi.is
```
You will be prompted to enter the password for your `<username> on jotunn.rhi.hi.is`, if it is different then on local Jupyterhub, add `<username>@jotunn.rhi.hi.is`
```bash
sigurdur14@jupyter:~$ ipython profile create --parallel jotunn
```

* Move the `ipcluster_config.py` from this repo to `~/.ipython/profile_jotunn/ipcluster_config.py`
the ipcluster_config.py might need to be configured for the remote python bash script and if the remote user directory and username differ from the local environment. But in Jupyterhub and Jötunn they are the same, both under `/home/<username>`

For most recent magics and MPI functionality:
Install most recent ipython and ipyparallel, notebook and jupyter server
Install widgetsnbextension and have this in notebook `!jupyter nbextension enable --py widgetsnbextension`, or terminal:`jupyter nbextension enable --py widgetsnbextension` `

#### Starting cluster:
Through the IPython clusters tab
Logs for starting on RU Jupyterhub are available for root with command `less +G /var/log/jupyterhub/rupyter.log`
but can also be started on terminal `ipcluster start -n 4 --profile jotunn`

## Connecting to Views
```python
# After a cluster is started use the Client to connect to the engines

import ipyparallel as ipp
cli = ipp.Client(profile='jotunn', sshserver='jotunn.rhi.hi.is')

```
If your Jupyterhub username is not the same as on Jötunn,
you need to add username to sshserver or you get a Timeout `cli = ipp.Client(profile='jotunn', sshserver='sigurdur14@jotunn.rhi.hi.is')`


## Current issues:

### Issue 1: (This is resolved by just using the Client(sshserver=...))
Using the cluster command in code 
```python
# Starting Cluster with 4 engines
rc = ipp.Cluster(n=4, profile="jotunn", timeout=20).start_and_connect_sync()
```
or 
```python
cluster = ipp.Cluster.from_file(profile="remotempi")
rc = cluster.connect_client_sync()
```
to connect and start usually results in a TimeoutError with the following error(not full output):
```
File ~/.conda/envs/ipytest/lib/python3.8/site-packages/ipyparallel/client/client.py:758, in Client._connect(self, sshserver, ssh_kwargs, timeout)
    756 evts = poller.poll(timeout * 1000)
    757 if not evts:
--> 758     raise TimeoutError("Hub connection request timed out")
    759 idents, msg = self.session.recv(self._query_socket, mode=0)
    760 if self.debug:

TimeoutError: Hub connection request timed out
```

### Issue 2 (with Jötunn)
Running sync_imports or apply_sync()
```python
bc = cli.broadcast_view()
with bc.sync_imports(): 
    import numpy
```
yields in the following error meaning there are some package inconsistencies on Jötunn that I was not able to resolve without inducing other package errors.
```
/home/sigurdur14/.local/lib/python3.6/site-packages/ipyparallel/serialize/codeutil.py in code_ctor(*args)
     20 
     21 def code_ctor(*args):
---> 22     return types.CodeType(*args)
     23 
     24 

TypeError: code() takes at most 15 arguments (16 given)
```
But importing numpy or running something else without sync_imports() works fine. But there is also inconsistency in python3.6 can't install the lastest numpy so setting up a parallel demo for that did not work as intended.

We can import numpy and other things for example in a %px direct view cell. 
%px in a cell is a shortcut to [`DirectView.execute()`](https://ipyparallel.readthedocs.io/en/latest/api/ipyparallel.html#ipyparallel.DirectView.execute "ipyparallel.DirectView.execute") and [`AsyncResult.display_outputs()`](https://ipyparallel.readthedocs.io/en/latest/api/ipyparallel.html#ipyparallel.AsyncResult.display_outputs "ipyparallel.AsyncResult.display_outputs") methods respectively.
See more [magic commands](https://ipyparallel.readthedocs.io/en/latest/tutorial/magics.html)


