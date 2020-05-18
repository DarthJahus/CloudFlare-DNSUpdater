# CloudFlare DNS Updater

This simple script will retrieve the IP of your server and update it on **CloudFlare**.

It can be used as a service that launches at startup, which would correctly set your IP every time it changes.

The script can come handy if you are using **Google Cloud** with a scheduled start and stop or any other provider with a dynamic IP address.

## Configuration

An example `config.json` file has been provided. You'll need your project ID and a CloudFlare API Token with `Zone.Zone` and `Zone.DNS` permissions.
