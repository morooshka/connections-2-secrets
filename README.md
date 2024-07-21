# connections-2-secrets
Helps to export Apache Airflow connections from source setup to a target k8s-based deployment.  
Converts connections export file, produced by airflow CLI tool to the secrets manifest for 
[Official Airflow Helm Chart](https://airflow.apache.org/docs/helm-chart/stable/index.html) 
based k8s deployment  

Connections settings are described [here](https://airflow.apache.org/docs/helm-chart/stable/adding-connections-and-variables.html#connections-and-sensitive-environment-variables)

Produces a `secret.yaml` manifest for applying with kubectl 
and a `values.yaml` data to append to Helm Chart's `.Values.secret` section 
before updating

### How to use
Follow the steps:

1. Export connections from a source setup via airflow CLI tool:

    ~~~commandline
    airflow connections export --file-format=yaml connections.yaml
    
    ~~~

2. Copy the exported data file `connections.yaml` via scp to your laptop
3. Execute the script to convert data, setting required namespace and an exported file path:

    ~~~commandline
    connections2secrets.py --namespace=my-airflow --source=./connections.yaml
    
    ~~~

4. Apply the generated `secret.yaml` manifest via `kubectl`

    ~~~commandline
    kubectl apply -f secret.yaml
    
    ~~~

5. Append the `.Values.secret` section of your values file with the data from generated `values.yaml`
6. Update the helm chart deployment as described [here](https://airflow.apache.org/docs/helm-chart/stable/quick-start.html)
