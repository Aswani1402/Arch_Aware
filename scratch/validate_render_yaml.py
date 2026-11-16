import yaml

with open('render.yaml', 'r') as f:
    data = yaml.safe_load(f)

services = data.get('services', [])
print(f"Total services in render.yaml: {len(services)}")
for s in services:
    name = s.get('name')
    stype = s.get('type')
    runtime = s.get('runtime')
    print(f"\nService: {name} (type: {stype}, runtime: {runtime})")
    print(f"  rootDir: {s.get('rootDir')}")
    print(f"  buildCommand: {s.get('buildCommand')}")
    print(f"  startCommand: {s.get('startCommand')}")
    if 'disk' in s:
        d = s['disk']
        print(f"  disk: {d.get('name')} mounted at {d.get('mountPath')} ({d.get('sizeGB')} GB)")
    env_vars = s.get('envVars', [])
    print("  envVars:")
    for ev in env_vars:
        k = ev.get('key')
        v = ev.get('value', '<generated or sync>')
        print(f"    - {k}: {v}")

