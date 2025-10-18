import json
from datetime import datetime, timedelta
import random

# Sample incident templates
INCIDENT_TEMPLATES = [
    {
        "title": "Database Connection Pool Exhausted",
        "description": "Users reporting 500 errors on checkout page. Error logs show: 'HikariCP - Connection is not available, request timed out after 30000ms'. Connection pool size currently at 20. Peak traffic time.",
        "severity": "P1",
        "incident_type": "database",
        "error_messages": "java.sql.SQLTransientConnectionException: HikariCP - Connection is not available\nCaused by: java.sql.SQLException: Timeout after 30000ms",
        "resolution_steps": "1. Increased HikariCP maximum pool size from 20 to 50 in application.properties\n2. Increased minimum idle connections from 10 to 25\n3. Added connection leak detection with 60s threshold\n4. Deployed config change via rolling update\n5. Monitored connection pool metrics - utilization dropped from 100% to 45%",
        "root_cause": "Traffic spike exceeded connection pool capacity during flash sale event",
        "resolution_time_minutes": 12,
        "technical_terms": ["HikariCP", "connection pool", "SQLTransientConnectionException", "timeout"],
        "affected_systems": ["checkout-service", "postgres-primary"],
        "tags": ["database", "performance", "connection-pool"]
    },
    {
        "title": "Memory Leak in User Service causing OOM",
        "description": "User service pods crashing every 2-3 hours with OutOfMemoryError. Heap dumps show excessive String objects in memory. GC logs indicate heap exhaustion before crash.",
        "severity": "P0",
        "incident_type": "application",
        "error_messages": "java.lang.OutOfMemoryError: Java heap space\nat java.util.HashMap.resize(HashMap.java:704)\nHeap dump file created [2789453312 bytes]",
        "resolution_steps": "1. Analyzed heap dump with Eclipse MAT - found 850MB of String objects\n2. Identified bug in user cache implementation - not clearing expired entries\n3. Applied fix: Added scheduled task to evict expired cache entries every 5 minutes\n4. Increased heap size from 2GB to 4GB as temporary measure\n5. Deployed fix to production\n6. Monitored heap usage - now stable at 1.2GB",
        "root_cause": "Cache implementation bug causing memory leak - expired user sessions never evicted from memory",
        "resolution_time_minutes": 85,
        "technical_terms": ["OutOfMemoryError", "heap dump", "memory leak", "garbage collection", "cache eviction"],
        "affected_systems": ["user-service", "kubernetes-cluster"],
        "tags": ["memory", "java", "production-outage"]
    },
    {
        "title": "Redis Cluster Split-Brain causing data inconsistency",
        "description": "Multiple Redis master nodes detected. Writes going to different masters causing data conflicts. Client applications reporting inconsistent user session data.",
        "severity": "P0",
        "incident_type": "database",
        "error_messages": "READONLY You can't write against a read only replica.\nCluster state: fail\nNot all cluster slots are covered",
        "resolution_steps": "1. Checked Redis Sentinel logs - network partition 15 minutes ago\n2. Identified split-brain: 2 masters for same shard\n3. Stopped all writes by enabling maintenance mode\n4. Manually failed over to correct master using CLUSTER FAILOVER\n5. Resync'd replica nodes\n6. Verified cluster topology with CLUSTER NODES\n7. Re-enabled writes after validation",
        "root_cause": "Network partition between availability zones caused Redis Sentinel to elect new master while old master still responsive",
        "resolution_time_minutes": 45,
        "technical_terms": ["Redis", "split-brain", "cluster failover", "sentinel", "network partition"],
        "affected_systems": ["redis-cluster", "session-store"],
        "tags": ["redis", "distributed-systems", "data-consistency"]
    },
    {
        "title": "Kubernetes Node Not Ready - Disk Pressure",
        "description": "Worker node showing NotReady status. Pods being evicted. kubectl describe node shows 'DiskPressure' condition. Root filesystem at 98% usage.",
        "severity": "P1",
        "incident_type": "infrastructure",
        "error_messages": "Node condition DiskPressure is now: True\nEvicting pod: user-service-7d4f8c9b5-9k2mp\nFailed to garbage collect: failed to evict pods",
        "resolution_steps": "1. SSH'd to problematic node\n2. Found /var/log/containers filling disk - 45GB of old logs\n3. Cleaned up old container logs: find /var/log/containers -type f -mtime +7 -delete\n4. Adjusted log rotation policy in /etc/logrotate.d/containers\n5. Node returned to Ready state automatically\n6. Implemented DaemonSet for automated log cleanup\n7. Added disk usage monitoring alerts at 80%",
        "root_cause": "Container logs not being rotated properly, filling node's root filesystem",
        "resolution_time_minutes": 25,
        "technical_terms": ["Kubernetes", "DiskPressure", "pod eviction", "log rotation", "node NotReady"],
        "affected_systems": ["k8s-worker-node-03", "logging-system"],
        "tags": ["kubernetes", "disk-space", "node-management"]
    },
    {
        "title": "API Gateway 504 Timeout - Upstream Service Slow",
        "description": "Users reporting API timeouts. API Gateway returning 504 Gateway Timeout errors. Backend services appear healthy but response times elevated from 200ms to 8000ms.",
        "severity": "P1",
        "incident_type": "application",
        "error_messages": "upstream timed out (110: Connection timed out) while reading response header from upstream\n504 Gateway Time-out",
        "resolution_steps": "1. Checked API Gateway logs - timeouts after 30s\n2. Investigated backend service - found N+1 database query problem\n3. Analyzed slow query log - missing index on orders.user_id\n4. Created index: CREATE INDEX idx_orders_user_id ON orders(user_id)\n5. Query time dropped from 7.2s to 45ms\n6. Added database query performance monitoring",
        "root_cause": "Recent code deployment introduced N+1 query pattern without proper database indexing",
        "resolution_time_minutes": 38,
        "technical_terms": ["504 timeout", "N+1 query", "database index", "upstream timeout", "slow query"],
        "affected_systems": ["api-gateway", "order-service", "postgres-db"],
        "tags": ["performance", "database", "indexing"]
    }
]

def generate_incidents(count=20):
    """Generate sample incident data"""
    incidents = []
    base_date = datetime.now() - timedelta(days=180)
    
    for i in range(count):
        template = random.choice(INCIDENT_TEMPLATES)
        
        # Add some variation
        created_at = base_date + timedelta(days=random.randint(0, 180), hours=random.randint(0, 23))
        resolved_at = created_at + timedelta(minutes=template['resolution_time_minutes'])
        
        incident = {
            "incident_id": f"INC-{str(10000 + i).zfill(5)}",
            "title": template['title'],
            "description": template['description'],
            "severity": template['severity'],
            "incident_type": template['incident_type'],
            "status": "resolved",
            "affected_systems": template['affected_systems'],
            "error_messages": template['error_messages'],
            "technical_terms": template['technical_terms'],
            "resolution_steps": template['resolution_steps'],
            "resolution_time_minutes": template['resolution_time_minutes'],
            "root_cause": template['root_cause'],
            "source_type": "incident",
            "created_at": created_at.isoformat(),
            "resolved_at": resolved_at.isoformat(),
            "updated_at": resolved_at.isoformat(),
            "tags": template['tags']
        }
        
        incidents.append(incident)
    
    return incidents

if __name__ == "__main__":
    incidents = generate_incidents(20)
    
    # Save to file
    with open('sample_incidents.json', 'w') as f:
        json.dump(incidents, f, indent=2)
    
    print(f"✅ Generated {len(incidents)} sample incidents")
    print("Saved to: sample_incidents.json")