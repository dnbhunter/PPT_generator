# DNB Presentation Generator - Performance & Scalability Guide

## Performance Architecture

### System Performance Targets

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| API Response Time | < 200ms (95th percentile) | Application Performance Monitoring |
| Presentation Generation | < 30 seconds | End-to-end timing |
| Document Processing | < 10 seconds | Processing pipeline metrics |
| Concurrent Users | 1,000+ simultaneous | Load testing |
| Throughput | 100 requests/second | Performance benchmarking |
| Availability | 99.9% uptime | Health monitoring |

### Performance Monitoring Stack

```python
# src/core/monitoring.py
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import structlog

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active database connections')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
GENERATION_DURATION = Histogram('presentation_generation_duration_seconds', 'Presentation generation time')

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        
    def track_request(self, func):
        """Decorator to track request performance"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"Request failed: {e}")
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_DURATION.observe(duration)
                REQUEST_COUNT.labels(
                    method=kwargs.get('method', 'unknown'),
                    endpoint=kwargs.get('endpoint', 'unknown'),
                    status=status
                ).inc()
                
        return wrapper
    
    def update_system_metrics(self):
        """Update system performance metrics"""
        # Memory usage
        memory = psutil.virtual_memory()
        MEMORY_USAGE.set(memory.used)
        
        # CPU usage
        cpu_percent = psutil.cpu_percent()
        CPU_USAGE.set(cpu_percent)
        
        # Log warnings for high resource usage
        if memory.percent > 80:
            logger.warning(f"High memory usage: {memory.percent}%")
        
        if cpu_percent > 80:
            logger.warning(f"High CPU usage: {cpu_percent}%")

performance_monitor = PerformanceMonitor()
```

## Caching Strategy

### Multi-Level Caching Architecture

```python
# src/core/cache.py
import redis
import json
from typing import Any, Optional, Dict
import hashlib
from functools import wraps
import pickle
import gzip

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.local_cache = {}  # In-memory cache for frequently accessed data
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0
        }
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with fallback to Redis"""
        try:
            # Check local cache first
            if key in self.local_cache:
                self.cache_stats["hits"] += 1
                return self.local_cache[key]
            
            # Check Redis cache
            compressed_data = await self.redis_client.get(key)
            if compressed_data:
                # Decompress and deserialize
                data = pickle.loads(gzip.decompress(compressed_data))
                # Store in local cache for faster access
                self.local_cache[key] = data
                self.cache_stats["hits"] += 1
                return data
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["errors"] += 1
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 3600,
        local_cache: bool = True
    ):
        """Set value in cache with compression"""
        try:
            # Serialize and compress
            serialized_data = pickle.dumps(value)
            compressed_data = gzip.compress(serialized_data)
            
            # Store in Redis
            await self.redis_client.setex(key, ttl, compressed_data)
            
            # Store in local cache if requested
            if local_cache and len(self.local_cache) < 1000:  # Limit local cache size
                self.local_cache[key] = value
                
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.cache_stats["errors"] += 1

def cache_result(
    prefix: str, 
    ttl: int = 3600,
    use_local_cache: bool = True
):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = cache_manager._generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(
                cache_key, 
                result, 
                ttl=ttl,
                local_cache=use_local_cache
            )
            
            return result
        return wrapper
    return decorator

# Usage examples
@cache_result("user_presentations", ttl=1800)
async def get_user_presentations(user_id: str) -> List[Presentation]:
    """Cached user presentations lookup"""
    return await presentation_repository.get_by_user_id(user_id)

@cache_result("document_content", ttl=7200)
async def get_processed_document(document_id: str) -> ProcessedDocument:
    """Cached document processing results"""
    return await document_processor.process(document_id)
```

### Database Optimization

