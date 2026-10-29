"""Generates the 10 benchmark repositories (5 Python, 5 JS/TS) across Small, Medium, Large scales
along with ground-truth reference symbol tables and architecture topologies.
"""

import json
from pathlib import Path


def create_benchmarks():
    base_dir = Path(__file__).resolve().parent / "benchmarks"
    gt_dir = Path(__file__).resolve().parent / "ground_truth"
    base_dir.mkdir(parents=True, exist_ok=True)
    gt_dir.mkdir(parents=True, exist_ok=True)

    # 1. py_small_math
    p1 = base_dir / "py_small_math"
    p1.mkdir(parents=True, exist_ok=True)
    (p1 / "vector.py").write_text('''"""Vector operations module."""
import math

class Vector2D:
    """Represents a 2D vector."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self) -> "Vector2D":
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

def dot_product(v1: Vector2D, v2: Vector2D) -> float:
    return v1.x * v2.x + v1.y * v2.y
''')
    (p1 / "matrix.py").write_text('''"""Matrix transformation module."""
from vector import Vector2D, dot_product

class Matrix2x2:
    """Represents a 2x2 matrix."""
    def __init__(self, a: float, b: float, c: float, d: float):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def determinant(self) -> float:
        return self.a * self.d - self.b * self.c

    def transform(self, v: Vector2D) -> Vector2D:
        return Vector2D(self.a * v.x + self.b * v.y, self.c * v.x + self.d * v.y)
''')
    (p1 / "main.py").write_text('''"""Entrypoint for py_small_math."""
from vector import Vector2D, dot_product
from matrix import Matrix2x2

def run_math_pipeline(scale: float) -> float:
    v = Vector2D(3.0, 4.0)
    m = Matrix2x2(scale, 0, 0, scale)
    v_transformed = m.transform(v)
    return v_transformed.magnitude()
''')

    # 2. py_small_kv
    p2 = base_dir / "py_small_kv"
    p2.mkdir(parents=True, exist_ok=True)
    (p2 / "storage.py").write_text('''"""In-memory KV storage."""
import time

class StorageEngine:
    def __init__(self):
        self._data = {}
        self._expiry = {}

    def set(self, key: str, value: str, ttl: int = 0):
        self._data[key] = value
        if ttl > 0:
            self._expiry[key] = time.time() + ttl

    def get(self, key: str) -> str:
        if key in self._expiry and time.time() > self._expiry[key]:
            del self._data[key]
            del self._expiry[key]
            return None
        return self._data.get(key)
''')
    (p2 / "serializer.py").write_text('''"""Serialization helpers."""
import json

def serialize_payload(obj: dict) -> str:
    return json.dumps(obj)

def deserialize_payload(raw: str) -> dict:
    return json.loads(raw)
''')
    (p2 / "server.py").write_text('''"""KV Server Interface."""
from storage import StorageEngine
from serializer import serialize_payload, deserialize_payload

class KVServer:
    def __init__(self):
        self.engine = StorageEngine()

    def handle_request(self, command: str, key: str, value: str = None) -> str:
        if command == "SET":
            self.engine.set(key, value)
            return "OK"
        elif command == "GET":
            val = self.engine.get(key)
            return val or "NIL"
        return "ERR"
''')

    # 3. py_med_taskflow
    p3 = base_dir / "py_med_taskflow"
    p3.mkdir(parents=True, exist_ok=True)
    (p3 / "models.py").write_text('''"""Task models."""
from typing import List, Callable

class Task:
    def __init__(self, task_id: str, action: Callable, dependencies: List[str] = None):
        self.task_id = task_id
        self.action = action
        self.dependencies = dependencies or []
        self.completed = False
''')
    (p3 / "dag.py").write_text('''"""DAG topological scheduler."""
from models import Task
from typing import Dict, List

class TaskDAG:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def add_task(self, task: Task):
        self.tasks[task.task_id] = task

    def get_execution_order(self) -> List[str]:
        visited = set()
        order = []
        def dfs(t_id):
            if t_id in visited:
                return
            visited.add(t_id)
            for dep in self.tasks[t_id].dependencies:
                dfs(dep)
            order.append(t_id)
        for t_id in self.tasks:
            dfs(t_id)
        return order
''')
    (p3 / "executor.py").write_text('''"""Worker executor pool."""
from dag import TaskDAG

class TaskExecutor:
    def __init__(self, dag: TaskDAG):
        self.dag = dag

    def execute_all(self) -> int:
        order = self.dag.get_execution_order()
        count = 0
        for t_id in order:
            task = self.dag.tasks[t_id]
            task.action()
            task.completed = True
            count += 1
        return count
''')
    (p3 / "app.py").write_text('''"""Taskflow application runner."""
from models import Task
from dag import TaskDAG
from executor import TaskExecutor

def build_sample_pipeline() -> int:
    dag = TaskDAG()
    dag.add_task(Task("step1", lambda: print("1")))
    dag.add_task(Task("step2", lambda: print("2"), dependencies=["step1"]))
    executor = TaskExecutor(dag)
    return executor.execute_all()
''')

    # 4. py_med_apigateway
    p4 = base_dir / "py_med_apigateway"
    p4.mkdir(parents=True, exist_ok=True)
    (p4 / "auth.py").write_text('''"""Authentication and JWT validator."""
class AuthProvider:
    def __init__(self, secret: str):
        self.secret = secret

    def authenticate_token(self, token: str) -> bool:
        return token == f"token_{self.secret}"

    def generate_token(self, user_id: str) -> str:
        return f"token_{self.secret}"
''')
    (p4 / "rate_limiter.py").write_text('''"""Sliding window rate limiter."""
class RateLimiter:
    def __init__(self, max_requests: int):
        self.max_requests = max_requests
        self.counts = {}

    def is_allowed(self, client_ip: str) -> bool:
        count = self.counts.get(client_ip, 0)
        if count >= self.max_requests:
            return False
        self.counts[client_ip] = count + 1
        return True
''')
    (p4 / "router.py").write_text('''"""REST route dispatcher with decorators."""
from auth import AuthProvider
from rate_limiter import RateLimiter

class APIGateway:
    def __init__(self, secret: str, rate_limit: int = 100):
        self.auth = AuthProvider(secret)
        self.limiter = RateLimiter(rate_limit)

    def route_get(self, path: str, token: str, ip: str) -> str:
        if not self.limiter.is_allowed(ip):
            return "429 Too Many Requests"
        if not self.auth.authenticate_token(token):
            return "401 Unauthorized"
        return f"200 OK for {path}"

    def route_post(self, path: str, payload: dict, token: str) -> str:
        if not self.auth.authenticate_token(token):
            return "401 Unauthorized"
        return f"201 Created at {path}"
''')

    # 5. py_large_cms
    p5 = base_dir / "py_large_cms"
    p5.mkdir(parents=True, exist_ok=True)
    (p5 / "database.py").write_text('''"""Database ORM abstraction."""
class DatabaseConnection:
    def __init__(self, uri: str):
        self.uri = uri
        self.connected = False

    def connect(self) -> bool:
        self.connected = True
        return True

    def query(self, sql: str) -> list:
        return [{"id": 1, "query": sql}]
''')
    (p5 / "models.py").write_text('''"""Content models."""
from database import DatabaseConnection

class Post:
    def __init__(self, post_id: int, title: str, content: str):
        self.post_id = post_id
        self.title = title
        self.content = content

class Author:
    def __init__(self, author_id: int, name: str, email: str):
        self.author_id = author_id
        self.name = name
        self.email = email
''')
    (p5 / "views.py").write_text('''"""CMS views."""
from models import Post, Author
from database import DatabaseConnection

class CMSController:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def get_post_detail(self, post_id: int) -> dict:
        results = self.db.query(f"SELECT * FROM posts WHERE id={post_id}")
        return results[0] if results else {}

    def publish_post(self, title: str, content: str, author_id: int) -> int:
        self.db.query(f"INSERT INTO posts (title, content, author_id) VALUES ('{title}', '{content}', {author_id})")
        return 1
''')
    (p5 / "app.py").write_text('''"""Main CMS application."""
from database import DatabaseConnection
from views import CMSController

def create_cms_app(db_uri: str) -> CMSController:
    db = DatabaseConnection(db_uri)
    db.connect()
    return CMSController(db)
''')

    # 6. js_small_calculator
    p6 = base_dir / "js_small_calculator"
    p6.mkdir(parents=True, exist_ok=True)
    (p6 / "lexer.js").write_text('''// Lexer tokenizer
function tokenize(expr) {
    return expr.match(/\\d+|\\+|\\-|\\*|\\//g) || [];
}
module.exports = { tokenize };
''')
    (p6 / "evaluator.js").write_text('''// Expression evaluator
const { tokenize } = require("./lexer.js");

function evaluateExpression(expr) {
    const tokens = tokenize(expr);
    let result = parseFloat(tokens[0]);
    for (let i = 1; i < tokens.length; i += 2) {
        const op = tokens[i];
        const val = parseFloat(tokens[i + 1]);
        if (op === "+") result += val;
        if (op === "-") result -= val;
        if (op === "*") result *= val;
        if (op === "/") result /= val;
    }
    return result;
}
module.exports = { evaluateExpression };
''')

    # 7. js_small_eventemitter
    p7 = base_dir / "js_small_eventemitter"
    p7.mkdir(parents=True, exist_ok=True)
    (p7 / "events.js").write_text('''// PubSub event bus
class EventEmitter {
    constructor() {
        this.listeners = {};
    }
    on(event, handler) {
        if (!this.listeners[event]) this.listeners[event] = [];
        this.listeners[event].push(handler);
    }
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(fn => fn(data));
        }
    }
}
module.exports = { EventEmitter };
''')
    (p7 / "logger.js").write_text('''// Event logger
const { EventEmitter } = require("./events.js");

function attachLogger(emitter) {
    emitter.on("info", data => console.log("[INFO]", data));
    emitter.on("error", err => console.error("[ERROR]", err));
}
module.exports = { attachLogger };
''')

    # 8. js_med_router
    p8 = base_dir / "js_med_router"
    p8.mkdir(parents=True, exist_ok=True)
    (p8 / "middleware.js").write_text('''// Middleware pipeline
function createMiddlewareChain() {
    const stack = [];
    return {
        use(fn) { stack.push(fn); },
        run(req, res) { stack.forEach(fn => fn(req, res)); }
    };
}
module.exports = { createMiddlewareChain };
''')
    (p8 / "router.js").write_text('''// HTTP Router
const { createMiddlewareChain } = require("./middleware.js");

class Router {
    constructor() {
        this.routes = {};
        this.middleware = createMiddlewareChain();
    }
    get(path, handler) {
        this.routes[`GET:${path}`] = handler;
    }
    post(path, handler) {
        this.routes[`POST:${path}`] = handler;
    }
    dispatch(method, path, req, res) {
        this.middleware.run(req, res);
        const key = `${method.toUpperCase()}:${path}`;
        if (this.routes[key]) {
            return this.routes[key](req, res);
        }
        return "404 Not Found";
    }
}
module.exports = { Router };
''')

    # 9. ts_med_store
    p9 = base_dir / "ts_med_store"
    p9.mkdir(parents=True, exist_ok=True)
    (p9 / "types.ts").write_text('''// State store interfaces
export interface Action {
    type: string;
    payload?: any;
}
export interface State {
    [key: string]: any;
}
export type Reducer = (state: State, action: Action) => State;
''')
    (p9 / "store.ts").write_text('''// Central state store
import { Action, State, Reducer } from "./types.js";

export class Store {
    private state: State;
    private reducer: Reducer;

    constructor(reducer: Reducer, initialState: State = {}) {
        this.reducer = reducer;
        this.state = initialState;
    }

    public getState(): State {
        return this.state;
    }

    public dispatch(action: Action): void {
        this.state = this.reducer(this.state, action);
    }
}
''')

    # 10. ts_large_orchestrator
    p10 = base_dir / "ts_large_orchestrator"
    p10.mkdir(parents=True, exist_ok=True)
    (p10 / "registry.ts").write_text('''// Service registry
export interface ServiceNode {
    id: string;
    host: string;
    port: number;
    healthy: boolean;
}

export class ServiceRegistry {
    private nodes: Map<string, ServiceNode> = new Map();

    public register(node: ServiceNode): void {
        this.nodes.set(node.id, node);
    }

    public getHealthyNodes(): ServiceNode[] {
        return Array.from(this.nodes.values()).filter(n => n.healthy);
    }
}
''')
    (p10 / "loadbalancer.ts").write_text('''// Round robin load balancer
import { ServiceRegistry, ServiceNode } from "./registry.js";

export class LoadBalancer {
    private registry: ServiceRegistry;
    private cursor: number = 0;

    constructor(registry: ServiceRegistry) {
        this.registry = registry;
    }

    public getNextNode(): ServiceNode | null {
        const healthy = this.registry.getHealthyNodes();
        if (healthy.length === 0) return null;
        const node = healthy[this.cursor % healthy.length];
        this.cursor++;
        return node;
    }
}
''')
    (p10 / "app.ts").write_text('''// Orchestration app
import { ServiceRegistry } from "./registry.js";
import { LoadBalancer } from "./loadbalancer.js";

export function bootstrapCluster(): LoadBalancer {
    const reg = new ServiceRegistry();
    reg.register({ id: "srv-1", host: "10.0.0.1", port: 8080, healthy: true });
    reg.register({ id: "srv-2", host: "10.0.0.2", port: 8080, healthy: true });
    return new LoadBalancer(reg);
}
''')

    print("All 10 benchmark repositories successfully generated!")


if __name__ == "__main__":
    create_benchmarks()
