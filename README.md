# Namesilo DynDns Service

This tool acts as DynDns Service using [Namesilo API](https://github.com/dhoessl/python_namesilo_api).

# Config
Configuration is done using a yaml config file. <br>
The file should be located at `/etc/namesilo_dyndns/config.yaml` or at `~/.config/namesilo_dyndns.yaml`.

If the file is not found a `FileNotFoundError` is raised.

Example config can be found in the example folder.

# Install
```
pip install -r https://raw.githubusercontent.com/dhoessl/namesilo_dyndns/refs/heads/master/requirements.txt
pip install -U git+https://github.com/dhoessl/namesilo_dyndns
```

If the active user is not root you need to create the logfile and change owner to the running user.

```
sudo touch /var/log/dyndns.log
sudo chown $USER:root /var/log/dyndns.log
```

# Usage

`python3 -m namesilo_dyndns`

This command can be shot using cron or a systemd timer.

# Customize

If you want to set another ipv4_server or ipv6_server you need to change `get_my_ip` function or use a service which outputs the ip address as json format like this:
```
{"ip": "8.8.8.8"}
```

To customize this function:
```
import NamesiloDyndns from namesilo_dyndns

app = NamesiloDyndns()

@app.get_my_ip
def get_my_ip_custom(server):
    # request and return ip here

if __name__ == "__main__":
    app.run()
```
