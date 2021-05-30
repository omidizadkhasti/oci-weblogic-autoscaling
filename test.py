import requests
import oci

def getInstanceMetaData():
    headers = {"Authorization":"Bearer Oracle"}
    r = requests.get("http://169.254.169.254/opc/v2/instance/", headers=headers)
    return r.json()

print(oci.__file__)
print(getInstanceMetaData()["id"])
signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
identity_client = oci.identity.IdentityClient(config={}, signer=signer)