```python
# src/core/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import asyncpg

class DatabaseManager:
    def __init__(self, database_url: str, pool_size: int = 20):
        # Connection pooling for better performance
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections every hour
            echo=False  # Set to True for query debugging
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    async def execute_optimized_query(
        self, 
        query: str, 
        params: Dict = None
    ) -> List[Dict]:
        """Execute query with performance optimizations"""
        async with self.engine.begin() as conn:
            # Use prepared statements for better performance
            result = await conn.execute(text(query), params or {})
            return [dict(row) for row in result.fetchall()]
    
    async def bulk_insert(self, table_name: str, data: List[Dict]):
        """Optimized bulk insert operation"""
        if not data:
            return
        
        # Use COPY for PostgreSQL bulk inserts
        async with self.engine.begin() as conn:
            await conn.execute(text(f"""
                INSERT INTO {table_name} 
                ({', '.join(data[0].keys())})
                VALUES 
                {', '.join(['(' + ', '.join([':' + k for k in row.keys()]) + ')' for row in data])}
            """), data)

# Optimized queries with proper indexing
OPTIMIZED_QUERIES = {
    "user_presentations": """
        SELECT p.*, d.filename, d.file_size
        FROM presentations p
        LEFT JOIN documents d ON p.source_document_id = d.id
        WHERE p.user_id = :user_id 
        AND p.deleted_at IS NULL
        ORDER BY p.created_at DESC
        LIMIT :limit OFFSET :offset
    """,
    
    "presentation_search": """
        SELECT p.*, ts_rank(to_tsvector('english', p.title || ' ' || p.description), query) AS rank
        FROM presentations p, 
             to_tsquery('english', :search_query) query
        WHERE p.user_id = :user_id 
        AND p.deleted_at IS NULL
        AND to_tsvector('english', p.title || ' ' || p.description) @@ query
        ORDER BY rank DESC, p.created_at DESC
    """
}
```

## Scalability Architecture

### Horizontal Scaling with Load Balancing

```yaml
# infrastructure/bicep/load-balancer.bicep
resource applicationGateway 'Microsoft.Network/applicationGateways@2021-08-01' = {
  name: 'ag-presentation-generator'
  location: location
  properties: {
    sku: {
      name: 'WAF_v2'
      tier: 'WAF_v2'
      capacity: 2
    }
    autoscaleConfiguration: {
      minCapacity: 2
      maxCapacity: 10
    }
    gatewayIPConfigurations: [
      {
        name: 'appGatewayIpConfig'
        properties: {
          subnet: {
            id: subnet.id
          }
        }
      }
    ]
    frontendIPConfigurations: [
      {
        name: 'appGatewayFrontendIP'
        properties: {
          publicIPAddress: {
            id: publicIP.id
          }
        }
      }
    ]
    frontendPorts: [
      {
        name: 'port_443'
        properties: {
          port: 443
        }
      }
    ]
    backendAddressPools: [
      {
        name: 'appServiceBackendPool'
        properties: {
          backendAddresses: [
            {
              fqdn: containerApp.properties.configuration.ingress.fqdn
            }
          ]
        }
      }
    ]
    httpListeners: [
      {
        name: 'httpsListener'
        properties: {
          frontendIPConfiguration: {
            id: resourceId('Microsoft.Network/applicationGateways/frontendIPConfigurations', 'ag-presentation-generator', 'appGatewayFrontendIP')
          }
          frontendPort: {
            id: resourceId('Microsoft.Network/applicationGateways/frontendPorts', 'ag-presentation-generator', 'port_443')
          }
          protocol: 'Https'
          sslCertificate: {
            id: resourceId('Microsoft.Network/applicationGateways/sslCertificates', 'ag-presentation-generator', 'appGatewaySslCert')
          }
        }
      }
    ]
    requestRoutingRules: [
      {
        name: 'defaultRule'
        properties: {
          ruleType: 'Basic'
          httpListener: {
            id: resourceId('Microsoft.Network/applicationGateways/httpListeners', 'ag-presentation-generator', 'httpsListener')
          }
          backendAddressPool: {
            id: resourceId('Microsoft.Network/applicationGateways/backendAddressPools', 'ag-presentation-generator', 'appServiceBackendPool')
          }
          backendHttpSettings: {
            id: resourceId('Microsoft.Network/applicationGateways/backendHttpSettingsCollection', 'ag-presentation-generator', 'appGatewayBackendHttpSettings')
          }
        }
      }
    ]
    webApplicationFirewallConfiguration: {
      enabled: true
      firewallMode: 'Prevention'
      ruleSetType: 'OWASP'
      ruleSetVersion: '3.2'
    }
  }
}
```

### Auto-Scaling Configuration

