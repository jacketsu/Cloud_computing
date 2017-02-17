import boto.ec2
import time
import os

def ec2_launch_instance(ami, keyName, instanceType, securityGroup, region):
    conn = boto.ec2.connect_to_region('us-west-2')

    try:
        key=conn.get_all_key_pairs(keynames=[keyName])[0]
    except conn.ResponseError as ex:
        if ex.code == 'InvalidKeyPair.NotFound':
            print('Try to create keypair: %s' % keyName)
            key = conn.create_key_pair(keyName)
            key_dir = 'ssh'
            try:
                if not os.path.isdir(key_dir):
                    os.chmod(key_dir, 0o777)
                    os.mkdir(key_dir, 0o700)
                key.save(key_dir)
            except TypeError:
                pass
        else:
            raise

    try:
        group = conn.get_all_security_groups(groupnames=[securityGroup])[0]
    except conn.ResponseError as ex:
        if ex.code == 'InvalidGroup.NotFound':
            print('Try to create security group: %s' % securityGroup)
            group = conn.create_security_group(securityGroup, 'to be allowed SSH access')
        else:
            raise

    try:
        group.authorize('tcp', 22, 22, '0.0.0.0/0')
    except conn.ResponseError as ex:
        if ex.code == 'InvalidPermission.Duplicate':
            print('Security Group: %s already authorized' % securityGroup)
        else:
            raise

    reservation = conn.run_instances(
            ami,
            key_name=keyName,
            instance_type=instanceType,
            security_groups=[securityGroup])

    instance=reservation.instances[0]
    print('Waiting for the instance')
    while instance.update() != "running":
        time.sleep(5)
    print('IP: ', instance.ip_address)
    print('Region: ', instance.placement)
    print('ID: ', instance.id)

    return instance

if __name__ == '__main__':
    ec2_launch_instance('ami-f173cc91', 'goodLduck', 't2.midcro', 'ddfefense', 'us-west-2')

