import urllib.request
import json
import time

def run():
    print("🚀 [End User] Opening Dashboard & Clicking 'Trigger Swarm'...")
    req = urllib.request.Request(
        'http://localhost:8000/api/swarm/run',
        data=json.dumps({'image_tag': 'nginx:1.14.2', 'deployment_name': 'test-app'}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    run_id = json.loads(res.read())['run_id']
    print(f"📦 [System] Swarm Run Triggered. ID: {run_id}")
    print("⏳ [End User] Watching Live Logs on Dashboard...")
    
    status = 'running'
    while status == 'running':
        time.sleep(5)
        status_res = urllib.request.urlopen(f'http://localhost:8000/api/swarm/status/{run_id}')
        data = json.loads(status_res.read())
        status = data['status']
        print(f"   [System] Current Status: {status.upper()}")
        
    if status == 'needs_approval':
        print(f"⚠️ [System] Conflict Escalated. Item added to Approval Queue.")
        print("🧑‍💻 [End User] Reviewing Escalation. Deciding to Approve...")
        
        approve_req = urllib.request.Request(
            'http://localhost:8000/api/swarm/approve',
            data=json.dumps({'run_id': run_id, 'decision': 'proceed'}).encode(),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(approve_req)
        print("✅ [End User] Clicked 'Approve & Proceed'.")
        
        time.sleep(2)
        status_res = urllib.request.urlopen(f'http://localhost:8000/api/swarm/status/{run_id}')
        data = json.loads(status_res.read())
        print(f"🎉 [System] Final Status: {data['status'].upper()} | Decision: {data['state'].get('final_decision')}")

if __name__ == '__main__':
    run()