```yaml
# Container Apps auto-scaling
resource containerApp 'Microsoft.App/containerApps@2022-03-01' = {
  name: 'ca-presentation-generator'
  location: location
  properties: {
    managedEnvironmentId: containerEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
      }
      dapr: {
        enabled: false
      }
      secrets: [
        {
          name: 'database-connection-string'
          value: databaseConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          image: 'dnbacr.azurecr.io/presentation-generator:latest'
          name: 'presentation-generator'
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
          env: [
            {
              name: 'DATABASE_URL'
              secretRef: 'database-connection-string'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 2
        maxReplicas: 20
        rules: [
          {
            name: 'http-scaling-rule'
            http: {
              metadata: {
                concurrentRequests: '30'
              }
            }
          }
          {
            name: 'cpu-scaling-rule'
            custom: {
              type: 'cpu'
              metadata: {
                type: 'Utilization'
                value: '70'
              }
            }
          }
          {
            name: 'memory-scaling-rule'
            custom: {
              type: 'memory'
              metadata: {
                type: 'Utilization'
                value: '80'
              }
            }
          }
        ]
      }
    }
  }
}
```

## Asynchronous Processing

### Background Task Queue

```python
# src/core/tasks.py
import asyncio
from celery import Celery
from typing import Dict, Any
import structlog

logger = structlog.get_logger()

# Celery configuration for distributed task processing
celery_app = Celery(
    'presentation_generator',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['src.tasks.presentation_tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'src.tasks.presentation_tasks.generate_presentation': 'generation_queue',
        'src.tasks.presentation_tasks.process_document': 'processing_queue',
        'src.tasks.presentation_tasks.export_presentation': 'export_queue'
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000
)

class AsyncTaskManager:
    def __init__(self):
        self.active_tasks = {}
        self.task_stats = {
            "completed": 0,
            "failed": 0,
            "active": 0
        }
    
    async def submit_task(
        self, 
        task_name: str, 
        task_data: Dict[str, Any],
        priority: int = 5
    ) -> str:
        """Submit task to background queue"""
        try:
            # Submit task with priority and retry configuration
            task = celery_app.send_task(
                task_name,
                args=[task_data],
                priority=priority,
                retry=True,
                retry_policy={
                    'max_retries': 3,
                    'interval_start': 0,
                    'interval_step': 0.2,
                    'interval_max': 0.2,
                }
            )
            
            self.active_tasks[task.id] = {
                "task_name": task_name,
                "status": "pending",
                "submitted_at": time.time()
            }
            
            self.task_stats["active"] += 1
            
            logger.info(f"Task submitted: {task.id}")
            return task.id
            
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            raise
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status and result"""
        try:
            task = celery_app.AsyncResult(task_id)
            
            status_info = {
                "task_id": task_id,
                "status": task.status,
                "result": task.result if task.ready() else None,
                "traceback": task.traceback if task.failed() else None
            }
            
            # Update local task tracking
            if task_id in self.active_tasks:
                self.active_tasks[task_id]["status"] = task.status
                
                if task.ready():
                    self.task_stats["active"] -= 1
                    if task.successful():
                        self.task_stats["completed"] += 1
                    else:
                        self.task_stats["failed"] += 1
            
            return status_info
            
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return {"task_id": task_id, "status": "error", "error": str(e)}

task_manager = AsyncTaskManager()
```

### Presentation Generation Tasks

```python
# src/tasks/presentation_tasks.py
from celery import shared_task
import asyncio
from src.agents.orchestrator import MultiAgentOrchestrator
from src.models.schemas import PresentationRequest, GenerationStatus

@shared_task(bind=True, max_retries=3)
def generate_presentation(self, request_data: Dict[str, Any]):
    """Background task for presentation generation"""
    try:
        # Create orchestrator instance
        orchestrator = MultiAgentOrchestrator()
        
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'initialization', 'progress': 0}
        )
        
        # Run the async generation process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                orchestrator.generate_presentation_async(request_data)
            )
            
            return {
                'status': 'completed',
                'presentation_id': result.presentation_id,
                'generation_time': result.generation_time,
                'slide_count': result.slide_count
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Presentation generation failed: {e}")
        
        # Update failure state
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 100}
        )
        
        raise

@shared_task(bind=True, max_retries=2)
def process_document(self, document_data: Dict[str, Any]):
    """Background task for document processing"""
    try:
        from src.services.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'text_extraction', 'progress': 25}
        )
        
        # Process document
        result = asyncio.run(processor.process_document(document_data))
        
        return {
            'status': 'completed',
            'document_id': result.document_id,
            'word_count': result.word_count,
            'pii_detected': result.pii_detected
        }
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise

@shared_task(bind=True)
def export_presentation(self, export_data: Dict[str, Any]):
    """Background task for presentation export"""
    try:
        from src.services.export_service import ExportService
        
        export_service = ExportService()
        
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'file_generation', 'progress': 50}
        )
        
        # Export presentation
        result = asyncio.run(export_service.export_presentation(export_data))
        
        return {
            'status': 'completed',
            'export_id': result.export_id,
            'download_url': result.download_url,
            'file_size': result.file_size
        }
        
    except Exception as e:
        logger.error(f"Presentation export failed: {e}")
        raise
```

