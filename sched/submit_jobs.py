import os
import json
import sys
from datetime import datetime
from azureml.core.compute import AmlCompute
from azureml.core.datastore import Datastore
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.pipeline.steps import PythonScriptStep
from azureml.core.runconfig import CondaDependencies, RunConfiguration
from azureml.core import Workspace, Run, Experiment
from azureml.core.authentication import ServicePrincipalAuthentication


config_file = sys.argv[1]
with open(config_file) as f:
    j = json.loads(f.read())

# Batch AI Run Config
conda_dependencies = CondaDependencies.create(
    pip_packages=j["pip_packages"], python_version=j["python_version"]
)
batchai_run_config = RunConfiguration(conda_dependencies=conda_dependencies)
batchai_run_config.environment.docker.enabled = True

# SP Authentication
sp_auth = ServicePrincipalAuthentication(
    tenant_id=j["sp_tenant"], username=j["sp_client"], password=j["sp_secret"]
)

# AML Workspace
aml_ws = Workspace.get(
    name=j["aml_work_space"],
    auth=sp_auth,
    subscription_id=str(j["subscription_id"]),
    resource_group=j["resource_group_name"],
)

# AML Compute Target
compute_target = AmlCompute(aml_ws, j["cluster_name"])

# Pipeline Input and Output
data_ds = Datastore.register_azure_blob_container(
    aml_ws,
    datastore_name="data_ds",
    container_name=j["data_blob_container"],
    account_name=j["blob_account"],
    account_key=j["blob_key"],
)
data_dir = DataReference(datastore=data_ds, data_reference_name="data")

models_ds = Datastore.register_azure_blob_container(
    aml_ws,
    datastore_name="models_ds",
    container_name=j["models_blob_container"],
    account_name=j["blob_account"],
    account_key=j["blob_key"],
)
models_dir = DataReference(datastore=models_ds, data_reference_name="models")

preds_ds = Datastore.register_azure_blob_container(
    aml_ws,
    datastore_name="preds_ds",
    container_name=j["preds_blob_container"],
    account_name=j["blob_account"],
    account_key=j["blob_key"],
)
preds_dir = PipelineData(name="preds", datastore=preds_ds, is_directory=True)

# Create a pipeline step for each (device, tag) pair
steps = []
for device_id in j["device_ids"]:
    for tag in j["tags"]:
        preds_dir = PipelineData(name="preds", datastore=preds_ds, is_directory=True)
        step = PythonScriptStep(
            name="{}_{}".format(device_id, tag),
            script_name=j["python_script_name"],
            arguments=[device_id, tag, models_dir, data_dir, j["data_blob"], preds_dir],
            inputs=[models_dir, data_dir],
            outputs=[preds_dir],
            source_directory=j["python_script_directory"],
            compute_target=compute_target,
            runconfig=batchai_run_config,
        )
        steps.append(step)


experiment_name = "exp_" + datetime.now().strftime("%y%m%d%H%M%S")

pipeline = Pipeline(workspace=aml_ws, steps=steps)
pipeline.validate()
pipeline_run = Experiment(aml_ws, experiment_name).submit(pipeline)


