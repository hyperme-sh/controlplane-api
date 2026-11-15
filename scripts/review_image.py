"""Observe retained layers without running older API images."""
import importlib.util
import json
from pathlib import Path
import sys

spec=importlib.util.spec_from_file_location('inspect_image',Path(__file__).with_name('inspect-container.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

if __name__=='__main__':
    layers=Path(sys.argv[2]);result=module.unpack_image(sys.argv[1],layers,enforce_user=False)
    result['digest']=sys.argv[3]
    result['legal_paths']=sorted(str(p.relative_to(layers)) for p in layers.rglob('*') if p.is_file() and ('/usr/share/doc/' in '/'+str(p.relative_to(layers)) or '/usr/share/common-licenses/' in '/'+str(p.relative_to(layers))))
    result['source_bundle_present']=any(p.endswith('/sources/index.json') for p in result['legal_paths'])
    result['debian_source_bundle_present']=any(p.endswith('/debian-sources/index.json') for p in result['legal_paths'])
    result['publication_cleared']=False
    result['scope']='All retained layers, not a reconstructed final filesystem; secret scan is separate'
    print('HISTORICAL_IMAGE_REVIEW='+json.dumps(result,sort_keys=True))
