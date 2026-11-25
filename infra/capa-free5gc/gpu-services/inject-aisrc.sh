#!/usr/bin/env bash
# B2: run on the management-cluster host with management kubectl access.
set -euo pipefail
umask 077
ARCHIVE=${AISRC_ARCHIVE:-$HOME/voice-studio-platform-internal-20261030.tar.gz}
SSH_KEY=${GPU_SSH_KEY:-$HOME/mynephio2025.pem}
GPU_CLUSTER=${GPU_CLUSTER_NAME:-demo-gpu-a}
MANAGEMENT_NAMESPACE=${MANAGEMENT_NAMESPACE:-default}
MANAGEMENT_CONTEXT=${MANAGEMENT_CONTEXT:-management}
GPU_PUBLIC_IP=${GPU_PUBLIC_IP:-}
while (($#)); do
  case "$1" in
    --archive) ARCHIVE=$2; shift 2;;
    --ssh-key) SSH_KEY=$2; shift 2;;
    --cluster) GPU_CLUSTER=$2; shift 2;;
    --namespace) MANAGEMENT_NAMESPACE=$2; shift 2;;
    --context) MANAGEMENT_CONTEXT=$2; shift 2;;
    --gpu-ip) GPU_PUBLIC_IP=$2; shift 2;;
    *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2;;
  esac
done
for tool in tar ssh python3; do command -v "$tool" >/dev/null; done
test -s "$ARCHIVE"
test -s "$SSH_KEY"
if [[ -z "$GPU_PUBLIC_IP" ]]; then
  command -v kubectl >/dev/null
  GPU_PUBLIC_IP=$(kubectl --context "$MANAGEMENT_CONTEXT" -n "$MANAGEMENT_NAMESPACE" \
    get awsmachines.infrastructure.cluster.x-k8s.io \
    -l "cluster.x-k8s.io/cluster-name=$GPU_CLUSTER" -o json | python3 -c '
import ipaddress,json,sys
machines=json.load(sys.stdin)["items"]
assert len(machines)==1,"Expected one GPU AWSMachine"
ips=[a["address"] for a in machines[0].get("status",{}).get("addresses",[]) if a["type"]=="ExternalIP"]
assert len(ips)==1 and ipaddress.ip_address(ips[0]).is_global,"GPU public IP is not ready"
print(ips[0])')
fi
python3 - "$GPU_PUBLIC_IP" <<'PY'
import ipaddress,sys
assert ipaddress.ip_address(sys.argv[1]).is_global,'A GPU public IP is required'
PY
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
# Extract only the private subtree, validating each member in one archive pass.
python3 - "$ARCHIVE" "$work" <<'PYTHON'
import pathlib,shutil,sys,tarfile
prefix='voice-studio-platform/private/aisrc'
root=pathlib.Path(sys.argv[2])
with tarfile.open(sys.argv[1],'r|gz') as archive:
    found=False
    for member in archive:
        name=member.name.removeprefix('./')
        if name==prefix or name.startswith(prefix+'/'):
            path=pathlib.PurePosixPath(name)
            assert not path.is_absolute() and '..' not in path.parts,'Unsafe archive path'
            assert member.isdir() or member.isfile(),'Only regular AISRC files and directories are accepted'
            target=root.joinpath(*path.parts[2:])
            if member.isdir():
                target.mkdir(parents=True,exist_ok=True,mode=0o700)
            else:
                target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                with archive.extractfile(member) as source, target.open('wb') as output:
                    shutil.copyfileobj(source,output,16*1024*1024)
            found=True
    assert found,'AISRC subtree is absent'
PYTHON
for file in image.tar machine-id runtime/client.env; do test -s "$work/aisrc/$file"; done
for dir in runtime/pretrained runtime/DATA/license runtime/DATA/security; do test -d "$work/aisrc/$dir"; done
rm -f -- "$work/aisrc/.ready"
printf 'AISRC_INPUT_READY\n'
# A complete incoming directory is validated before publishing the ready marker.
ssh_args=(-i "$SSH_KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new "ubuntu@$GPU_PUBLIC_IP")
tar -C "$work" -cf - aisrc | ssh "${ssh_args[@]}" 'set -eu
sudo install -d -m 0700 /var/lib/voice-private
sudo mkdir /var/lib/voice-private/.transfer-in-progress
trap "sudo rmdir /var/lib/voice-private/.transfer-in-progress" EXIT
if sudo test -e /var/lib/voice-private/aisrc/.ready; then
  echo "AISRC inputs already installed; refusing to replace active inputs" >&2
  exit 1
fi
sudo install -d -m 0700 /var/lib/voice-private/incoming
sudo tar -xf - -C /var/lib/voice-private/incoming
for f in image.tar machine-id runtime/client.env; do sudo test -s "/var/lib/voice-private/incoming/aisrc/$f"; done
for d in runtime/pretrained runtime/DATA/license runtime/DATA/security; do sudo test -d "/var/lib/voice-private/incoming/aisrc/$d"; done
sudo cp -a /var/lib/voice-private/incoming/aisrc/. /var/lib/voice-private/aisrc/
sudo chmod 0700 /var/lib/voice-private/aisrc
sudo touch /var/lib/voice-private/aisrc/.ready
sudo rm -rf /var/lib/voice-private/incoming
printf "AISRC_TRANSFER_READY\n"'
