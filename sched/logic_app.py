from azure.mgmt.logic.models import Workflow, WorkflowParameter
import azure.mgmt.logic.logic_management_client as logic_client
from azure.common.credentials import  ServicePrincipalCredentials
import json

resource_group_name = 'bleikbaimm'
workflow_name = 'test79'
subscription_id = 'edf507a2-6235-46c5-b560-fd463ba2e771'
location = 'eastus'
logic_app_json_file = 'C:/Users/bleik/OneDrive - Microsoft/projects/batchai_manymodels/baimmscheduler/v2/logic_app.json'
sp_tenant_id = '72f988bf-86f1-41af-91ab-2d7cd011db47'
sp_client = '095d4aa7-a8d5-4f24-aa96-c631e3dee97c'
sp_key = 'a9b478dc-dbdb-403f-bd6d-1dee6c0b1bd4'

credentials = ServicePrincipalCredentials(client_id=sp_client,
    secret=sp_key,
    tenant=sp_tenant_id)

logic_app_json = json.load(open(logic_app_json_file))

con_param = WorkflowParameter.from_dict(logic_app_json['$connections'])

wf = Workflow(location=location,
              definition=logic_app_json['definition'],
              parameters={'$connections': con_param})

lc = logic_client.LogicManagementClient(credentials, subscription_id)

lc.workflows.create_or_update(resource_group_name,
    workflow_name,
    wf)
