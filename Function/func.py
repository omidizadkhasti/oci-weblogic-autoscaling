import io
import json
import logging
import oci

from fdk import response


def execute_command(signer, resourceId, commandText, TargertInstanceOCID, commandDispName):
    client = oci.compute_instance_agent.ComputeInstanceAgentClient(config={}, signer=signer)
    resp = ""
    try:
       source = oci.compute_instance_agent.models.InstanceAgentCommandSourceViaTextDetails(source_type='TEXT',text='sudo -u oracle  /u01/oracle/product/fmw/oracle_common/common/bin/wlst.sh /u01/oracle/config/scripts/destroyWLManagedServer.py '+resourceId)
       output = oci.compute_instance_agent.models.InstanceAgentCommandOutputViaTextDetails(output_type='TEXT')
       content = oci.compute_instance_agent.models.InstanceAgentCommandContent(output=output,source=source)
       targetInstance = oci.compute_instance_agent.models.InstanceAgentCommandTarget(instance_id="ocid1.instance.oc1.ap-melbourne-1.anwwkljrxoesbjicmdp4yw2kneq5s57ghtf5btln2duprkz6vetwgvzxa2rq")
       commandDetails=oci.compute_instance_agent.models.CreateInstanceAgentCommandDetails(compartment_id=signer.compartment_id, execution_time_out_in_seconds=417, target=targetInstance, content=content, display_name='wl-autoscaling-command')
       resp = client.create_instance_agent_command(create_instance_agent_command_details=commandDetails)
       logging.getLogger().info('Response: '+ str(resp)) 
    except Exception as ex:
       logging.getLogger().info('error : ' + str(ex))

    return resp.data

def handler(ctx, data: io.BytesIO=None):
    resourceId = ""
    resp = ""
    try:
        cfg = ctx.Config()
        commandText = cfg["command_text"]
        TargertInstanceOCID = cfg["target_instance_OCID"]
        commandDispName = cfg["command_display_name"]
        body = json.loads(data.getvalue())
        resourceId = body["data"]["resourceId"]
        signer = oci.auth.signers.get_resource_principals_signer()
        # Initialize service client with default config file
        logging.getLogger().info('Compartment: '+str(signer.compartment_id))
        resp = execute_command(signer, resourceId, commandText, TargertInstanceOCID, commandDispName)
    except (Exception, ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))

    return response.Response(
        ctx, response_data=resp,
        headers={"Content-Type": "application/json"}
    )