## Load Testing

### Performance Test Suite

```python
# tests/performance/load_tests.py
import asyncio
import aiohttp
import time
from typing import List, Dict
import statistics

class LoadTester:
    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url
        self.auth_token = auth_token
        self.results = []
    
    async def single_request(
        self, 
        session: aiohttp.ClientSession, 
        endpoint: str,
        method: str = "GET",
        data: Dict = None
    ) -> Dict:
        """Execute a single HTTP request and measure performance"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with session.request(
                method,
                f"{self.base_url}{endpoint}",
                json=data,
                headers=headers
            ) as response:
                response_data = await response.json()
                end_time = time.time()
                
                return {
                    "success": response.status < 400,
                    "status_code": response.status,
                    "response_time": end_time - start_time,
                    "endpoint": endpoint,
                    "method": method
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "response_time": end_time - start_time,
                "endpoint": endpoint,
                "method": method
            }
    
    async def concurrent_load_test(
        self,
        endpoint: str,
        concurrent_users: int,
        requests_per_user: int,
        method: str = "GET",
        data: Dict = None
    ) -> Dict:
        """Run concurrent load test"""
        
        async def user_session(user_id: int):
            """Simulate a single user's session"""
            connector = aiohttp.TCPConnector(limit=100)
            async with aiohttp.ClientSession(connector=connector) as session:
                user_results = []
                
                for i in range(requests_per_user):
                    result = await self.single_request(session, endpoint, method, data)
                    result["user_id"] = user_id
                    result["request_number"] = i + 1
                    user_results.append(result)
                    
                    # Small delay between requests
                    await asyncio.sleep(0.1)
                
                return user_results
        
        # Start load test
        start_time = time.time()
        
        # Create tasks for concurrent users
        tasks = [user_session(i) for i in range(concurrent_users)]
        
        # Execute all tasks concurrently
        user_results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        
        # Flatten results
        all_results = []
        for user_result in user_results:
            all_results.extend(user_result)
        
        # Calculate statistics
        response_times = [r["response_time"] for r in all_results if r["success"]]
        success_count = sum(1 for r in all_results if r["success"])
        
        return {
            "total_requests": len(all_results),
            "successful_requests": success_count,
            "failed_requests": len(all_results) - success_count,
            "success_rate": success_count / len(all_results) * 100,
            "total_duration": end_time - start_time,
            "requests_per_second": len(all_results) / (end_time - start_time),
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else 0,
            "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0
        }

# Load test scenarios
async def run_performance_tests():
    """Run comprehensive performance tests"""
    tester = LoadTester(
        base_url="https://api.presentations.dnb.no/api/v1",
        auth_token="your_test_token"
    )
    
    test_scenarios = [
        {
            "name": "Health Check Load Test",
            "endpoint": "/health",
            "concurrent_users": 100,
            "requests_per_user": 10,
            "method": "GET"
        },
        {
            "name": "List Presentations Load Test",
            "endpoint": "/presentations",
            "concurrent_users": 50,
            "requests_per_user": 5,
            "method": "GET"
        },
        {
            "name": "Presentation Generation Load Test",
            "endpoint": "/generate/presentation",
            "concurrent_users": 10,
            "requests_per_user": 2,
            "method": "POST",
            "data": {
                "source_document_id": "test_doc_123",
                "metadata": {
                    "title": "Load Test Presentation",
                    "template": "corporate"
                }
            }
        }
    ]
    
    results = {}
    
    for scenario in test_scenarios:
        print(f"Running {scenario['name']}...")
        
        result = await tester.concurrent_load_test(
            endpoint=scenario["endpoint"],
            concurrent_users=scenario["concurrent_users"],
            requests_per_user=scenario["requests_per_user"],
            method=scenario["method"],
            data=scenario.get("data")
        )
        
        results[scenario["name"]] = result
        
        print(f"Results for {scenario['name']}:")
        print(f"  Success Rate: {result['success_rate']:.2f}%")
        print(f"  Requests/sec: {result['requests_per_second']:.2f}")
        print(f"  Avg Response Time: {result['avg_response_time']:.3f}s")
        print(f"  P95 Response Time: {result['p95_response_time']:.3f}s")
        print()
    
    return results

if __name__ == "__main__":
    asyncio.run(run_performance_tests())
```

