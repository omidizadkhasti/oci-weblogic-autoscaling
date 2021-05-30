import io
import json
import logging
import oci

from fdk import response

def list_instances(signer):
    client = oci.core.ComputeClient(config={}, signer=signer)
    # OCI API to manage Compute resources such as compute instances, block storage volumes, etc.
    try:
        # Returns a list of all instances in the current compartment
        inst = client.list_instances(signer.compartment_id)
        # Create a list that holds a list of the instances id and name next to each other
        inst = [[i.id, i.display_name] for i in inst.data]
    except Exception as ex:
        print("ERROR: accessing Compute instances failed", ex, flush=True)
        raise
    resp = { "instances": inst }
    return resp

def execute_command(signer, resourceId, commandText, targetInstanceOCID, commandDispName):
    client = oci.compute_instance_agent.ComputeInstanceAgentClient(config={}, signer=signer)
    resp = ""
    try:
       source = oci.compute_instance_agent.models.InstanceAgentCommandSourceViaTextDetails(source_type='TEXT',text=commandText+' '+resourceId)
       output = oci.compute_instance_agent.models.InstanceAgentCommandOutputViaTextDetails(output_type='TEXT')
       content = oci.compute_instance_agent.models.InstanceAgentCommandContent(output=output,source=source)
       targetInstance = oci.compute_instance_agent.models.InstanceAgentCommandTarget(instance_id=targetInstanceOCID)
       commandDetails=oci.compute_instance_agent.models.CreateInstanceAgentCommandDetails(compartment_id=signer.compartment_id, execution_time_out_in_seconds=417, target=targetInstance, content=content, display_name=commandDispName)
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
        targetInstanceOCID = cfg["target_instance_OCID"]
        commandDispName = cfg["command_display_name"]
        body = json.loads(data.getvalue())
        resourceId = body["data"]["resourceId"]
        signer = oci.auth.signers.get_resource_principals_signer()
        # Initialize service client with default config file
        logging.getLogger().info('Compartment: '+str(signer.compartment_id))
        resp = execute_command(signer, resourceId, commandText, targetInstanceOCID, commandDispName)
    except (Exception, ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))

    return response.Response(
        ctx, response_data=resp,
        headers={"Content-Type": "application/json"}
    )
