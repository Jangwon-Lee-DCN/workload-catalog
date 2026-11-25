"""Exercise B2 with a temporary archive and a local SSH transport substitute."""
from pathlib import Path
import os,subprocess,tempfile,tarfile
R=Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory(prefix='ims-aisrc-transfer-') as temporary:
 root=Path(temporary);source=root/'input/voice-studio-platform/private/aisrc';source.mkdir(parents=True)
 for name in ['image.tar','machine-id','runtime/client.env','runtime/pretrained/model','runtime/DATA/license/license','runtime/DATA/security/security']:
  p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('test fixture')
 archive=root/'input.tar.gz'
 with tarfile.open(archive,'w:gz') as output:output.add(root/'input/voice-studio-platform',arcname='voice-studio-platform')
 key=root/'key';key.write_text('test key fixture')
 remote=root/'remote';(remote/'aisrc').mkdir(parents=True)
 bindir=root/'bin';bindir.mkdir()
 shim=bindir/'ssh';shim.write_text('''#!/usr/bin/env python3
import os,sys,subprocess
command=sys.argv[-1].replace('/var/lib/voice-private',os.environ['TEST_REMOTE']).replace('sudo ','')
raise SystemExit(subprocess.run(['bash','-c',command]).returncode)
''');shim.chmod(0o755)
 env=os.environ.copy();env.update({'PATH':str(bindir)+':'+env['PATH'],'TEST_REMOTE':str(remote)})
 command=['bash',str(R/'infra/capa-free5gc/gpu-services/inject-aisrc.sh'),'--archive',str(archive),'--ssh-key',str(key),'--gpu-ip','8.8.8.8']
 result=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 assert result.returncode==0,result.stderr
 assert 'AISRC_TRANSFER_READY' in result.stdout
 assert (remote/'aisrc/.ready').is_file()
 assert (remote/'aisrc/runtime/client.env').read_text()=='test fixture'
 assert not (remote/'.transfer-in-progress').exists()
 repeated=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 assert repeated.returncode!=0 and 'AISRC_TRANSFER_READY' not in repeated.stdout
 assert (remote/'aisrc/runtime/client.env').read_text()=='test fixture'
 # A missing required input must fail before any SSH transfer.
 (source/'machine-id').unlink()
 with tarfile.open(archive,'w:gz') as output:output.add(root/'input/voice-studio-platform',arcname='voice-studio-platform')
 missing=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 assert missing.returncode!=0 and 'AISRC_INPUT_READY' not in missing.stdout
 print('AISRC_TRANSFER_AND_ACTIVE_INPUT_PROTECTION_PASS')
