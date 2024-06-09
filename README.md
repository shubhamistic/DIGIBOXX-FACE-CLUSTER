<a name="readme-top"></a>

<div align="center">
  <h3 align="center">DIGIBOXX-FACE-CLUSTER</h3>
  Face Recognition System designed for the Digiboxx.com Hackathon
  <p align="center">
    <a href="https://github.com/shubhamistic/DIGIBOXX-FACE-CLUSTER"><strong>Explore the docs »</strong></a>
    <br />
    ·
    <a href="https://github.com/shubhamistic/DIGIBOXX-FACE-CLUSTER/issues">Report Bug</a>
    ·
    <a href="https://github.com/shubhamistic/DIGIBOXX-FACE-CLUSTER/issues">Request Feature</a>
    ·
  </p>
</div>

## SETUP (Ubuntu 22.04 LTS, 64 bit x86)

```bash
sudo apt update
```

- Install Python3.9:
  ```bash
  sudo add-apt-repository ppa:deadsnakes/ppa
  apt list | grep python3.10
  sudo apt install python3.9
  sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
  sudo update-alternatives --config python3
  sudo apt-get install python3.9-distutils
  ```

- DOWNLOAD dlib from [*here*](https://wheels.fermentrack.com/simple/dlib/dlib-19.24.0-cp39-cp39-linux_x86_64.whl):
- MOVE **dlib-19.24.0-cp39-cp39-linux_x86_64.whl** to DIGIBOXX-HACKATHON directory


- Install virtualenv:
  ```bash
  sudo apt install virtualenv
  ```

- Install the repository:
  ```bash
  git clone https://github.com/shubhamistic/DIGIBOXX-FACE-CLUSTER.git
  ```

- Activate virtualenv and install the modules (use byobu):
  ```bash
  virtualenv DIGIBOXX-FACE-CLUSTER
  cd DIGIBOXX-FACE-CLUSTER
  source bin/activate
  pip install cmake
  pip install dlib-19.24.0-cp39-cp39-linux_x86_64.whl
  pip install --no-cache-dir -r requirements.txt
  ```

- Run the daemon using:
  ```bash
  python run.py <server_url> <daemon_authentication_key>
  ```

## [LICENSE](LICENSE)


## About the Author
This repository is maintained by [shubhamistic](https://github.com/shubhamistic), a passionate programmer and web developer. Explore my projects and join me on my journey to create innovative solutions and push the boundaries of what's possible.


<p align="right">(<a href="#readme-top">back to top</a>)</p>