## Performance Optimization Strategies

### 1. Database Optimization

```sql
-- Optimized database indexes for performance
CREATE INDEX CONCURRENTLY idx_presentations_user_id_created_at 
ON presentations (user_id, created_at DESC) 
WHERE deleted_at IS NULL;

CREATE INDEX CONCURRENTLY idx_presentations_status_created_at 
ON presentations (status, created_at DESC) 
WHERE deleted_at IS NULL;

CREATE INDEX CONCURRENTLY idx_documents_user_id_type 
ON documents (user_id, document_type) 
WHERE deleted_at IS NULL;

-- Full-text search index for presentation content
CREATE INDEX CONCURRENTLY idx_presentations_search 
ON presentations USING GIN (to_tsvector('english', title || ' ' || description));

-- Partial indexes for active records only
CREATE INDEX CONCURRENTLY idx_active_presentations 
ON presentations (created_at DESC) 
WHERE deleted_at IS NULL AND status IN ('completed', 'pending');
```

### 2. API Response Optimization

```python
# src/api/optimizations.py
from fastapi import Response
import gzip
import json

class ResponseOptimizer:
    @staticmethod
    def compress_response(content: str, min_size: int = 1000) -> bytes:
        """Compress response content if it's large enough"""
        if len(content) > min_size:
            return gzip.compress(content.encode('utf-8'))
        return content.encode('utf-8')
    
    @staticmethod
    def add_cache_headers(response: Response, max_age: int = 300):
        """Add appropriate cache headers"""
        response.headers["Cache-Control"] = f"public, max-age={max_age}"
        response.headers["ETag"] = hashlib.md5(
            response.body if hasattr(response, 'body') else b""
        ).hexdigest()
    
    @staticmethod
    def optimize_json_response(data: Dict, response: Response) -> Dict:
        """Optimize JSON response structure"""
        # Remove null values to reduce payload size
        optimized_data = {k: v for k, v in data.items() if v is not None}
        
        # Add cache headers for static data
        if "metadata" in optimized_data:
            ResponseOptimizer.add_cache_headers(response, max_age=1800)
        
        return optimized_data

# Usage in API endpoints
@app.get("/api/v1/presentations/{presentation_id}")
async def get_presentation(
    presentation_id: str,
    response: Response,
    current_user: User = Depends(get_current_user)
):
    presentation = await presentation_service.get_by_id(presentation_id)
    
    # Optimize response
    optimized_data = ResponseOptimizer.optimize_json_response(
        presentation.dict(), 
        response
    )
    
    return {"success": True, "data": optimized_data}
```

### 3. Memory Management

```python
# src/core/memory_management.py
import gc
import psutil
import asyncio
from typing import Dict, Any

class MemoryManager:
    def __init__(self, max_memory_percent: float = 80.0):
        self.max_memory_percent = max_memory_percent
        self.cleanup_threshold = max_memory_percent * 0.9  # 90% of max
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        memory = psutil.virtual_memory()
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            "system_memory_percent": memory.percent,
            "system_memory_available": memory.available / (1024**3),  # GB
            "process_memory_rss": process_memory.rss / (1024**3),  # GB
            "process_memory_vms": process_memory.vms / (1024**3)   # GB
        }
    
    async def cleanup_if_needed(self):
        """Clean up memory if usage is too high"""
        memory_stats = self.get_memory_usage()
        
        if memory_stats["system_memory_percent"] > self.cleanup_threshold:
            logger.warning(
                f"High memory usage detected: {memory_stats['system_memory_percent']:.1f}%"
            )
            
            # Force garbage collection
            gc.collect()
            
            # Clear local caches
            if hasattr(cache_manager, 'local_cache'):
                cache_manager.local_cache.clear()
            
            # Log memory stats after cleanup
            new_memory_stats = self.get_memory_usage()
            logger.info(
                f"Memory cleanup completed. Usage: {new_memory_stats['system_memory_percent']:.1f}%"
            )

memory_manager = MemoryManager()

# Periodic memory cleanup task
async def periodic_memory_cleanup():
    """Background task for periodic memory cleanup"""
    while True:
        await memory_manager.cleanup_if_needed()
        await asyncio.sleep(60)  # Check every minute

# Start background task
asyncio.create_task(periodic_memory_cleanup())
```

## Monitoring and Alerting

### Performance Dashboard

```python
# src/monitoring/dashboard.py
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

monitoring_router = APIRouter()

@monitoring_router.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@monitoring_router.get("/performance/stats")
async def get_performance_stats():
    """Get detailed performance statistics"""
    return {
        "cache_stats": cache_manager.cache_stats,
        "task_stats": task_manager.task_stats,
        "memory_stats": memory_manager.get_memory_usage(),
        "database_stats": await get_database_stats(),
        "system_stats": {
            "cpu_usage": psutil.cpu_percent(),
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict()
        }
    }

async def get_database_stats() -> Dict[str, Any]:
    """Get database performance statistics"""
    async with database_manager.engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT 
                schemaname,
                tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                seq_scan,
                seq_tup_read,
                idx_scan,
                idx_tup_fetch
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
        """))
        
        return [dict(row) for row in result.fetchall()]
```

### Performance Alerts

```python
# src/monitoring/alerts.py
class PerformanceAlertManager:
    def __init__(self):
        self.alert_thresholds = {
            "response_time_p95": 1.0,  # seconds
            "error_rate": 5.0,         # percent
            "memory_usage": 85.0,      # percent
            "cpu_usage": 80.0,         # percent
            "queue_depth": 1000        # number of tasks
        }
        
    async def check_performance_thresholds(self):
        """Check if any performance thresholds are exceeded"""
        alerts = []
        
        # Check response times
        p95_response_time = REQUEST_DURATION.get_sample_value(0.95)
        if p95_response_time > self.alert_thresholds["response_time_p95"]:
            alerts.append({
                "type": "high_response_time",
                "severity": "warning",
                "value": p95_response_time,
                "threshold": self.alert_thresholds["response_time_p95"]
            })
        
        # Check error rate
        total_requests = sum(REQUEST_COUNT._value.values())
        error_requests = sum(
            count for ((method, endpoint, status), count) in REQUEST_COUNT._value.items()
            if status != "success"
        )
        error_rate = (error_requests / total_requests) * 100 if total_requests > 0 else 0
        
        if error_rate > self.alert_thresholds["error_rate"]:
            alerts.append({
                "type": "high_error_rate",
                "severity": "critical",
                "value": error_rate,
                "threshold": self.alert_thresholds["error_rate"]
            })
        
        # Check system resources
        memory_usage = psutil.virtual_memory().percent
        if memory_usage > self.alert_thresholds["memory_usage"]:
            alerts.append({
                "type": "high_memory_usage",
                "severity": "warning",
                "value": memory_usage,
                "threshold": self.alert_thresholds["memory_usage"]
            })
        
        # Send alerts if any
        for alert in alerts:
            await self.send_alert(alert)
        
        return alerts
    
    async def send_alert(self, alert: Dict[str, Any]):
        """Send alert notification"""
        logger.warning(
            f"Performance alert: {alert['type']}",
            severity=alert["severity"],
            value=alert["value"],
            threshold=alert["threshold"]
        )
        
        # In production, send to monitoring service
        # await monitoring_service.send_alert(alert)

alert_manager = PerformanceAlertManager()

# Background task for performance monitoring
async def performance_monitoring_task():
    """Background task for continuous performance monitoring"""
    while True:
        try:
            await alert_manager.check_performance_thresholds()
            await performance_monitor.update_system_metrics()
        except Exception as e:
            logger.error(f"Performance monitoring error: {e}")
        
        await asyncio.sleep(30)  # Check every 30 seconds

# Start monitoring task
asyncio.create_task(performance_monitoring_task())
```

This comprehensive performance and scalability guide ensures the DNB Presentation Generator can handle enterprise-scale workloads while maintaining optimal performance and reliability.
